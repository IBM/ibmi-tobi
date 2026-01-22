""" Constants """
from pathlib import Path

DEFAULT_TGT_CCSID = "*JOB"
DEFAULT_OBJLIB = "*CURLIB"
DEFAULT_CURLIB = "*CRTDFT"

TOBI_PATH = Path(__file__).resolve().parent.parent.parent
MK_PATH = TOBI_PATH / "src" / "mk"

METADATA_HEADER = "%METADATA"
METADATA_FOOTER = "%EMETADATA"
TEXT_HEADER = "%TEXT"

TARGET_GROUPS = ["TRG",
                 "DTAARA",
                 "DTAQ",
                 "SQL",
                 "BNDD",
                 "PF",
                 "LF",
                 "DSPF",
                 "PRTF",
                 "CMD",
                 "MODULE",
                 "SRVPGM",
                 "PGM",
                 "MENU",
                 "PNLGRP",
                 "QMQRY",
                 "WSCST",
                 "MSG"
                 ]

FILE_TARGETGROUPS_MAPPING = {
    "PGM.SQLRPGLE": {"PGM"},
    "PGM.RPGLE": {"PGM"},
    "PGM.CLLE": {"PGM"},
    "PGM.CBLLE": {"PGM"},
    "PGM.C": {"PGM"},
    "PGM.SQLCBLLE": {"PGM"},
    "CMDSRC": {"CMD"},
    "CMD": {"CMD"},
    "DSPF": {"DSPF"},
    "LF": {"LF"},
    "PF": {"PF"},
    "PRTF": {"PRTF"},
    "FILE": {"PF"},
    "MENUSRC": {"MENU"},
    "MENU": {"MENU"},
    "C": {"MODULE"},
    "CPP": {"MODULE"},
    "RPGLE": {"MODULE", "PGM"},
    "CLLE": {"MODULE", "PGM"},
    "CBLLE": {"MODULE", "PGM"},
    "SQLC": {"MODULE", "PGM"},
    "SQLCPP": {"MODULE", "PGM"},
    "SQLRPGLE": {"MODULE", "PGM"},
    "SQLCBLLE": {"MODULE", "PGM"},
    "MODULE": {"PGM"},
    "CLP": {"PGM"},
    "CBL": {"PGM"},
    "RPG": {"PGM"},
    "ILEPGM": {"PGM"},
    "PNLGRPSRC": {"PNLGRP"},
    "PNLGRP": {"PNLGRP"},
    "SQL": {"QMQRY"},
    "BND": {"SRVPGM"},
    "ILESRVPGM": {"SRVPGM"},
    "BNDDIR": {"BNDD"},
    "DTAARA": {"DTAARA"},
    "DTAQ": {"DTAQ"},
    "SYSTRG": {"TRG"},
    "SQLPRC": {"SQL"},
    "TABLE": {"SQL"},
    "PFSQL": {"SQL"},
    "VIEW": {"SQL"},
    "INDEX": {"SQL"},
    "SQLSEQ": {"SQL"},
    "SQLUDF": {"SQL"},
    "SQLTRG": {"SQL"},
    "MSGF": {"MSG"},
    "WSCSTSRC": {"WSCST"},
    "SQLVAR": {"SRVPGM"},
}

TARGET_TARGETGROUPS_MAPPING = {
    "CMD": "CMD",
    "FILE": "PF",
    "MENU": "MENU",
    "MODULE": "MODULE",
    "PGM": "PGM",
    "PNLGRP": "PNLGRP",
    "QMQRY": "QMQRY",
    "BNDDIR": "BNDD",
    "DTAARA": "DTAARA",
    "DTAQ": "DTAQ",
    "SRVPGM": "SRVPGM",
    "MSGF": "MSG",
    "WSCST": "WSCST",
    "TRG": "TRG",
}

