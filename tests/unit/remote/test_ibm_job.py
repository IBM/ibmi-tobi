import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from tempfile import NamedTemporaryFile
from makei.ibm_job import IBMJob, get_joblog_for_job, save_joblog_json


@patch("makei.ibm_job.ibm_db_dbi")
def test_ibmjob_initialization(mock_ibm_db):
    """Test IBMJob initialization"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [("123456/USER/JOBNAME",)]
    mock_cursor.description = [("JOB_NAME",)]
    mock_conn.cursor.return_value = mock_cursor
    mock_ibm_db.connect.return_value = mock_conn

    job = IBMJob()

    assert job.conn == mock_conn
    assert job.job_id == "123456/USER/JOBNAME"
    mock_ibm_db.connect.assert_called_once()


@patch("makei.ibm_job.ibm_db_dbi")
def test_ibmjob_initialization_failure(mock_ibm_db):
    """Test IBMJob initialization failure"""
    mock_ibm_db.connect.side_effect = Exception("Connection failed")

    with pytest.raises(SystemExit) as exc_info:
        IBMJob()

    assert exc_info.value.code == 1


@patch("makei.ibm_job.ibm_db_dbi")
def test_ibmjob_run_cl_success(mock_ibm_db):
    """Test run_cl method with successful command"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [("123456/USER/JOBNAME",)]
    mock_cursor.description = [("JOB_NAME",)]
    mock_conn.cursor.return_value = mock_cursor
    mock_ibm_db.connect.return_value = mock_conn

    job = IBMJob()

    # Test successful CL command
    result = job.run_cl("CRTLIB LIB(TESTLIB)")

    assert result is True
    mock_cursor.callproc.assert_called_with("qsys2.qcmdexc", ["CRTLIB LIB(TESTLIB)"])


@patch("makei.ibm_job.ibm_db_dbi")
def test_ibmjob_run_cl_with_logging(mock_ibm_db, capsys):
    """Test run_cl method with logging enabled"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [("123456/USER/JOBNAME",)]
    mock_cursor.description = [("JOB_NAME",)]
    mock_conn.cursor.return_value = mock_cursor
    mock_ibm_db.connect.return_value = mock_conn

    job = IBMJob()

    # Test with logging
    job.run_cl("CRTLIB LIB(TESTLIB)", log=True)

    captured = capsys.readouterr()
    assert ">  CRTLIB LIB(TESTLIB)" in captured.out


@patch("makei.ibm_job.ibm_db_dbi")
def test_ibmjob_run_cl_failure(mock_ibm_db):
    """Test run_cl method with failed command"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [("123456/USER/JOBNAME",)]
    mock_cursor.description = [("JOB_NAME",)]
    mock_cursor.callproc.side_effect = Exception("Command failed")
    mock_conn.cursor.return_value = mock_cursor
    mock_ibm_db.connect.return_value = mock_conn

    job = IBMJob()

    # Test failed command without ignore_errors
    with pytest.raises(Exception):
        job.run_cl("INVALID COMMAND")


@patch("makei.ibm_job.ibm_db_dbi")
def test_ibmjob_run_cl_failure_ignored(mock_ibm_db, capsys):
    """Test run_cl method with failed command and ignore_errors=True"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [("123456/USER/JOBNAME",)]
    mock_cursor.description = [("JOB_NAME",)]
    mock_cursor.callproc.side_effect = Exception("Command failed")
    mock_conn.cursor.return_value = mock_cursor
    mock_ibm_db.connect.return_value = mock_conn

    job = IBMJob()

    # Test failed command with ignore_errors
    result = job.run_cl("INVALID COMMAND", ignore_errors=True)

    assert result is False


@patch("makei.ibm_job.ibm_db_dbi")
def test_ibmjob_run_sql_success(mock_ibm_db):
    """Test run_sql method with successful query"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.side_effect = [
        [("123456/USER/JOBNAME",)],  # For initialization
        [("LIB1",), ("LIB2",)],  # For actual query
    ]
    # description changes between initialization and query
    mock_cursor.description = [("LIBRARY_NAME",)]
    mock_conn.cursor.return_value = mock_cursor
    mock_ibm_db.connect.return_value = mock_conn

    job = IBMJob()

    # Update description for the actual query
    mock_cursor.description = [("LIBRARY_NAME",)]

    # Test SQL query
    result = job.run_sql("SELECT LIBRARY_NAME FROM QSYS2.LIBRARY_LIST_INFO")

    assert result is not None
    rows, columns = result
    assert len(rows) == 2
    assert columns == ["LIBRARY_NAME"]


