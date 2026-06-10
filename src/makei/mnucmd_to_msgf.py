#!/usr/bin/env python3
"""
Script to create a Menu Message File from a Menu Command source member.
"""

import sys
import re
from pathlib import Path
from makei.ibm_job import IBMJob, save_joblog_json
from datetime import datetime
from makei.crtfrmstmf import filter_joblogs
from makei.utils import format_datetime


class MnucmdToMsgf:
    """
    Class to handle conversion of Menu Command source files to Message Files.
    """

    def __init__(self, source_file, msgf_lib, msgf_name=None, text=None, joblog=None, outlog=None):
        """
        Initialize the converter.

        """
        self.source_file = source_file
        self.msgf_lib = msgf_lib
        self.msgf_name = msgf_name or self._derive_msgf_name()
        self.text = text or 'Menu message file'
        self.commands = {}
        self.job = IBMJob()
        self.job.run_cl("CHGJOB LOG(4 00 *SECLVL)", log=False)
        self.joblog = joblog
        self.outlog = outlog

    def _derive_msgf_name(self):
        """
        Derive message file name from source file.
        Strips QQ suffix if present.

        Returns:
            str: Derived message file name
        """
        base_name = Path(self.source_file).stem
        return base_name[:-2] if base_name.endswith('QQ') else base_name

    def parse_mnucmd_file(self):
        """
        Parse menu command source file and extract commands.

        Raises:
            ValueError: If file is empty or has invalid format
        """
        with open(self.source_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if not lines:
            raise ValueError("Empty menu command file")

        # Parse first line: should be "MENUNAME,0" or "MENUNAME,1"
        first_line = lines[0].strip()
        match = re.match(r'(\w+),([01])', first_line)  # eg : FOOQQ(any char or word) , 1(or 0)
        if not match:
            raise ValueError(f"Invalid first line format: {first_line}")

        i = 1
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            if len(line) < 5:
                i += 1
                continue

            seq = line[:4].strip()
            rest = line[4:].strip()
            cmd = rest

            # Validate sequence number
            if seq.isdigit() and cmd:
                self.commands[seq] = cmd
            i += 1

    def create_msgf(self):
        """
        Create message file and add message descriptions.

        Raises:
            RuntimeError: If message file creation fails
        """
        self.job.run_cl(
            f"DLTMSGF MSGF({self.msgf_lib}/{self.msgf_name})", ignore_errors=True, log=True)

        cmd_to_run = [f"CRTMSGF MSGF({self.msgf_lib}/{self.msgf_name}) TEXT('{self.text}')"]
        for seq, command in sorted(self.commands.items()):
            msg_id = f"USR{seq.zfill(4)}"
            escaped_cmd = command.replace("'", "''")
            cmd_to_run.append(f"ADDMSGD MSGID({msg_id}) MSGF({self.msgf_lib}/{self.msgf_name}) MSG('{escaped_cmd}')")

        for cmd in cmd_to_run:
            self.invoke_joblog(cmd)

        print(f"Menu message file {self.msgf_name} successfully created in {self.msgf_lib} library.")

    def convert(self):
        """
        Parse the source file and create the message file.

        Raises:
            ValueError: If no valid commands found in source file
        """
        self.parse_mnucmd_file()

        if not self.commands:
            raise ValueError("No valid commands found in source file")

        self.create_msgf()

    def invoke_joblog(self, cmd):
        failed = False
        try:
            self.job.run_cl(cmd, log=True)
        except Exception:
            failed = True
            raise
        finally:
            run_datetime = datetime.now()
            if self.joblog is not None:
                save_joblog_json(cmd, format_datetime(
                    run_datetime), self.job.job_id, self.msgf_name + ".MSGF", self.source_file, self.outlog or "",
                    failed, self.joblog, filter_joblogs)


def main():

    source_file = sys.argv[1]
    msgf_lib = sys.argv[2]
    msgf_name = sys.argv[3]
    text = sys.argv[4]
    jlog = sys.argv[5]
    outlog = sys.argv[6]
    try:
        converter = MnucmdToMsgf(source_file, msgf_lib, msgf_name, text, jlog, outlog)
        converter.convert()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
