#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from makei.crtfrmstmf import resolve_tmp_lib
from makei.ibm_job import IBMJob, save_joblog_json
from makei.utils import format_datetime, get_iasp_prefix


class CrtOvl:
    """Create an overlay object from an IFS-packaged save file."""

    job: IBMJob
    ifs_savf: str
    ovl: str
    lib: str
    parameters: Optional[str]
    precmd: str
    postcmd: str
    joblog_path: Optional[str]
    output: str
    iasp: str
    tmp_lib: str
    tmp_savf: str

    def __init__(self, ifs_savf: str, ovl: str, lib: str,
                 parameters: Optional[str] = None,
                 precmd: str = "", postcmd: str = "",
                 output: str = "",
                 joblog_path: Optional[str] = None,
                 env_settings: Optional[Dict[str, str]] = None,
                 iasp: str = "") -> None:
        self.job = IBMJob()
        self.ifs_savf = ifs_savf
        self.ovl = ovl.strip().upper()
        self.lib = lib.strip().upper()
        self.parameters = parameters
        self.precmd = precmd or ""
        self.postcmd = postcmd or ""
        self.output = output or ""
        self.joblog_path = joblog_path
        self.env_settings = env_settings or {}
        self.iasp = iasp or ""
        self.iasp_prefix = get_iasp_prefix(self.iasp)

        # mirrors crtfrmstmf: resolve_tmp_lib() -> QTEMP (non-IASP) or self.lib (IASP)
        self.tmp_lib = resolve_tmp_lib(self.lib, self.iasp)
        self.tmp_savf = "QSAVOVL"  # mirrors crtfrmstmf's tmp_src = "QSOURCE"

        # Derive the source PF name from the save-file basename (strip .FILE)
        self.srcpf = Path(ifs_savf).stem.upper()

        self.job.run_cl("CHGJOB LOG(4 00 *SECLVL)", log=False)

    def setup_env(self):
        """Set up library list / curlib exactly as crtfrmstmf does."""
        if self.env_settings.get("curlib"):
            self.job.run_cl(
                f"CHGCURLIB CURLIB({self.env_settings['curlib']})", log=True)
        if self.env_settings.get("preUsrlibl"):
            for lib in reversed(self.env_settings["preUsrlibl"].split()):
                self.job.run_cl(
                    f"ADDLIBLE LIB({lib}) POSITION(*FIRST)",
                    ignore_errors=True, log=False)
        if self.env_settings.get("postUsrlibl"):
            for lib in self.env_settings["postUsrlibl"].split():
                self.job.run_cl(
                    f"ADDLIBLE LIB({lib}) POSITION(*LAST)",
                    ignore_errors=True, log=False)
        if self.env_settings.get("IBMiEnvCmd"):
            for cmd in self.env_settings["IBMiEnvCmd"].split("\\n"):
                if "SETASPGRP" not in cmd.upper():
                    self.job.run_cl(cmd, log=True)

    def run(self) -> bool:
        success = False
        self.setup_env()
        run_datetime = datetime.now()
        crtovl_cmd = f"CRTOVL {self.lib}/{self.ovl}"  # default for joblog on early failure

        if self.precmd:
            self.job.run_cl(self.precmd, log=True)

        # mirrors crtfrmstmf: IFS path to the temp save file in tmp_lib
        qsys_savf = f"{self.iasp_prefix}/QSYS.LIB/{self.tmp_lib}.LIB/{self.tmp_savf}.FILE"

        try:
            # Step 1 - clean up any leftover tmp_savf (mirrors crtfrmstmf DLTF tmp_src)
            self.job.run_cl(
                f"DLTF FILE({self.tmp_lib}/{self.tmp_savf})",
                ignore_errors=True, log=False)

            # Step 2 - create temporary save file (mirrors crtfrmstmf CRTSRCPF)
            self.job.run_cl(f"CRTSAVF FILE({self.tmp_lib}/{self.tmp_savf})", log=True)

            # Step 3 - copy IFS save-file artefact into tmp_lib (mirrors crtfrmstmf CPYFRMSTMF)
            self.job.run_cl(
                f"CPY OBJ('{self.ifs_savf}') TOOBJ('{qsys_savf}') REPLACE(*YES)",
                log=True)

            # Step 4 - restore the source PF into the target library.
            # SAVLIB must match the library the objects were originally saved from,
            # which is the same as the build library (self.lib).
            self.job.run_cl(
                f"RSTOBJ OBJ({self.srcpf}) SAVLIB({self.lib}) DEV(*SAVF) "
                f"SAVF({self.tmp_lib}/{self.tmp_savf}) RSTLIB({self.lib})",
                log=True)

            # Step 5 - create the overlay object
            crtovl_cmd = (
                f"CRTOVL OVL({self.lib}/{self.ovl}) "
                f"FILE({self.lib}/{self.srcpf}) "
                f"MBR({self.ovl})"
            )
            if self.parameters is not None:
                crtovl_cmd = crtovl_cmd + ' ' + self.parameters
            self.job.run_cl(crtovl_cmd, log=True)

            success = True

            if self.postcmd:
                self.job.run_cl(self.postcmd, log=True)

        except Exception:  # pylint: disable=broad-except
            print(f"Build not successful for {self.lib}/{self.ovl}.OVL")

        if self.joblog_path is not None:
            save_joblog_json(
                crtovl_cmd,
                format_datetime(run_datetime),
                self.job.job_id,
                f"{self.ovl}.OVL",
                self.ifs_savf,
                self.output,
                not success,
                self.joblog_path,
            )

        return success


