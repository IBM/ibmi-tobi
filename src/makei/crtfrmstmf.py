#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
import argparse
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from makei.ibm_job import IBMJob, save_joblog_json
from makei.utils import format_datetime, objlib_to_path, validate_ccsid, make_include_dirs_absolute

COMMAND_MAP = {'CRTCMD': 'CMD',
               'CRTBNDCL': 'PGM',
               'CRTCBLPGM': 'PGM',
               'CRTCLMOD': 'MODULE',
               'CRTCLPGM': 'PGM',
               'CRTDSPF': 'FILE',
               'CRTPRTF': 'FILE',
               'CRTLF': 'FILE',
               'CRTPF': 'FILE',
               'CRTMNU': 'MENU',
               'CRTPNLGRP': 'PNLGRP',
               'CRTQMQRY': 'QMQRY',
               'CRTSRVPGM': 'SRVPGM',
               'CRTWSCST': 'WSCST',
               'CRTRPGPGM': 'PGM',
               'CRTSQLRPG': 'PGM'}


class CrtFrmStmf():
    """create from stream file
    """
    # pylint: disable=too-many-instance-attributes

    job: IBMJob
    setup_job: IBMJob
    srcstmf: str
    obj: str
    lib: str
    cmd: str
    rcdlen: int
    parameters: Optional[str]
    env_settings: Dict[str, str]
    ccsid_c: str
    joblog_path: Optional[str]
    back_up_obj_list: List[Tuple[str, str, str]]  # List of (obj, lib, obj_type) tuples
    obj_type: str
    precmd: str
    postcmd: str

    def __init__(self, srcstmf: str, obj: str, lib: str, cmd: str, rcdlen: int, tgt_ccsid: Optional[str] = None,
                 parameters: Optional[str] = None, env_settings: Optional[Dict[str, str]] = None,
                 joblog_path: Optional[str] = None, tmp_lib="QTEMP", tmp_src="QSOURCE", precmd="",
                 postcmd="", output="") -> None:
        # pylint: disable=too-many-arguments
        self.job = IBMJob()
        self.setup_job = IBMJob()
        self.srcstmf = srcstmf
        self.obj = obj
        self.lib = lib
        self.cmd = cmd
        self.rcdlen = rcdlen
        self.parameters = parameters
        self.env_settings = env_settings if env_settings is not None else {}
        self.joblog_path = joblog_path
        self.job.run_cl("CHGJOB LOG(4 00 *SECLVL)", log=False)
        self.tmp_lib = tmp_lib
        self.tmp_src = tmp_src
        self.obj_type = COMMAND_MAP[self.cmd]
        self.precmd = precmd
        self.postcmd = postcmd
        self.output = output

        if tgt_ccsid is None or not validate_ccsid(tgt_ccsid):
            ccsid = retrieve_ccsid(srcstmf)
            if ccsid in ["1208", "819"]:
                self.ccsid_c = '*JOB'
            else:
                self.ccsid_c = str(ccsid)
        else:
            self.ccsid_c = tgt_ccsid

        if check_object_exists(self.obj, self.lib, self.obj_type):
            if self.cmd == "CRTPF":
                # For physical files, delete all its logical file dependencies
                self.back_up_obj_list = get_physical_dependencies(self.obj, self.lib, True, self.setup_job)
            else:
                self.back_up_obj_list = [(self.obj, self.lib, self.obj_type)]
        else:
            self.back_up_obj_list = []
        # Need project path for include resolution
        # prepend project path to every directory in INCDIR in compile parameters
        if (joblog_path and parameters):
            parameters = make_include_dirs_absolute(joblog_path, parameters)
        self.parameters = parameters

    def run(self):
        success = False
        self.setup_env()

        run_datetime = datetime.now()

        # Run the pre_cmd
        if self.precmd:
            self.job.run_cl(self.precmd, False, True)

        # Delete the temp source file
        self.job.run_cl(f'DLTF FILE({self.tmp_lib}/{self.tmp_src})', True)
        # Create the temp source file
        self.job.run_cl(
            f'CRTSRCPF FILE({self.tmp_lib}/{self.tmp_src}) RCDLEN({self.rcdlen}) MBR({self.obj}) CCSID({self.ccsid_c})')
        # Copy the source stream file to the temp source file
        self.job.run_cl(
            f'CPYFRMSTMF FROMSTMF("{self.srcstmf}") '
            f'TOMBR("/QSYS.LIB/{self.tmp_lib}.LIB/{self.tmp_src}.FILE/{self.obj}.MBR") MBROPT(*REPLACE)')

        self._backup_and_delete_objs()

        cmd = f"{self.cmd} {self.obj_type}({self.lib}/{self.obj}) " \
              f"SRCFILE({self.tmp_lib}/{self.tmp_src}) SRCMBR({self.obj})"
        if self.parameters is not None:
            cmd = cmd + ' ' + self.parameters
        try:
            self.job.run_cl(cmd, False, True)
            success = True

            # Run the post_cmd
            if self.postcmd:
                self.job.run_cl(self.postcmd, False, True)
        # pylint: disable=broad-except
        except Exception:
            print(f"Build not successful for {self.lib}/{self.obj}")
            if len(self.back_up_obj_list) > 0:
                self._restore_objs()

            # Process the event file
        if "*EVENTF" in cmd or "*SRCDBG" in cmd or "*LSTDBG" in cmd:
            if self.lib == "*CURLIB":
                self.lib = self._retrieve_current_library()
            if self.lib == "*NONE":
                self.lib = "*QGPL"
            self._update_event_file('37')

        if self.joblog_path is not None:
            save_joblog_json(cmd, format_datetime(
                run_datetime), self.job.job_id, self.obj + "." + self.obj_type, self.srcstmf, self.output,
                  not success, self.joblog_path, filter_joblogs)
        return success

    def setup_env(self):
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
                self.job.run_cl(cmd, log=True)

    def _retrieve_current_library(self):
        records, _ = self.job.run_sql(
            "SELECT SYSTEM_SCHEMA_NAME AS LIBRARY FROM QSYS2.LIBRARY_LIST_INFO WHERE TYPE='CURRENT'")
        row = records[0]
        if row:
            return row[0]
        return "*NONE"

    def _update_event_file(self, ccsid):
        self.setup_job.run_sql(
            f"CREATE OR REPLACE ALIAS {self.tmp_lib}.{self.obj} FOR {self.lib}.EVFEVENT ({self.obj});")
        results = self.setup_job.run_sql(" ".join(["SELECT",
                                                   f"CAST(EVFEVENT AS VARCHAR(300) CCSID {ccsid}) AS FULL",
                                                   f"FROM {self.tmp_lib}.{self.obj}",
                                                   f"WHERE Cast(evfevent As Varchar(300) Ccsid {ccsid})",
                                                   f"LIKE 'FILEID%{self.tmp_lib}/{self.tmp_src}({self.obj})%'",
                                                   ]))[0]
        if results:
            parts = results[0][0].split()
        else:
            return
        self.setup_job.run_sql(" ".join([f"Update {self.tmp_lib}.{self.obj}",
                                         "Set evfevent =",
                                         "(",
                                         f"SELECT Cast(evfevent As Varchar(24) Ccsid {ccsid})",
                                         f"CONCAT '{len(self.srcstmf):03} {self.srcstmf} {parts[-2]} {parts[-1]}'",
                                         f"FROM {self.tmp_lib}.{self.obj}",
                                         f"WHERE Cast(evfevent As Varchar(300) Ccsid {ccsid})",
                                         f"LIKE 'FILEID%{self.tmp_lib}/{self.tmp_src}({self.obj})%'",
                                         "FETCH First 1 Row Only)",
                                         f"WHERE Cast(evfevent As Varchar(300) Ccsid {ccsid})",
                                         f"LIKE 'FILEID%{self.tmp_lib}/{self.tmp_src}({self.obj})%'"]))

        self.setup_job.run_sql(f"DROP ALIAS {self.tmp_lib}.{self.obj}")

    def _backup_and_delete_objs(self):
        obj_list = self.back_up_obj_list
        if not len(obj_list) > 0:
            return

        print(f"Backing up {len(obj_list)} object(s)...")

        _, lib_list, _ = list(zip(*obj_list))
        obj_list_by_lib = {lib: [(obj_tuple[0], obj_tuple[2]) for obj_tuple in obj_list if lib == obj_tuple[1]] for lib
                           in set(lib_list)}

        for lib, obj_tuples in obj_list_by_lib.items():
            obj_name_list, obj_type_list = list(zip(*obj_tuples))
            self.setup_job.run_cl(f"CRTSAVF FILE({self.tmp_lib}/{lib})")
            self.setup_job.run_cl(
                f"SAVOBJ OBJ({' '.join(set(obj_name_list))}) LIB({self.lib}) DEV(*SAVF)"
                f" OBJTYPE({' '.join(map(lambda obj_type: f'*{obj_type}', set(obj_type_list)))})"
                f" SAVF({self.tmp_lib}/{lib}) SPLFDTA(*ALL) ACCPTH(*YES) QDTA(*DTAQ)")

        for obj_tuple in obj_list:
            self.setup_job.run_cl(
                f"DLTOBJ OBJ({obj_tuple[1]}/{obj_tuple[0]}) OBJTYPE(*{obj_tuple[2]})")

    def _restore_objs(self):
        obj_list = self.back_up_obj_list
        if not len(obj_list) > 0:
            return
        print(f"Restoring {len(obj_list)} object(s)...")

        _, lib_list, _ = list(zip(*obj_list))
        obj_list_by_lib = {lib: [(obj_tuple[0], obj_tuple[2]) for obj_tuple in obj_list if lib == obj_tuple[1]] for lib
                           in set(lib_list)}

        for lib, obj_tuples in obj_list_by_lib.items():
            obj_name_list, obj_type_list = list(zip(*obj_tuples))
            self.setup_job.run_cl(
                f"RSTOBJ OBJ({' '.join(set(obj_name_list))}) SAVLIB({self.lib}) DEV(*SAVF)"
                f" OBJTYPE({' '.join(map(lambda obj_type: f'*{obj_type}', set(obj_type_list)))})"
                f" SAVF({self.tmp_lib}/{lib})")
        print("done.")


