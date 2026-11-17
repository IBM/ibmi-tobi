#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-

import fcntl
import json
import sys
from contextlib import closing
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import ibm_db_dbi

from makei.utils import format_datetime


class IBMJob():
    job_id: str
    conn: ibm_db_dbi.Connection

    def __init__(self):
        try:
            self.conn = ibm_db_dbi.connect()
            # https://kadler.io/2018/09/20/using-python-ibm-db-with-un-journaled-files.html#
            self.conn.set_option({ibm_db_dbi.SQL_ATTR_TXN_ISOLATION: ibm_db_dbi.SQL_TXN_NO_COMMIT})
            self.job_id = self.run_sql("VALUES(QSYS2.JOB_NAME)")[0][0][0]
        # pylint: disable=broad-except
        except Exception as e:
            print(e)
            print("Cannot connect to the database")
            sys.exit(1)

    def __del__(self):
        self.conn.close()

    def run_cl(self, cmd: str, ignore_errors: bool = False, log: bool = False):
        if log:
            print(f">  {cmd}")
        with closing(self.conn.cursor()) as cursor:
            try:
                cursor.callproc("qsys2.qcmdexc", [cmd])
                return True
            # pylint: disable=broad-except
            except Exception:
                if not ignore_errors:
                    print(f"[FAILED]  {cmd}")
                    raise
                    return False
                else:
                    return True

    def run_sql(self, sql, ignore_errors=False, log: bool = False):
        with closing(self.conn.cursor()) as cursor:
            try:
                if log:
                    print(f"[QUERY] {sql}")
                cursor.execute(sql)
                try:
                    column_names = [column[0] for column in cursor.description]
                    rows = cursor.fetchall()
                # pylint: disable=broad-except
                except Exception:
                    return None
                return (rows, column_names)
            # pylint: disable=broad-except
            except Exception:
                if not ignore_errors:
                    print(f"[FAILED]  {sql}")
                    raise
                return None

    def dump_results_to_dict(self, results: Tuple[List[str], List[List[Any]]]):
        record_dicts = []
        records, column_names = results
        for record in records:
            record_dicts.append(dict(zip(column_names, record)))
        return record_dicts

    def dump_joblog(self):
        return get_joblog_for_job(self.job_id)


def get_joblog_for_job(job_id: str) -> List[Dict[str, Any]]:
    query_job = IBMJob()
    sql = "SELECT MESSAGE_ID," + \
          "MESSAGE_TEXT," + \
          "MESSAGE_SECOND_LEVEL_TEXT," + \
          "MESSAGE_TYPE," + \
          "SEVERITY," + \
          "MESSAGE_TIMESTAMP," + \
          "FROM_PROGRAM," + \
          "FROM_LIBRARY," + \
          "FROM_INSTRUCTION," + \
          "TO_PROGRAM," + \
          "TO_LIBRARY," + \
          "TO_MODULE," + \
          "TO_PROCEDURE," + \
          "TO_INSTRUCTION" + \
          " " + \
          "FROM TABLE(" + \
          f"QSYS2.JOBLOG_INFO('{job_id}')" + \
          ") A"
    results = query_job.run_sql(sql)
    joblog_dict = query_job.dump_results_to_dict(results)
    return joblog_dict


def default_filter_func(record: Dict[str, Any]) -> bool:
    _ = record
    return True


def _append_joblog_json(path: Path, entry: Dict[str, Any]):
    # Serialize only this result, before taking the lock or modifying the file.
    serialized = json.dumps([entry], indent=4).encode("utf-8")
    with path.with_suffix(".lock").open("w") as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX)
        try:
            if not path.is_file():
                with path.open("wb") as json_file:
                    json_file.write(serialized)
                return

            with path.open("r+b") as json_file:
                size = json_file.seek(0, 2)
                if size >= 10:
                    json_file.seek(0)
                    prefix = json_file.read(2)
                    json_file.seek(-8, 2)
                    suffix = json_file.read(8)
                    # Recognize the layout written by TOBi. Replace only the
                    # closing newline and array bracket, preserving old entries.
                    if prefix == b"[\n" and suffix == b"\n    }\n]":
                        json_file.seek(-2, 2)
                        json_file.write(b",\n" + serialized[2:])
                        return

                # Empty arrays (including launch's "[]\n") and other JSON
                # layouts are parsed and normalized once. Subsequent writes
                # take the constant-size read path above.
                json_file.seek(0)
                data = json.load(json_file)
                data.append(entry)
                serialized = json.dumps(data, indent=4).encode("utf-8")
                json_file.seek(0)
                json_file.write(serialized)
                json_file.truncate()
        finally:
            fcntl.flock(lock_file, fcntl.LOCK_UN)


def save_joblog_json(cmd: str, cmd_time: str, jobid: str, build_object: str, source: str, output: str,
                     failed: bool, joblog_json: Optional[str],
                     filter_func: Callable[[Dict[str, Any]], bool] = default_filter_func):
    records = get_joblog_for_job(jobid)
    messages = []
    for record in records:
        if not filter_func(record):
            continue
        if "not safe for a multithreaded job" in record["MESSAGE_TEXT"]:
            continue
        messages.append({"msgid": record["MESSAGE_ID"],
                         "type": record["MESSAGE_TYPE"],
                         "severity": record["SEVERITY"],
                         "message_time": format_datetime(record["MESSAGE_TIMESTAMP"]),
                         "message_text": record["MESSAGE_TEXT"],
                         "second_level": record["MESSAGE_SECOND_LEVEL_TEXT"],
                         "from_program": record["FROM_PROGRAM"],
                         "from_library": record["FROM_LIBRARY"],
                         "from_instruction": record["FROM_INSTRUCTION"],
                         "to_program": record["TO_PROGRAM"],
                         "to_library": record["TO_LIBRARY"],
                         "to_module": record["TO_MODULE"],
                         "to_procedure": record["TO_PROCEDURE"],
                         "to_instruction": record["TO_INSTRUCTION"]})

    dumped_joblog = {
        "cmd": cmd,
        "cmd_time": cmd_time,
        "msgs": messages,
        "object": build_object,
        "source": source,
        "output": output,
        "failed": failed
    }

    if joblog_json is not None:
        _append_joblog_json(Path(joblog_json), dumped_joblog)
    else:
        print(json.dumps([dumped_joblog], indent=4))
