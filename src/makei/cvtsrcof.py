#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-

from pathlib import Path

from makei.cvtsrcpf import CvtSrcPf
from makei.utils import objlib_to_path


class CvtSrcOf(CvtSrcPf):
    """Migrate a source physical file containing overlay members to the IFS.
    """

    # Name of the temporary save file used to package the source PF
    _OVERLAY_SAVF = "QOVLSAV"

    def run(self) -> int:
        lib = self.lib.upper()
        srcfile = self.srcfile.upper()
        savf_name = self._OVERLAY_SAVF

        # Verify the source PF exists before doing anything
        srcpath = Path(objlib_to_path(lib, f"{srcfile}.FILE", self.iasp))
        if not srcpath.exists():
            raise Exception(f"Source file '{srcpath}' does not exist")

        print(f"Source Overlay File {srcfile} found.")
        dst_filename = f"{srcfile}.FILE"
        if self.tolower:
            dst_filename = dst_filename.lower()
        dst_ifs_path = self.save_path / dst_filename

        print(f"Migrating overlay source file {lib}/{srcfile} -> {dst_filename}")

        # Step 1: Delete any existing QOVLSAV save file (ignore errors - it may not exist)
        self.job.run_cl(f"DLTF FILE({lib}/{savf_name})", ignore_errors=True, log=False)

        # Step 2: Create new QOVLSAV save file
        print(f"  Step 1: Creating save file {lib}/{savf_name}...")
        self.job.run_cl(f"CRTSAVF FILE({lib}/{savf_name})", log=True)

        # Step 3: Save the source PF into QOVLSAV
        print(f"  Step 2: Saving {lib}/{srcfile} to save file {lib}/{savf_name}...")
        self.job.run_cl(
            f"SAVOBJ OBJ({srcfile}) LIB({lib}) DEV(*SAVF) SAVF({lib}/{savf_name})",
            log=True)

        # Step 4: Copy save file from QSYS IFS path to project IFS directory
        qsys_savf_path = objlib_to_path(lib, f"{savf_name}.FILE", self.iasp)
        print(f"  Step 3: Copying {savf_name} -> {srcfile}.FILE...")
        self.job.run_cl(
            f"CPY OBJ('{qsys_savf_path}') TOOBJ('{dst_ifs_path}') REPLACE(*YES)",
            log=True)

        return 1


if __name__ == "__main__":
    import doctest

    doctest.testmod()
