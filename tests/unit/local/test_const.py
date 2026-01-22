from pathlib import Path
from makei.const import (
    DEFAULT_TGT_CCSID,
    DEFAULT_OBJLIB,
    DEFAULT_CURLIB,
    TOBI_PATH,
    MK_PATH,
    METADATA_HEADER,
    METADATA_FOOTER,
    TEXT_HEADER,
    TARGET_GROUPS,
    FILE_TARGETGROUPS_MAPPING,
    TARGET_TARGETGROUPS_MAPPING,
    FILE_TARGET_MAPPING,
    FILE_MAX_EXT_LENGTH,
    MEMBER_TEXT_LINES,
    C_STYLE_COMMENTS,
    SQL_STYLE_COMMENTS,
    COBOL_STYLE_COMMENTS,
    PNL_STYLE_COMMENTS,
    COMMENT_STYLES,
)


def test_default_constants():
    """Test default constant values"""
    assert DEFAULT_TGT_CCSID == "*JOB"
    assert DEFAULT_OBJLIB == "*CURLIB"
    assert DEFAULT_CURLIB == "*CRTDFT"


def test_path_constants():
    """Test path constants are valid Path objects"""
    assert isinstance(TOBI_PATH, Path)
    assert isinstance(MK_PATH, Path)
    assert TOBI_PATH.exists()
    assert MK_PATH.exists()
    assert MK_PATH == TOBI_PATH / "src" / "mk"


def test_metadata_constants():
    """Test metadata header/footer constants"""
    assert METADATA_HEADER == "%METADATA"
    assert METADATA_FOOTER == "%EMETADATA"
    assert TEXT_HEADER == "%TEXT"


def test_target_groups():
    """Test TARGET_GROUPS list contains expected values"""
    assert isinstance(TARGET_GROUPS, list)
    assert len(TARGET_GROUPS) > 0
    assert "PGM" in TARGET_GROUPS
    assert "MODULE" in TARGET_GROUPS
    assert "SRVPGM" in TARGET_GROUPS
    assert "CMD" in TARGET_GROUPS
    assert "PF" in TARGET_GROUPS
    assert "LF" in TARGET_GROUPS


def test_file_targetgroups_mapping():
    """Test FILE_TARGETGROUPS_MAPPING dictionary"""
    assert isinstance(FILE_TARGETGROUPS_MAPPING, dict)

    # Test some common mappings
    assert FILE_TARGETGROUPS_MAPPING["PGM.RPGLE"] == {"PGM"}
    assert FILE_TARGETGROUPS_MAPPING["PGM.SQLRPGLE"] == {"PGM"}
    assert FILE_TARGETGROUPS_MAPPING["RPGLE"] == {"MODULE", "PGM"}
    assert FILE_TARGETGROUPS_MAPPING["SQLRPGLE"] == {"MODULE", "PGM"}
    assert FILE_TARGETGROUPS_MAPPING["CMD"] == {"CMD"}
    assert FILE_TARGETGROUPS_MAPPING["PF"] == {"PF"}


def test_target_targetgroups_mapping():
    """Test TARGET_TARGETGROUPS_MAPPING dictionary"""
    assert isinstance(TARGET_TARGETGROUPS_MAPPING, dict)

    # Test mappings
    assert TARGET_TARGETGROUPS_MAPPING["CMD"] == "CMD"
    assert TARGET_TARGETGROUPS_MAPPING["PGM"] == "PGM"
    assert TARGET_TARGETGROUPS_MAPPING["MODULE"] == "MODULE"
    assert TARGET_TARGETGROUPS_MAPPING["SRVPGM"] == "SRVPGM"


def test_file_target_mapping():
    """Test FILE_TARGET_MAPPING dictionary"""
    assert isinstance(FILE_TARGET_MAPPING, dict)

    # Test some common mappings - FILE_TARGET_MAPPING returns sets
    assert FILE_TARGET_MAPPING["PGM.RPGLE"] == {"PGM"}
    assert FILE_TARGET_MAPPING["PGM.SQLRPGLE"] == {"PGM"}
    assert FILE_TARGET_MAPPING["RPGLE"] == {"MODULE", "PGM"}
    assert FILE_TARGET_MAPPING["SQLRPGLE"] == {"MODULE", "PGM"}
    assert FILE_TARGET_MAPPING["CMD"] == {"CMD"}
    assert FILE_TARGET_MAPPING["PF"] == {"FILE"}
    assert FILE_TARGET_MAPPING["DSPF"] == {"FILE"}
    assert FILE_TARGET_MAPPING["MODULE"] == {"PGM"}
    assert FILE_TARGET_MAPPING["BND"] == {"SRVPGM"}
    assert FILE_TARGET_MAPPING["SYSTRG"] == {"TRG"}


def test_file_max_ext_length():
    """Test FILE_MAX_EXT_LENGTH is calculated correctly"""
    assert isinstance(FILE_MAX_EXT_LENGTH, int)
    assert FILE_MAX_EXT_LENGTH > 0

    # Verify it's the max length of dot-separated parts
    max_len = max(len(ext.split(".")) for ext in FILE_TARGET_MAPPING.keys())
    assert FILE_MAX_EXT_LENGTH == max_len


