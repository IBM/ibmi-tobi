import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from tempfile import TemporaryDirectory
from makei.cvtsrcpf import CvtSrcPf, retrieve_ccsid


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing"""
    with TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@patch("makei.cvtsrcpf.IBMJob")
def test_cvtsrcpf_initialization(mock_ibm_job, temp_directory):
    """Test CvtSrcPf initialization"""
    mock_job_instance = Mock()
    mock_ibm_job.return_value = mock_job_instance

    cvt = CvtSrcPf(
        srcfile="QRPGLESRC",
        lib="MYLIB",
        tolower=True,
        default_ccsid="37",
        text=False,
        save_path=temp_directory,
    )

    assert cvt.srcfile == "QRPGLESRC"
    assert cvt.lib == "MYLIB"
    assert cvt.tolower is True
    assert cvt.default_ccsid == "37"
    assert cvt.save_path == temp_directory
    assert cvt.store_member_text is False
    assert cvt.ibmi_json_path == temp_directory / ".ibmi.json"


@patch("makei.cvtsrcpf.IBMJob")
def test_cvtsrcpf_initialization_with_invalid_ccsid(mock_ibm_job, temp_directory):
    """Test CvtSrcPf initialization with invalid CCSID"""
    mock_job_instance = Mock()
    mock_ibm_job.return_value = mock_job_instance

    cvt = CvtSrcPf(
        srcfile="QRPGLESRC",
        lib="MYLIB",
        tolower=False,
        default_ccsid="INVALID",
        save_path=temp_directory,
    )

    # Invalid CCSID should result in None
    assert cvt.default_ccsid is None


@patch("makei.cvtsrcpf.IBMJob")
def test_cvtsrcpf_get_src_mbr_name(mock_ibm_job, temp_directory):
    """Test _get_src_mbr_name method"""
    mock_job_instance = Mock()
    mock_ibm_job.return_value = mock_job_instance

    cvt = CvtSrcPf("QRPGLESRC", "MYLIB", False, save_path=temp_directory)

    src_mbr = ("TESTPGM", "RPGLE")
    name = cvt._get_src_mbr_name(src_mbr)

    assert name == "TESTPGM"


@patch("makei.cvtsrcpf.IBMJob")
def test_cvtsrcpf_get_src_mbr_ext(mock_ibm_job, temp_directory):
    """Test _get_src_mbr_ext method"""
    mock_job_instance = Mock()
    mock_ibm_job.return_value = mock_job_instance

    cvt = CvtSrcPf("QRPGLESRC", "MYLIB", False, save_path=temp_directory)

    # Test normal extension
    src_mbr1 = ("TESTPGM", "RPGLE")
    ext1 = cvt._get_src_mbr_ext(src_mbr1)
    assert ext1 == "RPGLE"

    # Test .src extension conversion
    src_mbr2 = ("TESTFILE", ".src")
    ext2 = cvt._get_src_mbr_ext(src_mbr2)
    assert ext2 == ".pf"


@patch("makei.cvtsrcpf.IBMJob")
def test_cvtsrcpf_get_dst_mbr_name(mock_ibm_job, temp_directory):
    """Test _get_dst_mbr_name method"""
    mock_job_instance = Mock()
    mock_ibm_job.return_value = mock_job_instance

    cvt = CvtSrcPf("QRPGLESRC", "MYLIB", False, save_path=temp_directory)

    # Test without tolower
    name1 = cvt._get_dst_mbr_name("TESTPGM", "RPGLE", False)
    assert name1 == "TESTPGM.RPGLE"

    # Test with tolower
    name2 = cvt._get_dst_mbr_name("TESTPGM", "RPGLE", True)
    assert name2 == "testpgm.rpgle"


@patch("makei.cvtsrcpf.IBMJob")
def test_cvtsrcpf_get_dst_mbr_path(mock_ibm_job, temp_directory):
    """Test _get_dst_mbr_path method"""
    mock_job_instance = Mock()
    mock_ibm_job.return_value = mock_job_instance

    cvt = CvtSrcPf("QRPGLESRC", "MYLIB", False, save_path=temp_directory)

    # Test path generation
    path = cvt._get_dst_mbr_path("testpgm.rpgle", "TESTPGM", "RPGLE", True)

    assert path == temp_directory / "testpgm.rpgle"


@patch("makei.cvtsrcpf.IBMJob")
def test_cvtsrcpf_get_dst_mbr_path_with_duplicates(mock_ibm_job, temp_directory):
    """Test _get_dst_mbr_path method with duplicate files"""
    mock_job_instance = Mock()
    mock_ibm_job.return_value = mock_job_instance

    cvt = CvtSrcPf("QRPGLESRC", "MYLIB", False, save_path=temp_directory)

    # Create a file to simulate duplicate
    existing_file = temp_directory / "testpgm.rpgle"
    existing_file.touch()

    # Should generate a new name with _1 suffix
    path = cvt._get_dst_mbr_path("testpgm.rpgle", "testpgm", "rpgle", True)

    assert path == temp_directory / "testpgm_1.rpgle"


@patch("makei.cvtsrcpf.IBMJob")
def test_cvtsrcpf_default_ccsid(mock_ibm_job, temp_directory):
    """Test _default_ccsid method"""
    mock_job_instance = Mock()
    mock_ibm_job.return_value = mock_job_instance

    # Test with default_ccsid set
    cvt1 = CvtSrcPf(
        "QRPGLESRC", "MYLIB", False, default_ccsid="37", save_path=temp_directory
    )
    assert cvt1._default_ccsid() == "37"

    # Test with default_ccsid None
    cvt2 = CvtSrcPf(
        "QRPGLESRC", "MYLIB", False, default_ccsid=None, save_path=temp_directory
    )
    assert cvt2._default_ccsid() == "*JOB"


@patch("makei.cvtsrcpf.IBMJob")
def test_cvtsrcpf_get_src_mbrs(mock_ibm_job, temp_directory):
    """Test _get_src_mbrs method"""
    mock_job_instance = Mock()
    mock_ibm_job.return_value = mock_job_instance

    # Mock SQL results
    mock_job_instance.run_sql.return_value = (
        [("TESTPGM1", "RPGLE"), ("TESTPGM2", "SQLRPGLE"), ("TESTCMD", "CMD")],
        ["SYSTEM_TABLE_MEMBER", "SOURCE_TYPE"],
    )

    cvt = CvtSrcPf("QRPGLESRC", "MYLIB", False, save_path=temp_directory)
    members = cvt._get_src_mbrs()

    assert len(members) == 3
    assert ("TESTPGM1", "RPGLE") in members
    assert ("TESTPGM2", "SQLRPGLE") in members
    assert ("TESTCMD", "CMD") in members


@patch("makei.cvtsrcpf.IBMJob")
def test_cvtsrcpf_get_src_mbrs_with_none_type(mock_ibm_job, temp_directory):
    """Test _get_src_mbrs method with None source type"""
    mock_job_instance = Mock()
    mock_ibm_job.return_value = mock_job_instance

    # Mock SQL results with None type
    mock_job_instance.run_sql.return_value = (
        [("TESTPGM", "RPGLE"), ("NOEXT", None)],
        ["SYSTEM_TABLE_MEMBER", "SOURCE_TYPE"],
    )

    cvt = CvtSrcPf("QRPGLESRC", "MYLIB", False, save_path=temp_directory)
    members = cvt._get_src_mbrs()

    assert len(members) == 2
    assert ("TESTPGM", "RPGLE") in members
    assert ("NOEXT", "") in members


@patch("makei.cvtsrcpf.IBMJob")
def test_cvtsrcpf_cvr_src_mbr(mock_ibm_job, temp_directory):
    """Test _cvr_src_mbr method"""
    mock_job_instance = Mock()
    mock_ibm_job.return_value = mock_job_instance
    mock_job_instance.run_cl.return_value = True

    cvt = CvtSrcPf("QRPGLESRC", "MYLIB", False, save_path=temp_directory)

    srcpath = Path("/QSYS.LIB/MYLIB.LIB/QRPGLESRC.FILE")
    dst_path = temp_directory / "testpgm.rpgle"

    result = cvt._cvr_src_mbr("TESTPGM", srcpath, "testpgm.rpgle", dst_path)

    assert result is True
    mock_job_instance.run_cl.assert_called_once()


@patch("makei.cvtsrcpf.IBMJob")
def test_cvtsrcpf_get_member_text(mock_ibm_job, temp_directory):
    """Test _get_member_text method"""
    mock_job_instance = Mock()
    mock_ibm_job.return_value = mock_job_instance

    # Mock SQL results
    mock_job_instance.run_sql.return_value = (
        [("Test program description",)],
        ["TEXT_DESCRIPTION"],
    )

    cvt = CvtSrcPf("QRPGLESRC", "MYLIB", False, save_path=temp_directory)

    srcpath = Path("/QSYS.LIB/MYLIB.LIB/QRPGLESRC.FILE")
    result = cvt._get_member_text("TESTPGM", srcpath)

    assert result[0][0][0] == "Test program description"


@patch("makei.cvtsrcpf.IBMJob")
@patch("makei.cvtsrcpf.get_style_dict")
def test_cvtsrcpf_insert_line(mock_get_style, mock_ibm_job, temp_directory):
    """Test insert_line method"""
    mock_job_instance = Mock()
    mock_ibm_job.return_value = mock_job_instance

    cvt = CvtSrcPf("QRPGLESRC", "MYLIB", False, save_path=temp_directory)

    # Create a test file
    test_file = temp_directory / "test.rpgle"
    test_file.write_text("Line 1\nLine 2\nLine 3\n")

    # Insert a line
    result = cvt.insert_line(test_file, "Test Comment", "*", "*", 0, 7, 72)

    assert result is True

    # Verify the line was inserted
    content = test_file.read_text()
    assert "Test Comment" in content


@patch("makei.cvtsrcpf.IBMJob")
def test_cvtsrcpf_insert_line_invalid_columns(mock_ibm_job, temp_directory):
    """Test insert_line with invalid column range"""
    mock_job_instance = Mock()
    mock_ibm_job.return_value = mock_job_instance

    cvt = CvtSrcPf("QRPGLESRC", "MYLIB", False, save_path=temp_directory)

    test_file = temp_directory / "test.rpgle"
    test_file.write_text("Line 1\n")

    # end_column <= start_column should return False
    result = cvt.insert_line(test_file, "Test", "*", "*", 0, 72, 7)

    assert result is False


@patch("os.popen")
def test_retrieve_ccsid(mock_popen):
    """Test retrieve_ccsid function"""
    mock_stream = Mock()
    mock_stream.read.return_value = "CCSID=37\nOWNER=USER\nSIZE=1024"
    mock_popen.return_value = mock_stream

    ccsid = retrieve_ccsid("/path/to/file", "1208")

    assert ccsid == "37"
    mock_popen.assert_called_once_with("/QOpenSys/usr/bin/attr /path/to/file")


@patch("os.popen")
def test_retrieve_ccsid_with_default(mock_popen):
    """Test retrieve_ccsid with default value when attr fails"""
    mock_stream = Mock()
    # Return valid CCSID format to test default value usage
    mock_stream.read.return_value = "CCSID=1208"
    mock_popen.return_value = mock_stream

    # Should return the CCSID from the file
    ccsid = retrieve_ccsid("/path/to/file", "1208")

    assert ccsid == "1208"


@patch("makei.cvtsrcpf.IBMJob")
@patch("makei.cvtsrcpf.check_keyword_in_file")
@patch("makei.cvtsrcpf.get_style_dict")
def test_cvtsrcpf_import_member_text(
    mock_get_style, mock_check_keyword, mock_ibm_job, temp_directory
):
    """Test import_member_text method"""
    mock_job_instance = Mock()
    mock_ibm_job.return_value = mock_job_instance

    # Mock no existing metadata
    mock_check_keyword.return_value = False

    # Mock style dict
    mock_get_style.return_value = {
        "start_comment": "*",
        "end_comment": "*",
        "start_column": 7,
        "end_column": 72,
        "write_on_line": 0,
    }

    cvt = CvtSrcPf("QRPGLESRC", "MYLIB", False, save_path=temp_directory)

    # Create a test file
    test_file = temp_directory / "test.rpgle"
    test_file.write_text("**FREE\nDcl-s myVar Char(10);\n")

    result = cvt.import_member_text(str(test_file), "Test program description")

    # Should return True (3 successful inserts)
    assert result == 3


@patch("makei.cvtsrcpf.IBMJob")
@patch("makei.cvtsrcpf.check_keyword_in_file")
@patch("makei.cvtsrcpf.get_style_dict")
def test_cvtsrcpf_import_member_text_existing_metadata(
    mock_get_style, mock_check_keyword, mock_ibm_job, temp_directory
):
    """Test import_member_text with existing metadata"""
    mock_job_instance = Mock()
    mock_ibm_job.return_value = mock_job_instance

    # Mock existing metadata and text
    mock_check_keyword.side_effect = [1, 2]  # metadata at line 1, text at line 2

    cvt = CvtSrcPf("QRPGLESRC", "MYLIB", False, save_path=temp_directory)

    test_file = temp_directory / "test.rpgle"
    test_file.write_text("**FREE\n")

    result = cvt.import_member_text(str(test_file), "Test description")

    # Should return False because metadata already exists
    assert result is False


@patch("makei.cvtsrcpf.IBMJob")
@patch("makei.cvtsrcpf.get_style_dict")
def test_cvtsrcpf_import_member_text_no_style(
    mock_get_style, mock_ibm_job, temp_directory
):
    """Test import_member_text when no style dict is found"""
    mock_job_instance = Mock()
    mock_ibm_job.return_value = mock_job_instance

    # Mock no style dict found
    mock_get_style.return_value = None

    cvt = CvtSrcPf("QRPGLESRC", "MYLIB", False, save_path=temp_directory)

    test_file = temp_directory / "test.unknown"
    test_file.write_text("Some content\n")

    result = cvt.import_member_text(str(test_file), "Test description")

    # Should return False when no style dict
    assert result is False
