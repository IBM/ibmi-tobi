from unittest.mock import Mock, patch
from makei.crtfrmstmf import (
    CrtFrmStmf,
    COMMAND_MAP,
    retrieve_ccsid,
    check_object_exists,
    get_physical_dependencies,
    delete_objects,
    filter_joblogs,
)


def test_command_map():
    """Test COMMAND_MAP contains expected mappings"""
    assert isinstance(COMMAND_MAP, dict)
    assert COMMAND_MAP["CRTCMD"] == "CMD"
    assert COMMAND_MAP["CRTBNDCL"] == "PGM"
    assert COMMAND_MAP["CRTPF"] == "FILE"
    assert COMMAND_MAP["CRTSRVPGM"] == "SRVPGM"
    assert COMMAND_MAP["CRTRPGPGM"] == "PGM"


@patch("makei.crtfrmstmf.IBMJob")
@patch("makei.crtfrmstmf.retrieve_ccsid")
@patch("makei.crtfrmstmf.check_object_exists")
def test_crtfrmstmf_initialization(
    mock_check_exists, mock_retrieve_ccsid, mock_ibm_job
):
    """Test CrtFrmStmf initialization"""
    mock_check_exists.return_value = False
    mock_retrieve_ccsid.return_value = "37"
    mock_job_instance = Mock()
    mock_ibm_job.return_value = mock_job_instance

    crt = CrtFrmStmf(
        srcstmf="/path/to/source.rpgle",
        obj="TESTOBJ",
        lib="TESTLIB",
        cmd="CRTRPGPGM",
        rcdlen=112,
    )

    assert crt.srcstmf == "/path/to/source.rpgle"
    assert crt.obj == "TESTOBJ"
    assert crt.lib == "TESTLIB"
    assert crt.cmd == "CRTRPGPGM"
    assert crt.rcdlen == 112
    assert crt.obj_type == "PGM"
    assert crt.back_up_obj_list == []


@patch("makei.crtfrmstmf.IBMJob")
@patch("makei.crtfrmstmf.retrieve_ccsid")
@patch("makei.crtfrmstmf.check_object_exists")
def test_crtfrmstmf_with_tgt_ccsid(
    mock_check_exists, mock_retrieve_ccsid, mock_ibm_job
):
    """Test CrtFrmStmf with explicit target CCSID"""
    mock_check_exists.return_value = False
    mock_job_instance = Mock()
    mock_ibm_job.return_value = mock_job_instance

    crt = CrtFrmStmf(
        srcstmf="/path/to/source.rpgle",
        obj="TESTOBJ",
        lib="TESTLIB",
        cmd="CRTRPGPGM",
        rcdlen=112,
        tgt_ccsid="37",
    )

    assert crt.ccsid_c == "37"
    # retrieve_ccsid should not be called when tgt_ccsid is provided
    mock_retrieve_ccsid.assert_not_called()


@patch("makei.crtfrmstmf.IBMJob")
@patch("makei.crtfrmstmf.retrieve_ccsid")
@patch("makei.crtfrmstmf.check_object_exists")
def test_crtfrmstmf_with_parameters(
    mock_check_exists, mock_retrieve_ccsid, mock_ibm_job
):
    """Test CrtFrmStmf with compile parameters"""
    mock_check_exists.return_value = False
    mock_retrieve_ccsid.return_value = "37"
    mock_job_instance = Mock()
    mock_ibm_job.return_value = mock_job_instance

    parameters = "DBGVIEW(*SOURCE) OPTION(*EVENTF)"
    crt = CrtFrmStmf(
        srcstmf="/path/to/source.rpgle",
        obj="TESTOBJ",
        lib="TESTLIB",
        cmd="CRTRPGPGM",
        rcdlen=112,
        parameters=parameters,
    )

    assert crt.parameters == parameters


@patch("makei.crtfrmstmf.IBMJob")
@patch("makei.crtfrmstmf.retrieve_ccsid")
@patch("makei.crtfrmstmf.check_object_exists")
@patch("makei.crtfrmstmf.get_physical_dependencies")
def test_crtfrmstmf_with_existing_pf(
    mock_get_deps, mock_check_exists, mock_retrieve_ccsid, mock_ibm_job
):
    """Test CrtFrmStmf with existing physical file"""
    mock_check_exists.return_value = True
    mock_retrieve_ccsid.return_value = "37"
    mock_job_instance = Mock()
    mock_ibm_job.return_value = mock_job_instance
    mock_get_deps.return_value = [
        ("TESTOBJ", "TESTLIB", "FILE"),
        ("LOGFILE", "TESTLIB", "FILE"),
    ]

    crt = CrtFrmStmf(
        srcstmf="/path/to/source.pf",
        obj="TESTOBJ",
        lib="TESTLIB",
        cmd="CRTPF",
        rcdlen=112,
    )

    # For PF, should get dependencies
    assert len(crt.back_up_obj_list) == 2
    mock_get_deps.assert_called_once()