FILE_TARGET_MAPPING = {
    "PGM.SQLRPGLE": {"PGM"},
    "PGM.RPGLE": {"PGM"},
    "PGM.CLLE": {"PGM"},
    "PGM.C": {"PGM"},
    "PGM.CBLLE": {"PGM"},
    "PGM.SQLCBLLE": {"PGM"},
    "CMDSRC": {"CMD"},
    "CMD": {"CMD"},
    "DSPF": {"FILE"},
    "LF": {"FILE"},
    "PF": {"FILE"},
    "PRTF": {"FILE"},
    "MENUSRC": {"MENU"},
    "MENU": {"MENU"},
    "C": {"MODULE", "PGM"},
    "CPP": {"MODULE"},
    "RPGLE": {"MODULE", "PGM"},
    "CLLE": {"MODULE", "PGM"},
    "CBLLE": {"MODULE", "PGM"},
    "SQLC": {"MODULE"},
    "SQLCPP": {"MODULE"},
    "SQLRPGLE": {"MODULE", "PGM"},
    "SQLCBLLE": {"MODULE", "PGM"},
    "MODULE": {"PGM"},
    "CLP": {"PGM"},
    "CBL": {"PGM"},
    "RPG": {"PGM"},
    "ILEPGM": {"PGM"},
    "PNLGRPSRC": {"PNLGRP"},
    "PNLGRP": {"PNLGRP"},
    "SQL": {"QMQRY", "SRVPGM"},
    "BND": {"SRVPGM"},
    "ILESRVPGM": {"SRVPGM"},
    "BNDDIR": {"BNDDIR"},
    "DTAARA": {"DTAARA"},
    "DTAQ": {"DTAQ"},
    "SYSTRG": {"TRG"},
    "SQLPRC": {"PGM"},
    "TABLE": {"FILE"},
    "PFSQL": {"FILE"},
    "VIEW": {"FILE"},
    "INDEX": {"FILE"},
    "SQLALIAS": {"FILE"},
    "SQLSEQ": {"DTAARA"},
    "SQLUDF": {"SRVPGM"},
    "SQLVAR": {"SRVPGM"},
    "SQLTRG": {"PGM"},
    "MSGF": {"MSGF"},
    "WSCSTSRC": {"WSCST"},
}
# This is the maximum number of dot seperated parts in the file extensions defined above.
FILE_MAX_EXT_LENGTH = max(
    map(lambda ext: len(ext.split('.')), FILE_TARGET_MAPPING.keys()))

# This is the number of lines to check in source file for member text as a comment.
MEMBER_TEXT_LINES = 15

_start_column = 7
_end_column = 72
C_STYLE_COMMENTS = (
    {"CMD", "CMDSRC", "C", "CPP", "CLLE", "CLP", "SQLC", "SQLCPP", "PGM.C", "PGM.CLLE", "BND",
        "ILESRVPGM", "BNDDIR", "DTAARA", "SYSTRG", "MSGF"},
    {
        "style_type": "C",
        "start_comment": "/*",
        "end_comment": "*/",
        "start_column": _start_column,
        "end_column": _end_column
    }
)

SQL_STYLE_COMMENTS = (
    {"TABLE", "PFSQL", "VIEW", "SQLUDT", "SQLALIAS", "SQLSEQ", "SQLPRC", "SQLTRG", "SQLUDF", "SQL", "INDEX"},
    {
        "style_type": "SQL",
        "start_comment": "--",
        "end_comment": "*",
        "start_column": _start_column,
        "end_column": _end_column
    }
)

COBOL_STYLE_COMMENTS = (
    {"DSPF", "LF", "PF", "PRTF", "RPGLE", "SQLRPGLE", "CBLLE", "SQLCBLLE", "PGM.RPGLE",
     "PGM.SQLRPGLE", "CBL", "PGM.CBLLE", "PGM.SQLCBLLE", "RPG"},
    {
        "style_type": "COBOL",
        "start_comment": "*",
        "end_comment": "*",
        "start_column": _start_column,
        "end_column": _end_column
    }
)

PNL_STYLE_COMMENTS = (
    {"PNLGRPSRC", "MENUSRC"},
    {
        "style_type": "PNL",
        "start_comment": ".*",
        "end_comment": "*",
        "start_column": 1,
        "end_column": _end_column
    }
)

COMMENT_STYLES = [C_STYLE_COMMENTS, SQL_STYLE_COMMENTS, COBOL_STYLE_COMMENTS, PNL_STYLE_COMMENTS]