@patch("makei.ibm_job.ibm_db_dbi")
def test_ibmjob_run_sql_with_logging(mock_ibm_db, capsys):
    """Test run_sql method with logging enabled"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.side_effect = [[("123456/USER/JOBNAME",)], [("LIB1",)]]
    mock_cursor.description = [("JOB_NAME",), ("LIBRARY_NAME",)]
    mock_conn.cursor.return_value = mock_cursor
    mock_ibm_db.connect.return_value = mock_conn

    job = IBMJob()

    # Test with logging
    job.run_sql("SELECT * FROM QSYS2.LIBRARY_LIST_INFO", log=True)

    captured = capsys.readouterr()
    assert "[QUERY]" in captured.out


@patch("makei.ibm_job.ibm_db_dbi")
def test_ibmjob_run_sql_no_results(mock_ibm_db):
    """Test run_sql method with query that returns no results"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.side_effect = [
        [("123456/USER/JOBNAME",)],
        Exception("No results"),
    ]
    mock_cursor.description = [("JOB_NAME",)]
    mock_conn.cursor.return_value = mock_cursor
    mock_ibm_db.connect.return_value = mock_conn

    job = IBMJob()

    # Test query with no results
    result = job.run_sql("DELETE FROM SOMETABLE")

    assert result is None


@patch("makei.ibm_job.ibm_db_dbi")
def test_ibmjob_run_sql_failure(mock_ibm_db):
    """Test run_sql method with failed query"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [("123456/USER/JOBNAME",)]
    mock_cursor.description = [("JOB_NAME",)]
    mock_cursor.execute.side_effect = [None, Exception("SQL error")]
    mock_conn.cursor.return_value = mock_cursor
    mock_ibm_db.connect.return_value = mock_conn

    job = IBMJob()

    # Test failed query without ignore_errors
    with pytest.raises(Exception):
        job.run_sql("INVALID SQL")


@patch("makei.ibm_job.ibm_db_dbi")
def test_ibmjob_run_sql_failure_ignored(mock_ibm_db):
    """Test run_sql method with failed query and ignore_errors=True"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [("123456/USER/JOBNAME",)]
    mock_cursor.description = [("JOB_NAME",)]
    mock_cursor.execute.side_effect = [None, Exception("SQL error")]
    mock_conn.cursor.return_value = mock_cursor
    mock_ibm_db.connect.return_value = mock_conn

    job = IBMJob()

    # Test failed query with ignore_errors
    result = job.run_sql("INVALID SQL", ignore_errors=True)

    assert result is None


@patch("makei.ibm_job.ibm_db_dbi")
def test_ibmjob_dump_results_to_dict(mock_ibm_db):
    """Test dump_results_to_dict method"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [("123456/USER/JOBNAME",)]
    mock_cursor.description = [("JOB_NAME",)]
    mock_conn.cursor.return_value = mock_cursor
    mock_ibm_db.connect.return_value = mock_conn

    job = IBMJob()

    # Test converting results to dict
    results = ([("LIB1", "CURRENT"), ("LIB2", "USER")], ["LIBRARY_NAME", "TYPE"])

    dicts = job.dump_results_to_dict(results)

    assert len(dicts) == 2
    assert dicts[0] == {"LIBRARY_NAME": "LIB1", "TYPE": "CURRENT"}
    assert dicts[1] == {"LIBRARY_NAME": "LIB2", "TYPE": "USER"}


@patch("makei.ibm_job.ibm_db_dbi")
@patch("makei.ibm_job.get_joblog_for_job")
def test_ibmjob_dump_joblog(mock_get_joblog, mock_ibm_db):
    """Test dump_joblog method"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [("123456/USER/JOBNAME",)]
    mock_cursor.description = [("JOB_NAME",)]
    mock_conn.cursor.return_value = mock_cursor
    mock_ibm_db.connect.return_value = mock_conn

    mock_get_joblog.return_value = [
        {"MESSAGE_ID": "CPF0001", "MESSAGE_TEXT": "Test message"}
    ]

    job = IBMJob()
    joblog = job.dump_joblog()

    assert len(joblog) == 1
    assert joblog[0]["MESSAGE_ID"] == "CPF0001"
    mock_get_joblog.assert_called_once_with("123456/USER/JOBNAME")


