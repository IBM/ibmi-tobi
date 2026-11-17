"""Exercise job-log persistence with real files and process-level locking."""

import fcntl
import json
import multiprocessing
from datetime import datetime
from pathlib import Path

import pytest

from makei import ibm_job


def save_log(path, index=0, **kwargs):
    ibm_job.save_joblog_json(
        cmd=f"CRTPGM PGM(TEST{index})",
        cmd_time="2026-01-01-12.00.00.000000",
        jobid="123456/USER/JOB",
        build_object=f"TEST{index}.PGM",
        source=f"test{index}.rpgle",
        output=f"test{index}.splf",
        failed=bool(index % 2),
        joblog_json=str(path) if path is not None else None,
        **kwargs,
    )


@pytest.fixture(autouse=True)
def no_database(monkeypatch):
    monkeypatch.setattr(ibm_job, "get_joblog_for_job", lambda jobid: [])


@pytest.mark.parametrize("initial", [
    None,
    "[]",
    "[]\n",  # The launch script initializes logs this way.
    " \n[ \t\n ]\r\n",
    '[{"cmd": "EXISTING", "msgs": []}]',
    json.dumps([{"cmd": "EXISTING", "msgs": []}], indent=4),
    json.dumps([{"cmd": "EXISTING", "msgs": []}], indent=4) + "\r\n  ",
    json.dumps([{"cmd": "café 日本語", "msgs": []}], indent=4, ensure_ascii=False),
])
def test_append_preserves_records_and_schema(tmp_path, initial):
    path = tmp_path / "joblog.json"
    expected = []
    if initial is not None:
        path.write_text(initial, encoding="utf-8")
        expected = json.loads(initial)

    for index in range(3):
        save_log(path, index)
        expected.append({
            "cmd": f"CRTPGM PGM(TEST{index})",
            "cmd_time": "2026-01-01-12.00.00.000000",
            "msgs": [],
            "object": f"TEST{index}.PGM",
            "source": f"test{index}.rpgle",
            "output": f"test{index}.splf",
            "failed": bool(index % 2),
        })
        # The public JSON array must be readable after every completed write.
        assert json.loads(path.read_text(encoding="utf-8")) == expected


def test_messages_and_filters_are_preserved(tmp_path, monkeypatch):
    message = {
        "MESSAGE_ID": "CPF0001",
        "MESSAGE_TYPE": "INFO",
        "SEVERITY": 0,
        "MESSAGE_TIMESTAMP": datetime(2026, 1, 1, 12),
        "MESSAGE_TEXT": 'café 日本語 "quoted" \\path\nnext line ] }',
        "MESSAGE_SECOND_LEVEL_TEXT": "More details",
        "FROM_PROGRAM": "FROMPGM",
        "FROM_LIBRARY": "FROMLIB",
        "FROM_INSTRUCTION": "0001",
        "TO_PROGRAM": "TOPGM",
        "TO_LIBRARY": "TOLIB",
        "TO_MODULE": "MODULE",
        "TO_PROCEDURE": "PROC",
        "TO_INSTRUCTION": "0002",
    }
    records = [
        message,
        dict(message, MESSAGE_ID="FILTERED"),
        dict(message, MESSAGE_TEXT="Command not safe for a multithreaded job"),
    ]
    monkeypatch.setattr(ibm_job, "get_joblog_for_job", lambda jobid: records)
    path = tmp_path / "joblog.json"
    for index in range(2):
        save_log(path, index, filter_func=lambda record: record["MESSAGE_ID"] != "FILTERED")
    entries = json.loads(path.read_text(encoding="utf-8"))
    for entry in entries:
        assert len(entry["msgs"]) == 1
        assert entry["msgs"][0] == {
            "msgid": "CPF0001", "type": "INFO", "severity": 0,
            "message_time": "2026-01-01-12.00.00.000000",
            "message_text": message["MESSAGE_TEXT"], "second_level": "More details",
            "from_program": "FROMPGM", "from_library": "FROMLIB", "from_instruction": "0001",
            "to_program": "TOPGM", "to_library": "TOLIB", "to_module": "MODULE",
            "to_procedure": "PROC", "to_instruction": "0002",
        }


def test_stdout_remains_a_json_array(capsys):
    save_log(None)
    output = capsys.readouterr().out
    entries = json.loads(output)
    assert len(entries) == 1
    assert entries[0]["object"] == "TEST0.PGM"
    assert output == json.dumps(entries, indent=4) + "\n"


class TrackedFile:
    def __init__(self, file, counts):
        self.file = file
        self.counts = counts

    def __getattr__(self, name):
        return getattr(self.file, name)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return self.file.__exit__(*args)

    def read(self, *args):
        value = self.file.read(*args)
        self.counts["read"] += len(value)
        return value

    def write(self, value):
        self.counts["written"] += len(value)
        return self.file.write(value)