@patch("makei.crtfrmstmf.IBMJob")
@patch("makei.crtfrmstmf.retrieve_ccsid")
@patch("makei.crtfrmstmf.check_object_exists")
def test_crtfrmstmf_setup_env(mock_check_exists, mock_retrieve_ccsid, mock_ibm_job):
    """Test setup_env method"""
    mock_check_exists.return_value = False
    mock_retrieve_ccsid.return_value = "37"
    mock_job_instance = Mock()
    mock_ibm_job.return_value = mock_job_instance

    env_settings = {
        "curlib": "MYLIB",
        "preUsrlibl": "LIB1 LIB2",
        "postUsrlibl": "LIB3 LIB4",
        "IBMiEnvCmd": "CHGJOB CCSID(37)\\nADDLIBLE QGPL",
    }

    crt = CrtFrmStmf(
        srcstmf="/path/to/source.rpgle",
        obj="TESTOBJ",
        lib="TESTLIB",
        cmd="CRTRPGPGM",
        rcdlen=112,
        env_settings=env_settings,
    )

    crt.setup_env()

    # Verify CL commands were called
    assert mock_job_instance.run_cl.called
    calls = mock_job_instance.run_cl.call_args_list

    # Check for CHGCURLIB
    assert any("CHGCURLIB" in str(call) for call in calls)
    # Check for ADDLIBLE
    assert any("ADDLIBLE" in str(call) for call in calls)


@patch("os.popen")
def test_retrieve_ccsid(mock_popen):
    """Test retrieve_ccsid function"""
    mock_stream = Mock()
    mock_stream.read.return_value = "CCSID=37\nOWNER=USER"
    mock_popen.return_value = mock_stream

    ccsid = retrieve_ccsid("/path/to/file")

    assert ccsid == "37"
    mock_popen.assert_called_once_with("/QOpenSys/usr/bin/attr /path/to/file")


def test_check_object_exists():
    """Test check_object_exists function"""
    with patch("pathlib.Path.exists") as mock_exists:
        mock_exists.return_value = True
        result = check_object_exists("TESTOBJ", "TESTLIB", "PGM")
        assert result is True

        mock_exists.return_value = False
        result = check_object_exists("TESTOBJ", "TESTLIB", "PGM")
        assert result is False


@patch("makei.crtfrmstmf.IBMJob")
def test_get_physical_dependencies(mock_ibm_job):
    """Test get_physical_dependencies function"""
    mock_job_instance = Mock()
    mock_ibm_job.return_value = mock_job_instance

    # Mock the SQL results
    mock_job_instance.run_sql.return_value = (
        [("LOGFILE", "TESTLIB"), ("DETFILE", "TESTLIB")],
        ["WHREFI", "WHRELI"],
    )

    with patch("pathlib.Path.exists", return_value=True):
        deps = get_physical_dependencies("TESTPF", "TESTLIB", True, mock_job_instance)

        assert len(deps) == 3  # 2 dependencies + self
        assert ("TESTPF", "TESTLIB", "FILE") in deps
        assert ("LOGFILE", "TESTLIB", "FILE") in deps
        assert ("DETFILE", "TESTLIB", "FILE") in deps


@patch("makei.crtfrmstmf.IBMJob")
def test_get_physical_dependencies_without_self(mock_ibm_job):
    """Test get_physical_dependencies without including self"""
    mock_job_instance = Mock()
    mock_ibm_job.return_value = mock_job_instance

    mock_job_instance.run_sql.return_value = (
        [("LOGFILE", "TESTLIB")],
        ["WHREFI", "WHRELI"],
    )

    with patch("pathlib.Path.exists", return_value=True):
        deps = get_physical_dependencies("TESTPF", "TESTLIB", False, mock_job_instance)

        assert len(deps) == 1
        assert ("TESTPF", "TESTLIB", "FILE") not in deps
        assert ("LOGFILE", "TESTLIB", "FILE") in deps


