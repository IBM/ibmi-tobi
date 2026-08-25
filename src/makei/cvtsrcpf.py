#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
import os
from pathlib import Path
from typing import List, Optional, Tuple

from makei.ibm_job import IBMJob
from makei.utils import (create_ibmi_json, objlib_to_path, validate_ccsid, check_keyword_in_file, get_style_dict,
                         get_iasp_prefix)
from makei.const import MEMBER_TEXT_LINES, METADATA_HEADER, METADATA_FOOTER, TEXT_HEADER, EXT_TO_COMMENT_STYLE
from makei.crtfrmstmf import resolve_tmp_lib


class CvtSrcPf:
    """convert from source physical file
    """
    # pylint: disable=too-few-public-methods
    job: IBMJob

    lib: str
    srcfile: str
    save_path: Path
    default_ccsid: Optional[str]
    tolower: bool
    ibmi_json_path: Optional[Path]
    store_member_text: bool
    iasp: str
    tmp_lib: str
    tmp_src: str
    rcdlen: int

    def __init__(
        self, srcfile: str, lib: str, tolower: bool, default_ccsid: Optional[str] = None,
            text: bool = False, save_path: Optional[Path] = None, iasp: str = "",
            rcdlen: int = 240, tmp_src: str = "QCVTSRC") -> None:
        self.job = IBMJob()

        self.lib = lib
        self.srcfile = srcfile
        self.save_path = save_path if save_path is not None else Path.cwd()
        self.iasp = iasp
        if default_ccsid is not None and validate_ccsid(default_ccsid):
            self.default_ccsid = default_ccsid
        else:
            self.default_ccsid = None

        self.tolower = tolower
        self.ibmi_json_path = save_path / ".ibmi.json"
        self.store_member_text = text
        self.iasp_prefix = get_iasp_prefix(self.iasp)
        self.tmp_src = tmp_src
        self.rcdlen = rcdlen
        self.tmp_lib = resolve_tmp_lib(self.lib, self.iasp)

    # for free form rpg, write_on_line = 1
    def insert_line(self, file_path, content, start_comment_characters: str, end_comment_characters: str,
                    write_on_line: int, start_column: int, end_column: int) -> bool:
        try:
            if end_column <= start_column:
                return False
            with open(file_path, 'r+') as file:
                lines = file.readlines()
                lines.insert(write_on_line, '\n')

                starting_whitespace = 0 if start_column == 0 else start_column - 1
                ending_whitespace = (end_column) - (starting_whitespace +
                                                    len(start_comment_characters + content + end_comment_characters))

                lines[write_on_line] = ((' ' * starting_whitespace) + start_comment_characters
                                        + content + (' ' * ending_whitespace) + end_comment_characters + '\n')
                file.seek(0)
                file.writelines(lines)
            return True
        except BaseException:
            return False

    def import_member_text(self, file_path: str, member_text: str) -> bool:
        # Check if member text exists
        metadata_comment_exists = check_keyword_in_file(file_path, METADATA_HEADER, MEMBER_TEXT_LINES)
        if metadata_comment_exists:
            text_comment_exists = check_keyword_in_file(file_path, TEXT_HEADER, MEMBER_TEXT_LINES,
                                                        metadata_comment_exists)
            if text_comment_exists and metadata_comment_exists < text_comment_exists:
                return False

        style_dict = get_style_dict(file_path)
        if style_dict is not None:
            start_comment = style_dict["start_comment"]
            end_comment = style_dict["end_comment"]
            start_column = style_dict["start_column"]
            end_column = end_column = style_dict["end_column"]
            write_on_line = style_dict["write_on_line"] if "write_on_line" in style_dict else 0

            first_write = self.insert_line(file_path, METADATA_FOOTER + ' ', start_comment,
                                           end_comment, write_on_line, start_column, end_column)
            second_write = self.insert_line(file_path, ' ' + TEXT_HEADER + ' ' + member_text, start_comment,
                                            end_comment, write_on_line, start_column, end_column)
            third_write = self.insert_line(file_path, METADATA_HEADER + ' ', start_comment, end_comment,
                                           write_on_line, start_column, end_column)

            return first_write + second_write + third_write
        return False

    def run(self) -> int:
        srcpath = Path(objlib_to_path(self.lib, f"{self.srcfile}.FILE", self.iasp))
        if not srcpath.exists():
            raise Exception(f"Source file '{srcpath}' does not exist")
        src_mbrs = self._get_src_mbrs()
        src_ccsid = retrieve_ccsid(str(srcpath), self._default_ccsid())
        if validate_ccsid(src_ccsid):
            self.default_ccsid = src_ccsid
        else:
            self.default_ccsid = "*JOB"

        print(f"{len(src_mbrs)} source members found.")
        cvt_count = 0
        for src_mbr in src_mbrs:
            src_mbr_name = self._get_src_mbr_name(src_mbr)
            src_mbr_ext = self._get_src_mbr_ext(src_mbr)
            dst_mbr_name = self._get_dst_mbr_name(src_mbr_name, src_mbr_ext, self.tolower)
            dst_mbr_path = self._get_dst_mbr_path(dst_mbr_name, src_mbr_name, src_mbr_ext, self.tolower)

            # Setup and copy source file to temporary location
            self._setup_and_copy_source_file(src_mbr_name, src_mbr_ext)

            # Get the path to the temporary source file
            tmp_srcpath = f"{self.iasp_prefix}/QSYS.LIB/{self.tmp_lib}.LIB/{self.tmp_src}.FILE"
            # Convert from temporary location and process display attributes
            if self._cvt_src_mbr(src_mbr_name, tmp_srcpath, dst_mbr_name, dst_mbr_path):
                cvt_count += 1
                if self.store_member_text:
                    result = self._get_member_text(src_mbr_name, srcpath)
                    member_text = result[0][0][0]

                    # If member has text
                    if member_text is not None:
                        successfulImport = self.import_member_text(dst_mbr_path, member_text)
                        if successfulImport:
                            print("Successfully imported member text!")

        if self.ibmi_json_path:
            create_ibmi_json(self.ibmi_json_path, tgt_ccsid=self.default_ccsid)

        return cvt_count

    def _default_ccsid(self) -> str:
        if self.default_ccsid is None:
            return "*JOB"
        else:
            return self.default_ccsid

    # Returns the source member's name without the extension
    def _get_src_mbr_name(self, src_mbr) -> str:
        return src_mbr[0]

    # Returns the source member's extension
    def _get_src_mbr_ext(self, src_mbr) -> str:
        src_mbr_ext = src_mbr[1]
        if src_mbr_ext == ".src":
            src_mbr_ext = ".pf"
        return src_mbr_ext

    def _get_dst_mbr_name(self, src_mbr_name, src_mbr_ext, tolower: bool) -> str:
        dst_mbr_name = f"{src_mbr_name}.{src_mbr_ext}"
        if tolower:
            dst_mbr_name = dst_mbr_name.lower()
        return dst_mbr_name

    def _get_dst_mbr_path(self, dst_mbr_name, src_mbr_name, src_mbr_ext, tolower: bool) -> str:
        dst_mbr_path = self.save_path / dst_mbr_name
        dups = 0
        while dst_mbr_path.exists():
            # if dst_mbr_name exists, rename it
            dups += 1
            dst_mbr_name = f"{src_mbr_name}_{dups}.{src_mbr_ext}"
            if tolower:
                dst_mbr_name = dst_mbr_name.lower()
            dst_mbr_path = self.save_path / dst_mbr_name
        return dst_mbr_path

    def _setup_and_copy_source_file(self, src_mbr_name: str, src_mbr_ext: str = "") -> None:
        """Setup temporary source physical file and copy source member to it."""
        # Delete existing temporary source file if it exists
        self.job.run_cl(f'DLTF FILE({self.tmp_lib}/{self.tmp_src})', ignore_errors=True)
        # Create temporary source physical file using tgtCcsid from .ibmi.json
        self.job.run_cl(
            f'CRTSRCPF FILE({self.tmp_lib}/{self.tmp_src}) RCDLEN({self.rcdlen}) MBR(*NONE) '
            f'CCSID({self.default_ccsid})', ignore_errors=False, log=False)

        # Copy source member to temporary file using CPYSRCF
        self.job.run_cl(
            f'CPYSRCF FROMFILE({self.lib}/{self.srcfile}) '
            f'TOFILE({self.tmp_lib}/{self.tmp_src}) '
            f'FROMMBR({src_mbr_name}) '
            f'MBROPT(*ADD)',
            ignore_errors=False, log=False)

        # Preprocess the member in QTEMP to remove hex codes before conversion
        self._preprocess_member_hex_codes(src_mbr_name, src_mbr_ext)

    @staticmethod
    def _is_comment_line(byte_list: list, src_mbr_ext: str) -> bool:
        """Return True if the EBCDIC byte_list represents a comment line.
        """
        ext = src_mbr_ext.lstrip(".").upper()
        style_type = EXT_TO_COMMENT_STYLE.get(ext)

        def first_nonspace(bl):
            for idx, b in enumerate(bl):
                if b != 0x40:   # EBCDIC space
                    return idx
            return len(bl)

        def starts_with(bl, b0, b1):
            start = first_nonspace(bl)
            return (start + 1 < len(bl)
                    and bl[start] == b0
                    and bl[start + 1] == b1)

        def col7_star(bl):
            return len(bl) > 6 and bl[6] == 0x5C  # EBCDIC '*'

        if style_type == "C":
            # /* after leading spaces  (CL, CLLE, C, BND, …)
            return starts_with(byte_list, 0x61, 0x5C)  # '/' '*'

        if style_type == "SQL":
            # -- after leading spaces  (TABLE, VIEW, SQLPRC, …)
            return starts_with(byte_list, 0x60, 0x60)  # '-' '-'

        if style_type == "PNL":
            # .* after leading spaces  (PNLGRPSRC, MENUSRC)
            return starts_with(byte_list, 0x4B, 0x5C)  # '.' '*'

        if style_type == "COBOL":
            if col7_star(byte_list):
                return True
            if ext in ("RPGLE", "SQLRPGLE"):
                return starts_with(byte_list, 0x61, 0x61)  # '/' '/'
            if ext in ("CBL", "COBOL", "SQLCBL", "CBLLE", "SQLCBLLE"):
                return any(
                    byte_list[i] == 0x5C and byte_list[i + 1] == 0x6E  # '*' '>'
                    for i in range(len(byte_list) - 1)
                )
            return False
        # Unknown extension — fall back to the universal IBM i column-7 '*' rule
        return len(byte_list) > 6 and byte_list[6] == 0x5C

    def _preprocess_member_hex_codes(self, src_mbr_name: str, src_mbr_ext: str = "") -> None:
        DISPLAY_ATTR_BYTES = set(range(0x20, 0x40))  # 0x20–0x3F

        try:
            sql_select = f"""
                SELECT SRCSEQ,
                    CAST(SRCDTA AS VARBINARY(32740)) AS RAW_DTA
                FROM {self.tmp_lib}.{self.tmp_src}
                ORDER BY SRCSEQ
            """
            results = self.job.run_sql(sql_select, ignore_errors=False, log=False)
            if not results or not results[0]:
                return

            cleaned_count = 0
            comment_hex_count = 0
            non_comment_hex_count = 0
            for srcseq, raw_dta in results[0]:
                if raw_dta is None:
                    continue

                modified = False
                in_dbcs = False
                byte_list = list(raw_dta)

                # Check before cleaning whether this line has display-attr bytes
                # on a non-comment line (developer attention needed)
                has_display_attr = any(
                    b in DISPLAY_ATTR_BYTES
                    for i, b in enumerate(byte_list)
                    if b not in (0x0E, 0x0F)  # ignore DBCS shift-out/in markers
                )
                if has_display_attr and not self._is_comment_line(byte_list, src_mbr_ext):
                    non_comment_hex_count += 1

                for i, b in enumerate(byte_list):
                    if b == 0x0E:
                        in_dbcs = True
                        continue
                    elif b == 0x0F:
                        in_dbcs = False
                        continue
                    if in_dbcs:
                        continue
                    if b in DISPLAY_ATTR_BYTES:
                        byte_list[i] = 0x40  # EBCDIC space
                        modified = True

                if modified:
                    cleaned_count += 1
                    cleaned_bytes = bytes(byte_list)
                    # Convert bytes to hex string and embed directly in SQL
                    hex_str = cleaned_bytes.hex().upper()
                    sql_update = f"""
                        UPDATE {self.tmp_lib}.{self.tmp_src}
                        SET SRCDTA = CAST(X'{hex_str}' AS VARCHAR(32740) CCSID {self.default_ccsid})
                        WHERE SRCSEQ = {srcseq}
                    """
                    self.job.run_sql(sql_update, ignore_errors=False, log=False)

            comment_hex_count = cleaned_count - non_comment_hex_count
            if cleaned_count > 0:
                print(f"\nCleaned EBCDIC display attr bytes from {cleaned_count} line(s) in {src_mbr_name}")
                print(f"[INFO]: Found {comment_hex_count} comment line(s) and "
                      f"{non_comment_hex_count} non-comment line(s) in {src_mbr_name}")

        except Exception as e:
            print(f"Warning: Could not preprocess member {src_mbr_name}: {e}")

    def _cvt_src_mbr(self, src_mbr_name, tmp_srcpath, dst_mbr_name, dst_mbr_path) -> bool:
        """Convert the preprocessed source member from temporary location to final stream file
        """
        print(f"Converting {src_mbr_name} to {dst_mbr_name}")
        return self.job.run_cl(
            f"CPYTOSTMF FROMMBR('{tmp_srcpath}/{src_mbr_name}.MBR') "
            f"TOSTMF('{dst_mbr_path}') ENDLINFMT(*LF) STMFCCSID(1208) STMFOPT(*REPLACE)",
            ignore_errors=True, log=True)

    def _get_member_text(self, src_mbr_name, srcpath):
        """Convert the source member
        """
        return self.job.run_sql(
            f"SELECT TEXT_DESCRIPTION FROM TABLE(qsys2.ifs_object_statistics('{srcpath}/{src_mbr_name}.MBR'))",
            ignore_errors=True, log=False)

    def _get_src_mbrs(self) -> List[Tuple[str, str]]:
        """Get the source members of the source file
        """
        library = self.lib.upper()
        srcpf = self.srcfile.upper()
        results = self.job.run_sql(
            f"select SYSTEM_TABLE_MEMBER, SOURCE_TYPE from qsys2.syspartitionstat "
            f"where SYSTEM_TABLE_SCHEMA='{library}' and SYSTEM_TABLE_NAME='{srcpf}'")
        if results:
            src_mbrs = []
            for row in results[0]:
                mbr_name = row[0].strip()
                if isinstance(row[1], str):
                    mbr_type = row[1].strip()
                else:
                    mbr_type = ''
                src_mbrs.append((mbr_name, mbr_type))
            return src_mbrs
        return []


def _get_attr(filepath: str, defaultCcsid: str):
    stream = os.popen(f'/QOpenSys/usr/bin/attr {filepath}')
    output = stream.read().strip()
    attrs = {"CCSID": defaultCcsid}
    if not output.__contains__("="):
        raise Exception(f"Unable to access '{filepath}' make sure file exists and that the user has permissions to it")
    else:
        for attr in output.split("\n"):
            if "=" in attr:
                [key, value] = attr.split("=")
                attrs[key] = value
    return attrs


def retrieve_ccsid(filepath: str, defaultCcsid: str) -> str:
    return _get_attr(filepath, defaultCcsid)["CCSID"]


if __name__ == "__main__":
    import doctest

    doctest.testmod()