@pytest.mark.parametrize("previous_count", [1, 1000])
def test_append_io_does_not_grow_with_previous_entries(tmp_path, monkeypatch, previous_count):
    path = tmp_path / "joblog.json"
    previous = [{"cmd": "EXISTING", "msgs": [{"message_text": "x" * 1024}]}] * previous_count
    before = json.dumps(previous, indent=4).encode("utf-8")
    path.write_bytes(before)
    counts = {"read": 0, "written": 0}
    original_open = Path.open

    def tracked_open(self, *args, **kwargs):
        file = original_open(self, *args, **kwargs)
        return TrackedFile(file, counts) if self == path else file

    with monkeypatch.context() as context:
        context.setattr(Path, "open", tracked_open)
        save_log(path)

    after = path.read_bytes()
    entries = json.loads(after)
    assert entries[:-1] == previous
    assert entries[-1]["object"] == "TEST0.PGM"
    # Deterministic performance regression: only inspect the array boundaries
    # and write the new result, regardless of the number of previous results.
    assert counts["read"] <= 4096
    assert counts["written"] <= len(json.dumps([entries[-1]], indent=4)) + 16
    assert after.startswith(before[:-2])
    assert after == json.dumps(entries, indent=4).encode("utf-8")


def test_serialization_failure_preserves_existing_log(tmp_path, monkeypatch):
    path = tmp_path / "joblog.json"
    save_log(path)
    before = path.read_bytes()
    # A serialization error must occur before the existing log is changed.
    monkeypatch.setattr(ibm_job, "format_datetime", lambda value: object())
    record = dict.fromkeys([
        "MESSAGE_ID", "MESSAGE_TYPE", "SEVERITY", "MESSAGE_TIMESTAMP",
        "MESSAGE_SECOND_LEVEL_TEXT", "FROM_PROGRAM", "FROM_LIBRARY", "FROM_INSTRUCTION",
        "TO_PROGRAM", "TO_LIBRARY", "TO_MODULE", "TO_PROCEDURE", "TO_INSTRUCTION",
    ])
    record["MESSAGE_TEXT"] = "test"
    monkeypatch.setattr(ibm_job, "get_joblog_for_job", lambda jobid: [record])
    with pytest.raises(TypeError):
        save_log(path, 1)
    assert path.read_bytes() == before
    with path.with_suffix(".lock").open("w") as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(lock_file, fcntl.LOCK_UN)


@pytest.mark.parametrize("initial", [b"", b"not json", b"[", b'[{"cmd": "incomplete"}'])
def test_invalid_log_is_not_overwritten(tmp_path, initial):
    path = tmp_path / "joblog.json"
    path.write_bytes(initial)
    with pytest.raises(ValueError):
        save_log(path)
    assert path.read_bytes() == initial
    # Failed writes must release the lock so a later invocation can proceed.
    with path.with_suffix(".lock").open("w") as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(lock_file, fcntl.LOCK_UN)


def test_write_error_releases_lock(tmp_path, monkeypatch):
    path = tmp_path / "joblog.json"
    save_log(path)
    before = path.read_bytes()
    original_open = Path.open

    class FailingFile(TrackedFile):
        def write(self, value):
            raise OSError("Simulated write error")

    def failing_open(self, *args, **kwargs):
        file = original_open(self, *args, **kwargs)
        return FailingFile(file, {"read": 0}) if self == path else file

    with monkeypatch.context() as context:
        context.setattr(Path, "open", failing_open)
        with pytest.raises(OSError, match="Simulated write error"):
            save_log(path, 1)
    assert path.read_bytes() == before
    with path.with_suffix(".lock").open("w") as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(lock_file, fcntl.LOCK_UN)
    save_log(path, 1)
    assert len(json.loads(path.read_bytes())) == 2


def write_parallel_logs(path, start, count, barrier):
    barrier.wait(timeout=10)
    for index in range(start, start + count):
        save_log(path, index)


@pytest.mark.parametrize("initial", [None, "[]\n"])
def test_parallel_writers_keep_every_result(tmp_path, initial):
    path = tmp_path / "joblog.json"
    if initial is not None:
        path.write_text(initial, encoding="utf-8")
    context = multiprocessing.get_context("fork")
    barrier = context.Barrier(4)
    processes = [context.Process(target=write_parallel_logs, args=(path, start, 25, barrier))
                 for start in range(0, 100, 25)]
    try:
        for process in processes:
            process.start()
        for process in processes:
            process.join(timeout=20)
        assert [process.exitcode for process in processes] == [0] * 4
    finally:
        for process in processes:
            if process.is_alive():
                process.terminate()
                process.join()

    entries = json.loads(path.read_text(encoding="utf-8"))
    assert len(entries) == 100
    assert {entry["object"] for entry in entries} == {f"TEST{index}.PGM" for index in range(100)}
    assert sum(entry["failed"] for entry in entries) == 50