@patch("shutil.rmtree")
@patch("pathlib.Path.exists")
def test_delete_objects(mock_exists, mock_rmtree):
    """Test delete_objects function"""
    mock_exists.return_value = True

    obj_list = [("OBJ1", "LIB1", "PGM"), ("OBJ2", "LIB1", "FILE")]

    delete_objects(obj_list, verbose=False)

    assert mock_rmtree.call_count == 2


def test_filter_joblogs():
    """Test filter_joblogs function"""
    # Should filter out CPD0912
    record1 = {"MESSAGE_ID": "CPD0912", "MESSAGE_TEXT": "Printer device error"}
    assert filter_joblogs(record1) is False

    # Should filter out CPF1301
    record2 = {"MESSAGE_ID": "CPF1301", "MESSAGE_TEXT": "Journaling error"}
    assert filter_joblogs(record2) is False

    # Should filter out CPF9898
    record3 = {"MESSAGE_ID": "CPF9898", "MESSAGE_TEXT": "Some message"}
    assert filter_joblogs(record3) is False

    # Should filter out CPF2105
    record4 = {"MESSAGE_ID": "CPF2105", "MESSAGE_TEXT": "Object not found"}
    assert filter_joblogs(record4) is False

    # Should filter out SQL messages
    record5 = {"MESSAGE_ID": "SQL0204", "MESSAGE_TEXT": "SQL error"}
    assert filter_joblogs(record5) is False

    # Should keep other messages
    record6 = {"MESSAGE_ID": "RNF7031", "MESSAGE_TEXT": "Compilation error"}
    assert filter_joblogs(record6) is True

    # Should filter None message IDs
    record7 = {"MESSAGE_ID": None, "MESSAGE_TEXT": "Some message"}
    assert filter_joblogs(record7) is False


def test_filter_joblogs_with_text_patterns():
    """Test filter_joblogs with specific text patterns"""
    # Should filter job change errors
    record = {
        "MESSAGE_ID": "CPF1234",
        "MESSAGE_TEXT": "Job changed successfully; however errors occurred.",
    }
    assert filter_joblogs(record) is False

    # Should keep normal messages
    record2 = {"MESSAGE_ID": "RNF7031", "MESSAGE_TEXT": "Variable TEST not defined"}
    assert filter_joblogs(record2) is True


@patch("makei.crtfrmstmf.IBMJob")
@patch("makei.crtfrmstmf.retrieve_ccsid")
@patch("makei.crtfrmstmf.check_object_exists")
def test_crtfrmstmf_with_precmd_postcmd(
    mock_check_exists, mock_retrieve_ccsid, mock_ibm_job
):
    """Test CrtFrmStmf with pre and post commands"""
    mock_check_exists.return_value = False
    mock_retrieve_ccsid.return_value = "37"
    mock_job_instance = Mock()
    mock_ibm_job.return_value = mock_job_instance

    crt = CrtFrmStmf(
        srcstmf="/path/to/source.rpgle",
        obj="TESTOBJ",
        lib="TESTLIB",
        cmd="CRTRPGPGM",
        rcdlen=112,
        precmd="CHGJOB CCSID(37)",
        postcmd="GRTOBJAUT OBJ(TESTLIB/TESTOBJ) OBJTYPE(*PGM) USER(*PUBLIC) AUT(*USE)",
    )

    assert crt.precmd == "CHGJOB CCSID(37)"
    assert (
        crt.postcmd
        == "GRTOBJAUT OBJ(TESTLIB/TESTOBJ) OBJTYPE(*PGM) USER(*PUBLIC) AUT(*USE)"
    )


@patch("makei.crtfrmstmf.IBMJob")
@patch("makei.crtfrmstmf.retrieve_ccsid")
@patch("makei.crtfrmstmf.check_object_exists")
def test_crtfrmstmf_obj_type_mapping(
    mock_check_exists, mock_retrieve_ccsid, mock_ibm_job
):
    """Test that obj_type is correctly mapped from command"""
    mock_check_exists.return_value = False
    mock_retrieve_ccsid.return_value = "37"
    mock_job_instance = Mock()
    mock_ibm_job.return_value = mock_job_instance

    # Test different commands
    test_cases = [
        ("CRTCMD", "CMD"),
        ("CRTBNDCL", "PGM"),
        ("CRTPF", "FILE"),
        ("CRTSRVPGM", "SRVPGM"),
        ("CRTMNU", "MENU"),
    ]

    for cmd, expected_type in test_cases:
        crt = CrtFrmStmf(
            srcstmf="/path/to/source", obj="TESTOBJ", lib="TESTLIB", cmd=cmd, rcdlen=112
        )
        assert crt.obj_type == expected_type, f"Failed for {cmd}"