def test_member_text_lines():
    """Test MEMBER_TEXT_LINES constant"""
    assert isinstance(MEMBER_TEXT_LINES, int)
    assert MEMBER_TEXT_LINES == 15


def test_c_style_comments():
    """Test C_STYLE_COMMENTS tuple structure"""
    assert isinstance(C_STYLE_COMMENTS, tuple)
    assert len(C_STYLE_COMMENTS) == 2

    extensions, style_dict = C_STYLE_COMMENTS
    assert isinstance(extensions, set)
    assert isinstance(style_dict, dict)

    # Check extensions
    assert "CMD" in extensions
    assert "C" in extensions
    assert "CPP" in extensions
    assert "CLLE" in extensions

    # Check style dict
    assert style_dict["style_type"] == "C"
    assert style_dict["start_comment"] == "/*"
    assert style_dict["end_comment"] == "*/"
    assert "start_column" in style_dict
    assert "end_column" in style_dict


def test_sql_style_comments():
    """Test SQL_STYLE_COMMENTS tuple structure"""
    assert isinstance(SQL_STYLE_COMMENTS, tuple)
    assert len(SQL_STYLE_COMMENTS) == 2

    extensions, style_dict = SQL_STYLE_COMMENTS
    assert isinstance(extensions, set)
    assert isinstance(style_dict, dict)

    # Check extensions
    assert "TABLE" in extensions
    assert "VIEW" in extensions
    assert "SQL" in extensions

    # Check style dict
    assert style_dict["style_type"] == "SQL"
    assert style_dict["start_comment"] == "--"
    assert style_dict["end_comment"] == "*"


def test_cobol_style_comments():
    """Test COBOL_STYLE_COMMENTS tuple structure"""
    assert isinstance(COBOL_STYLE_COMMENTS, tuple)
    assert len(COBOL_STYLE_COMMENTS) == 2

    extensions, style_dict = COBOL_STYLE_COMMENTS
    assert isinstance(extensions, set)
    assert isinstance(style_dict, dict)

    # Check extensions
    assert "RPGLE" in extensions
    assert "SQLRPGLE" in extensions
    assert "CBLLE" in extensions
    assert "PF" in extensions
    assert "DSPF" in extensions

    # Check style dict
    assert style_dict["style_type"] == "COBOL"
    assert style_dict["start_comment"] == "*"
    assert style_dict["end_comment"] == "*"


def test_pnl_style_comments():
    """Test PNL_STYLE_COMMENTS tuple structure"""
    assert isinstance(PNL_STYLE_COMMENTS, tuple)
    assert len(PNL_STYLE_COMMENTS) == 2

    extensions, style_dict = PNL_STYLE_COMMENTS
    assert isinstance(extensions, set)
    assert isinstance(style_dict, dict)

    # Check extensions
    assert "PNLGRPSRC" in extensions
    assert "MENUSRC" in extensions

    # Check style dict
    assert style_dict["style_type"] == "PNL"
    assert style_dict["start_comment"] == ".*"
    assert style_dict["end_comment"] == "*"
    assert style_dict["start_column"] == 1


def test_comment_styles():
    """Test COMMENT_STYLES list contains all comment style tuples"""
    assert isinstance(COMMENT_STYLES, list)
    assert len(COMMENT_STYLES) == 4

    assert C_STYLE_COMMENTS in COMMENT_STYLES
    assert SQL_STYLE_COMMENTS in COMMENT_STYLES
    assert COBOL_STYLE_COMMENTS in COMMENT_STYLES
    assert PNL_STYLE_COMMENTS in COMMENT_STYLES


def test_file_extensions_coverage():
    """Test that common file extensions are covered in mappings"""
    common_extensions = [
        "RPGLE",
        "SQLRPGLE",
        "CLLE",
        "C",
        "CPP",
        "CMD",
        "PF",
        "LF",
        "DSPF",
        "SYSTRG"
    ]

    for ext in common_extensions:
        assert ext in FILE_TARGET_MAPPING, f"{ext} not in FILE_TARGET_MAPPING"
        assert (
            ext in FILE_TARGETGROUPS_MAPPING
        ), f"{ext} not in FILE_TARGETGROUPS_MAPPING"


def test_mapping_consistency():
    """Test consistency between different mapping dictionaries"""
    # Every key in FILE_TARGET_MAPPING should map to a value in TARGET_TARGETGROUPS_MAPPING
    for file_ext, targets in FILE_TARGET_MAPPING.items():
        # FILE_TARGET_MAPPING values are sets, so iterate through them
        for target in targets:
            if target in TARGET_TARGETGROUPS_MAPPING:
                # Verify the target group exists
                target_group = TARGET_TARGETGROUPS_MAPPING[target]
                assert (
                    target_group in TARGET_GROUPS
                ), f"{target_group} not in TARGET_GROUPS"


def test_comment_style_column_ranges():
    """Test that comment style column ranges are valid"""
    for comment_style in COMMENT_STYLES:
        _, style_dict = comment_style
        start_col = style_dict["start_column"]
        end_col = style_dict["end_column"]

        assert isinstance(start_col, int)
        assert isinstance(end_col, int)
        assert start_col >= 0
        assert end_col > start_col
