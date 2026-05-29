#!/usr/bin/env python3
"""
Simple script to create a Menu Message File from a Menu Command source member.
Based on the UTMNUMSGF REXX/400 command logic.
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from makei.ibm_job import IBMJob, save_joblog_json
from makei.utils import format_datetime


class MnuCmdToMsgf:
    """Create Message File from Menu Command source file"""

    job: IBMJob
    srcstmf: str
    obj: str
    lib: str
    text: str
    env_settings: Dict[str, str]
    joblog_path: Optional[str]
    output: str

    def __init__(self, srcstmf: str, obj: str, lib: str, text: str = '',
                 env_settings: Optional[Dict[str, str]] = None,
                 joblog_path: Optional[str] = None, output: str = ""
                 ) -> None:
        self.job = IBMJob()
        self.srcstmf = srcstmf
        self.obj = obj
        self.lib = lib
        self.text = text
        self.env_settings = env_settings if env_settings is not None else {}
        self.joblog_path = joblog_path
        self.output = output
        self.job.run_cl("CHGJOB LOG(4 00 *SECLVL)", log=False)

    def run(self):
        """Main execution method"""
        success = False
        self.setup_env()

        run_datetime = datetime.now()

        try:
            # Parse menu command file
            commands = self._parse_mnucmd_file()
            if not commands:
                print("No valid commands found in source file")

            # Create message file
            self._create_msgf(commands)
            success = True

        except Exception as e:
            print(f"Failed to create {self.obj}.MSGF")
            print(f"Error: {e}", file=sys.stderr)

        if self.joblog_path is not None:
            cmd = f"CRTMSGF MSGF({self.lib}/{self.obj}) TEXT('{self.text}')"
            save_joblog_json(
                cmd,
                format_datetime(run_datetime),
                self.job.job_id,
                self.obj + ".MSGF",
                self.srcstmf,
                self.output,
                not success,
                self.joblog_path,
                lambda x: True,
            )

        return success

    def setup_env(self):
        """Setup environment (library list, current library, etc.)"""
        if "curlib" in self.env_settings and self.env_settings["curlib"]:
            self.job.run_cl(f"CHGCURLIB CURLIB({self.env_settings['curlib']})", log=True)

        if "preUsrlibl" in self.env_settings and self.env_settings["preUsrlibl"]:
            for libl in reversed(self.env_settings["preUsrlibl"].split()):
                self.job.run_cl(f"ADDLIBLE LIB({libl}) POSITION(*FIRST)", ignore_errors=True, log=True)

        if "postUsrlibl" in self.env_settings and self.env_settings["postUsrlibl"]:
            for libl in self.env_settings["postUsrlibl"].split():
                self.job.run_cl(f"ADDLIBLE LIB({libl}) POSITION(*LAST)", ignore_errors=True, log=True)

        if "IBMiEnvCmd" in self.env_settings and self.env_settings["IBMiEnvCmd"]:
            for cmd in self.env_settings["IBMiEnvCmd"].split("\\n"):
                if "SETASPGRP" not in cmd.upper():
                    self.job.run_cl(cmd, log=True)

    def _parse_mnucmd_file(self):
        """Parse menu command source file and extract commands."""
        commands = {}

        with open(self.srcstmf, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if not lines:
            raise ValueError("Empty menu command file")

        # Parse first line: should be "MENUNAME,0" or "MENUNAME,1"
        first_line = lines[0].strip()
        match = re.match(r'(\w+),([01])', first_line)
        if not match:
            raise ValueError(f"Invalid first line format: {first_line}")

        # Parse remaining lines for commands
        i = 1
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            # Skips empty commands
            if len(line) < 5:
                i += 1
                continue

            seq = line[:4].strip()
            rest = line[4:].strip()
            cmd = rest

            if seq.isdigit() and cmd:
                commands[seq] = cmd
            i += 1
        return commands

    def _create_msgf(self, commands):
        """Create message file and add message descriptions."""
        print(f"Creating MSGF from MNUCMD [{Path(self.srcstmf).name}] in {self.lib}")

        self.job.run_cl(f"DLTMSGF MSGF({self.lib}/{self.obj})", ignore_errors=True, log=True)

        self.job.run_cl(f"CRTMSGF MSGF({self.lib}/{self.obj}) TEXT('{self.text}')",
                        ignore_errors=False, log=True)

        for seq, command in sorted(commands.items()):
            msg_id = f"USR{seq.zfill(4)}"
            escaped_cmd = command.replace("'", "''")
            self.job.run_cl(
                f"ADDMSGD MSGID({msg_id}) MSGF({self.lib}/{self.obj}) MSG('{escaped_cmd}')",
                ignore_errors=False, log=True)

        print(f"{self.obj}.MSGF was created successfully!\n")


def cli():
    """CLI entry point for mnucmd_to_msgf"""
    parser = argparse.ArgumentParser(prog='mnucmd_to_msgf')

    parser.add_argument(
        "-f",
        '--stream-file',
        help='Specifies the path name of the MNUCMD source file.',
        metavar='<srcstmf>',
        required=True
    )

    parser.add_argument(
        "-o",
        "--object",
        help='Enter the name of the message file object.',
        metavar='<object>',
        required=True
    )

    parser.add_argument(
        "-l",
        '--library',
        help='Enter the name of the library.',
        metavar='<library>',
        default="*CURLIB"
    )

    parser.add_argument(
        "-c",
        '--command',
        help='Command type',
        metavar='<cmd>',
        default='CRTMSGF',
    )

    parser.add_argument(
        "-p",
        '--parameters',
        help='Additional parameters (TEXT description).',
        metavar='<parms>',
        nargs='?'
    )

    parser.add_argument(
        "--save-joblog",
        help='Output the joblog to the specified json file.',
        metavar='<path to joblog json file>',
    )

    parser.add_argument(
        "--output",
        metavar='<output>',
    )

    args = parser.parse_args()
    srcstmf_absolute_path = str(Path(args.stream_file.strip()).resolve())
    env_settings = {}
    if "curlib" in os.environ:
        env_settings["curlib"] = sanitize_lib_envvar(os.environ["curlib"])
    if "preUsrlibl" in os.environ:
        env_settings["preUsrlibl"] = sanitize_lib_envvar(os.environ["preUsrlibl"])
    if "postUsrlibl" in os.environ:
        env_settings["postUsrlibl"] = sanitize_lib_envvar(os.environ["postUsrlibl"])
    if "IBMiEnvCmd" in os.environ:
        env_settings["IBMiEnvCmd"] = os.environ["IBMiEnvCmd"]

    text = ''
    if args.parameters:
        text_match = re.search(r"TEXT\('([^']*)'\)", args.parameters)
        if text_match:
            text = text_match.group(1)
    handle = MnuCmdToMsgf(
        srcstmf_absolute_path,
        args.object.strip(),
        args.library.strip(),
        text,
        env_settings,
        args.save_joblog,
        output=args.output if args.output else ""
    )

    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    success = handle.run()
    print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    sys.exit(0 if success else 1)


def sanitize_lib_envvar(lib_or_libl: str):
    """Remove escape characters from library names"""
    return lib_or_libl.replace("\\#", "#")


if __name__ == '__main__':
    cli()