def cli():
    """
    crtfrmstmf program cli entry
    """
    parser = argparse.ArgumentParser(prog='crtfrmstmf')

    parser.add_argument(
        "-f",
        '--stream-file',
        help='Specifies the path name of the stream file containing the source code to be compiled.',
        metavar='<srcstmf>',
        required=True
    )

    parser.add_argument(
        "-o",
        "--object",
        help='Enter the name of the object.',
        metavar='<object>',
        required=True
    )

    parser.add_argument(
        "-l",
        '--library',
        help='Enter the name of the library. If no library is specified, '
             'the created object is stored in the current library.',
        metavar='<library>',
        default="*CURLIB"
    )

    parser.add_argument(
        "-c",
        '--command',
        help='Specifies the compile command used to create the object.',
        metavar='<cmd>',
        required=True,
        choices=COMMAND_MAP.keys(),

    )

    parser.add_argument(
        "-r",
        '--rcdlen',
        help='Specifies the record length for the temporary source physical file.',
        metavar='<rcdlen>',
        default=32000

    )

    parser.add_argument(
        "-p",
        '--parameters',
        help='Specifies the parameters added to the compile command.',
        metavar='<parms>',
        nargs='?'
    )

    parser.add_argument(
        "--save-joblog",
        help='Output the joblog to the specified json file.',
        metavar='<path to joblog json file>',
    )
    parser.add_argument(
        "--ccsid",
        help='The CCSID of the source code.',
        metavar='<ccsid>',
    )
    parser.add_argument(
        "--precmd",
        metavar='<precmd>',
    )
    parser.add_argument(
        "--postcmd",
        metavar='<postcmd>',
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

    handle = CrtFrmStmf(srcstmf_absolute_path, args.object.strip(),
                        args.library.strip(), args.command.strip(), args.rcdlen, args.ccsid, args.parameters,
                        env_settings, args.save_joblog, precmd=args.precmd, postcmd=args.postcmd, output=args.output)

    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    success = handle.run()
    print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    sys.exit(0 if success else 1)


# Helper functions


def _get_attr(srcstmf: str):
    stream = os.popen(f'/QOpenSys/usr/bin/attr {srcstmf}')
    output = stream.read().strip()
    attrs = {}
    for attr in output.split("\n"):
        [key, value] = attr.split("=")
        attrs[key] = value
    return attrs


# Library names that include the hash symbol need to be
# escaped otherwise make will treat characters after the
# hash as a comment.
#
# This escaping is performed in `build.py`.
#
# Here we are replacing the escaped characters with the
# non-escaped hash character, reversing the escaping
# needed by make.
def sanitize_lib_envvar(lib_or_libl: str):
    return lib_or_libl.replace("\\#", "#")


def retrieve_ccsid(srcstmf: str) -> str:
    return _get_attr(srcstmf)["CCSID"]


def check_object_exists(obj: str, lib: str, obj_type: str) -> bool:
    obj_path = Path(f"/QSYS.LIB/{lib}.LIB/{obj}.{obj_type}")
    return obj_path.exists()


def get_physical_dependencies(obj: str, lib: str, include_self: bool, job: Optional[IBMJob] = None,
                              verbose: bool = False) -> List[Tuple[str, str, str]]:
    """Get the dependencies for a given physical file object

    Args:
        obj (str): Object name of the physical file
        lib (str): Library name of the physical file
        include_self (bool): whether to include the physical file itself in the result
        job (IBMJob, optional): Job used to run the commands. If none is set, a new job will be created. Defaults to
        None.
        verbose (bool, optional): Defaults to False.

    Returns:
        List[Tuple[str, str, str]]: List of (obj, lib, obj_type) tuples
    """

    lib_path = Path(f'/QSYS.LIB/{lib}.LIB')
    pf_path = lib_path / f"{obj}.FILE"
    if not pf_path.exists():
        if verbose:
            print(f"delete_physical_dependencies: {pf_path} does not exist.")
        return []

    if job is None:
        job = IBMJob()

    # Run DSPDBR command and save the result into a file
    job.run_cl(f"DSPDBR FILE({lib}/{obj}) OUTPUT(*OUTFILE) OUTFILE(QTEMP/DEPOUT)")
    # Query from the file to get the dependencies
    dep_files, _ = job.run_sql("SELECT WHREFI, WHRELI from QTEMP.DEPOUT")
    # For PF without deps, the result will be [('          ', '          ')], so filter it
    dep_files = list(filter(lambda t: t[0].strip() and t[1].strip(), dep_files))
    result = list(map(lambda dep_file: (dep_file[0].strip(), dep_file[1].strip(), "FILE"), dep_files))
    if include_self:
        result.append((obj, lib, "FILE"))
    return result


def delete_objects(obj_list: List[Tuple[str, str, str]], verbose: bool = False):
    for obj_tuple in obj_list:
        obj, lib, obj_type = obj_tuple
        obj_path = Path(objlib_to_path(lib, f"{obj}.{obj_type}"))
        if verbose:
            print(f"attempt to delete {obj_path}.")
        if obj_path.exists():
            shutil.rmtree(obj_path)
            if verbose:
                if obj_path.exists():
                    print(f"{obj_path} not deleted.")
                else:
                    print(f"{obj_path} not deleted.")


def filter_joblogs(record: Dict[str, Any]) -> bool:
    """Filter out the joblog records that are not related to the compile job"""
    # pylint: disable=too-many-return-statements

    msgid = record["MESSAGE_ID"]
    msgtext = record["MESSAGE_TEXT"]
    if msgid is None:
        return False
    if msgid == "CPD0912":
        # Printer device errors
        return False
    if msgid == "CPF1301":
        # Journaling errors
        return False
    if msgid == "CPF9898":
        # https://techchannel.com/SMB/02/2019/qsqsrvr-job-considerations
        return False
    if msgid == "CPF2105":
        # DLTF errors: no object found
        return False
    if msgid == "CPF1336":
        return False
    if "Job changed successfully; however errors occurred." in msgtext:
        return False
    if "SQL" in msgid:
        # Ignore all SQL errors
        return False
    return True


if __name__ == "__main__":
    cli()