@patch("makei.ibm_job.IBMJob")
def test_get_joblog_for_job(mock_ibm_job_class):
    """Test get_joblog_for_job function"""
    mock_job = Mock()
    mock_ibm_job_class.return_value = mock_job

    # Mock SQL results
    mock_job.run_sql.return_value = (
        [
            (
                "CPF0001",
                "Test message",
                "Second level",
                "INFO",
                0,
                "2024-01-01-12.00.00.000000",
                "PROG1",
                "LIB1",
                "0001",
                "PROG2",
                "LIB2",
                "MOD1",
                "PROC1",
                "0002",
            )
        ],
        [
            "MESSAGE_ID",
            "MESSAGE_TEXT",
            "MESSAGE_SECOND_LEVEL_TEXT",
            "MESSAGE_TYPE",
            "SEVERITY",
            "MESSAGE_TIMESTAMP",
            "FROM_PROGRAM",
            "FROM_LIBRARY",
            "FROM_INSTRUCTION",
            "TO_PROGRAM",
            "TO_LIBRARY",
            "TO_MODULE",
            "TO_PROCEDURE",
            "TO_INSTRUCTION",
        ],
    )

    mock_job.dump_results_to_dict.return_value = [
        {
            "MESSAGE_ID": "CPF0001",
            "MESSAGE_TEXT": "Test message",
            "MESSAGE_SECOND_LEVEL_TEXT": "Second level",
            "MESSAGE_TYPE": "INFO",
            "SEVERITY": 0,
            "MESSAGE_TIMESTAMP": "2024-01-01-12.00.00.000000",
            "FROM_PROGRAM": "PROG1",
            "FROM_LIBRARY": "LIB1",
            "FROM_INSTRUCTION": "0001",
            "TO_PROGRAM": "PROG2",
            "TO_LIBRARY": "LIB2",
            "TO_MODULE": "MOD1",
            "TO_PROCEDURE": "PROC1",
            "TO_INSTRUCTION": "0002",
        }
    ]

    joblog = get_joblog_for_job("123456/USER/JOBNAME")

    assert len(joblog) == 1
    assert joblog[0]["MESSAGE_ID"] == "CPF0001"


@patch("makei.ibm_job.get_joblog_for_job")
@patch("makei.ibm_job.format_datetime")
def test_save_joblog_json_new_file(mock_format_dt, mock_get_joblog):
    """Test save_joblog_json with new file"""
    mock_format_dt.return_value = "2024-01-01 12:00:00"
    mock_get_joblog.return_value = [
        {
            "MESSAGE_ID": "CPF0001",
            "MESSAGE_TYPE": "INFO",
            "SEVERITY": 0,
            "MESSAGE_TIMESTAMP": "2024-01-01-12.00.00.000000",
            "MESSAGE_TEXT": "Test message",
            "MESSAGE_SECOND_LEVEL_TEXT": "Second level",
            "FROM_PROGRAM": "PROG1",
            "FROM_LIBRARY": "LIB1",
            "FROM_INSTRUCTION": "0001",
            "TO_PROGRAM": "PROG2",
            "TO_LIBRARY": "LIB2",
            "TO_MODULE": "MOD1",
            "TO_PROCEDURE": "PROC1",
            "TO_INSTRUCTION": "0002",
        }
    ]

    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        temp_path = f.name

    try:
        # Remove the file so it's created fresh
        Path(temp_path).unlink()

        save_joblog_json(
            cmd="CRTPGM PGM(TEST)",
            cmd_time="2024-01-01 12:00:00",
            jobid="123456/USER/JOBNAME",
            object="TEST.PGM",
            source="/path/to/source.rpgle",
            output="",
            failed=False,
            joblog_json=temp_path,
        )

        # Verify file was created and contains data
        with open(temp_path, "r") as f:
            data = json.load(f)

        assert len(data) == 1
        assert data[0]["cmd"] == "CRTPGM PGM(TEST)"
        assert data[0]["object"] == "TEST.PGM"
        assert data[0]["failed"] is False
        assert len(data[0]["msgs"]) == 1
    finally:
        if Path(temp_path).exists():
            Path(temp_path).unlink()