def _sanitize_lib(value: str) -> str:
    """Reverse the \\# escaping applied by build.py."""
    return value.replace("\\#", "#")


def cli():
    """
    crtovl program cli entry
    """
    parser = argparse.ArgumentParser(prog='crtovl')

    parser.add_argument(
        '-f',
        '--savf',
        help='Specifies the absolute IFS path to the .FILE save-file artefact.',
        metavar='<ifs_savf>',
        required=True
    )

    parser.add_argument(
        '-o',
        '--object',
        help='Enter the name of the overlay object.',
        metavar='<ovl>',
        required=True
    )

    parser.add_argument(
        '-l',
        '--library',
        help='Enter the name of the library. If no library is specified, '
             'the created object is stored in the current library.',
        metavar='<library>',
        default='*CURLIB'
    )

    parser.add_argument(
        '-p',
        '--params',
        help='Specifies the parameters added to the CRTOVL command.',
        metavar='<params>',
        nargs='?'
    )

    parser.add_argument(
        '--save-joblog',
        help='Output the joblog to the specified json file.',
        metavar='<path to joblog json file>',
    )
    parser.add_argument(
        '--precmd',
        metavar='<precmd>',
    )
    parser.add_argument(
        '--postcmd',
        metavar='<postcmd>',
    )
    parser.add_argument(
        '--output',
        metavar='<output>',
    )
    parser.add_argument(
        '-c',
        '--command',
        help='Compile command name (accepted for compatibility; not used).',
        metavar='<cmd>',
    )
    parser.add_argument(
        '--ccsid',
        help='Source CCSID (accepted for compatibility; not used).',
        metavar='<ccsid>',
    )

    args = parser.parse_args()
    ifs_savf = str(Path(args.savf.strip()).resolve())
    env_settings = {}
    if 'curlib' in os.environ:
        env_settings['curlib'] = _sanitize_lib(os.environ['curlib'])
    if 'preUsrlibl' in os.environ:
        env_settings['preUsrlibl'] = _sanitize_lib(os.environ['preUsrlibl'])
    if 'postUsrlibl' in os.environ:
        env_settings['postUsrlibl'] = _sanitize_lib(os.environ['postUsrlibl'])
    if 'IBMiEnvCmd' in os.environ:
        env_settings['IBMiEnvCmd'] = os.environ['IBMiEnvCmd']
    if 'iasp' in os.environ:
        env_settings['iasp'] = _sanitize_lib(os.environ['iasp'])

    handle = CrtOvl(
        ifs_savf=ifs_savf,
        ovl=args.object,
        lib=args.library,
        parameters=args.params,
        precmd=args.precmd,
        postcmd=args.postcmd,
        output=args.output,
        joblog_path=args.save_joblog,
        env_settings=env_settings,
        iasp=env_settings.get('iasp', ''),
    )
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    success = handle.run()
    print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    cli()
