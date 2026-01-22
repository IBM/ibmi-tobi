#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-

import json
from pathlib import Path
from typing import Dict

from makei.const import DEFAULT_TGT_CCSID, DEFAULT_OBJLIB
from makei.utils import parse_all_variables


class IBMiJson:
    """A class to represent the ibmi.json file"""

    version: str
    build: Dict[str, str]

    def __init__(self, version: str, build: Dict[str, str]):
        self.version = version
        self.build = build

    @classmethod
    def from_values(cls, tgt_ccsid: str, objlib: str, version: str = None) -> "IBMiJson":
        """Creates an IBMiJson object from values"""
        return IBMiJson(version, {
            "tgt_ccsid": tgt_ccsid,
            "objlib": objlib
        })

    @classmethod
    def from_file(cls, file_path: Path, parent_ibm_i_json: "IBMiJson") -> "IBMiJson":
        if file_path.exists():
            with file_path.open() as file:
                data = json.load(file)
                if "version" in data:
                    version = data["version"]
                else:
                    version = None
                # Initialize with parent values
                tgt_ccsid = parent_ibm_i_json.build["tgt_ccsid"]
                objlib = parent_ibm_i_json.build["objlib"]
                if "build" in data:
                    build = data["build"]
                    if "tgtCcsid" in build:
                        tgt_ccsid = build["tgtCcsid"]
                    # if tgt_ccsid is None:
                    #     tgt_ccsid= "*JOB"
                    if "objlib" in build:
                        objlib = parse_all_variables(build["objlib"])

                return IBMiJson(version, {"tgt_ccsid": tgt_ccsid, "objlib": objlib})
        else:
            return parent_ibm_i_json.copy()

    def __dict__(self):
        build = {}

        if "tgt_ccsid" in self.build:
            if (self.build["tgt_ccsid"] != DEFAULT_TGT_CCSID and self.build["tgt_ccsid"] is not None and
                    self.build["tgt_ccsid"] != ""):
                build["tgtCcsid"] = self.build["tgt_ccsid"]
        if "objlib" in self.build:
            if (self.build["objlib"] != DEFAULT_OBJLIB and self.build["objlib"] is not None and
                    self.build["objlib"] != ""):
                build["objlib"] = self.build["objlib"]

        if len(build.keys()) > 0:
            return {
                "version": self.version,
                "build": build
            }
        return None

    def copy(self) -> "IBMiJson":
        """Returns a copy of the IBMiJson object"""
        import copy as copy_module
        return IBMiJson(self.version, copy_module.deepcopy(self.build))

    def save(self, file_path: str) -> None:
        """Saves the IBMiJson object to a file"""
        if not Path(file_path).exists():
            Path(file_path).touch()
        with open(file_path, 'w', encoding="utf-8") as f:
            json.dump(self.__dict__(), f, indent=4)