@patch("makei.ibm_job.get_joblog_for_job")
@patch("makei.ibm_job.format_datetime")
def test_save_joblog_json_append(mock_format_dt, mock_get_joblog):
    """Test save_joblog_json appending to existing file"""
    mock_format_dt.return_value = "2024-01-01 12:00:00"
    mock_get_joblog.return_value = []

    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        # Write initial data
        json.dump([{"cmd": "EXISTING", "msgs": []}], f)
        temp_path = f.name

    try:
        save_joblog_json(
            cmd="NEW COMMAND",
            cmd_time="2024-01-01 12:00:00",
            jobid="123456/USER/JOBNAME",
            object="NEW.PGM",
            source="/path/to/source.rpgle",
            output="",
            failed=False,
            joblog_json=temp_path,
        )

        # Verify data was appended
        with open(temp_path, "r") as f:
            data = json.load(f)

        assert len(data) == 2
        assert data[0]["cmd"] == "EXISTING"
        assert data[1]["cmd"] == "NEW COMMAND"
    finally:
        if Path(temp_path).exists():
            Path(temp_path).unlink()


@patch("makei.ibm_job.get_joblog_for_job")
@patch("makei.ibm_job.format_datetime")
def test_save_joblog_json_with_filter(mock_format_dt, mock_get_joblog):
    """Test save_joblog_json with filter function"""
    mock_format_dt.return_value = "2024-01-01 12:00:00"
    mock_get_joblog.return_value = [
        {
            "MESSAGE_ID": "CPF0001",
            "MESSAGE_TYPE": "INFO",
            "SEVERITY": 0,
            "MESSAGE_TIMESTAMP": "2024-01-01-12.00.00.000000",
            "MESSAGE_TEXT": "Keep this",
            "MESSAGE_SECOND_LEVEL_TEXT": "",
            "FROM_PROGRAM": "PROG1",
            "FROM_LIBRARY": "LIB1",
            "FROM_INSTRUCTION": "0001",
            "TO_PROGRAM": "PROG2",
            "TO_LIBRARY": "LIB2",
            "TO_MODULE": "MOD1",
            "TO_PROCEDURE": "PROC1",
            "TO_INSTRUCTION": "0002",
        },
        {
            "MESSAGE_ID": "CPF0002",
            "MESSAGE_TYPE": "INFO",
            "SEVERITY": 0,
            "MESSAGE_TIMESTAMP": "2024-01-01-12.00.00.000000",
            "MESSAGE_TEXT": "Filter this",
            "MESSAGE_SECOND_LEVEL_TEXT": "",
            "FROM_PROGRAM": "PROG1",
            "FROM_LIBRARY": "LIB1",
            "FROM_INSTRUCTION": "0001",
            "TO_PROGRAM": "PROG2",
            "TO_LIBRARY": "LIB2",
            "TO_MODULE": "MOD1",
            "TO_PROCEDURE": "PROC1",
            "TO_INSTRUCTION": "0002",
        },
    ]

    def filter_func(record):
        return record["MESSAGE_ID"] == "CPF0001"

    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        temp_path = f.name

    try:
        Path(temp_path).unlink()

        save_joblog_json(
            cmd="TEST",
            cmd_time="2024-01-01 12:00:00",
            jobid="123456/USER/JOBNAME",
            object="TEST.PGM",
            source="/path/to/source.rpgle",
            output="",
            failed=False,
            joblog_json=temp_path,
            filter_func=filter_func,
        )

        with open(temp_path, "r") as f:
            data = json.load(f)

        # Only one message should be saved (the filtered one)
        assert len(data[0]["msgs"]) == 1
        assert data[0]["msgs"][0]["msgid"] == "CPF0001"
    finally:
        if Path(temp_path).exists():
            Path(temp_path).unlink()
