#!/usr/bin/env python3.9

""" The utility module"""

import json
import os
import subprocess
import sys
import copy
from datetime import datetime
from enum import Enum
from pathlib import Path
from shutil import move, copymode
from tempfile import mkstemp, gettempdir
from typing import Callable, Optional, Tuple, Union

from makei.const import FILE_MAX_EXT_LENGTH, FILE_TARGET_MAPPING, COMMENT_STYLES


class Colors(str, Enum):
    """ An enum of colors to be used for output"""
    BOLD = '\033[1m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def colored(message: str, color: Colors) -> str:
    """Returns a colored message if supported
    """
    if support_color():
        return f"{color}{message}{Colors.ENDC}"
    return f"{message}"


def support_color():
    """ Detects if the terminal supports color."""
    return sys.stdout.isatty()


def parse_variable(var_name: str):
    """ Returns the value of the given variable name in the system environment,
        or the input value itself if it is not a variable name.

    >>> os.environ["key1"] = "value1"
    >>> parse_variable("key1")
    'key1'
    >>> parse_variable("&key1")
    'value1'
    >>> parse_variable("&key1")
    'value1'
    """
    if var_name.startswith("&") and len(var_name) > 1:
        var_name = var_name[1:]
        try:
            value = os.environ[var_name]
            return value
        except KeyError:
            print(colored(
                f"{var_name} must be defined first in the environment variable.", Colors.FAIL))
            sys.exit(1)
    else:
        return var_name


def parse_all_variables(input_str: str) -> str:
    """ Resolve and return the input string with all variables being replaced

    >>> os.environ["key1"] = "value1"
    >>> os.environ["key2"] = "value2"
    >>> os.environ["key3"] = "value3"
    >>> os.environ["dependency_dir"] = "dep_dir_value"
    >>> parse_all_variables("key1")
    'key1'
    >>> parse_all_variables("key1/key2")
    'key1/key2'
    >>> parse_all_variables("&key1")
    'value1'
    >>> parse_all_variables("&key1/key2")
    'value1/key2'
    >>> parse_all_variables("key1/&key2")
    'key1/value2'
    >>> parse_all_variables("key1/")
    'key1/'
    >>> parse_all_variables("/key1/")
    '/key1/'
    >>> parse_all_variables("/&key1/")
    '/value1/'
    >>> parse_all_variables("/&key1///&key2/&key3")
    '/value1///value2/value3'
    >>> parse_all_variables("&dependency_dir/includes")
    'dep_dir_value/includes'
    """
    slashList = input_str.split("/")
    result = ""
    for slashPart in slashList:
        spaceList = slashPart.split(" ")
        for spacePart in spaceList:
            result = result + parse_variable(spacePart) + ' '

        result = result[:-1] + "/"
    result = result[:-1]
    return result


def objlib_to_path(lib, object_name=None) -> str:
    """Returns the path for the given objlib in IFS

    >>> objlib_to_path("TONGKUN")
    '/QSYS.LIB/TONGKUN.LIB'
    >>> objlib_to_path("TONGKUN", "SAMREF.FILE")
    '/QSYS.LIB/TONGKUN.LIB/SAMREF.FILE'
    """
    if not lib:
        raise ValueError()
    if lib == "QSYS":
        return f"/QSYS.LIB/{object_name}"
    if object_name is not None:
        return f"/QSYS.LIB/{lib}.LIB/{object_name}"
    lib = lib.replace("#", "\\#")
    return f"/QSYS.LIB/{lib}.LIB"


def create_temp_file(file_name: str) -> Path:
    """ Creates a temporary file with the given name and returns the path to it.
    """
    temp_file = Path(gettempdir()) / file_name
    temp_file.touch()
    return temp_file


def validate_ccsid(ccsid: str):
    """Returns if the ccsid is a valid value
    """
    if ccsid == "*JOB":
        # *JOB is a valid ccsid
        return True
    if ccsid.startswith("*"):
        return False
    if ccsid == "65535":
        return False
    try:
        int(ccsid)
        temp_file = create_temp_file(f"ccsid_{ccsid}")
        if run_command(f"attr {temp_file} CCSID={ccsid}", echo_cmd=False) != 0:
            # If the ccsid is invalid, the command will fail.
            return False
        return True
    # pylint: disable=broad-except
    except Exception:
        return False


def create_ibmi_json(ibmi_json_path: Path, tgt_ccsid: str = None, version: str = None, objlib: str = None):
    """ Creates the .ibmi.json file with the given parameters.
    """
    if not ibmi_json_path.exists():
        ibmi_json_path.touch()
    with ibmi_json_path.open() as file:
        try:
            ibmi_json = json.load(file)
        except json.decoder.JSONDecodeError:
            ibmi_json = {}

        build = ibmi_json["build"] if "build" in ibmi_json else {}
        if tgt_ccsid is not None:
            build["tgtCcsid"] = tgt_ccsid
        if objlib is not None:
            build["objlib"] = objlib
        if version is not None:
            ibmi_json["version"] = version
        ibmi_json["build"] = build
        with ibmi_json_path.open("w") as file:
            json.dump(ibmi_json, file, indent=4)


def print_to_stdout(line: Union[str, bytes]):
    """Default stdoutHandler for run_command defined below to write the bytes to the stdout
    """
    if isinstance(line, str):
        line = line.encode(sys.getdefaultencoding())
    sys.stdout.buffer.write(line)
    sys.stdout.buffer.flush()


def run_command(cmd: str, stdout_handler: Callable[[bytes], None] = print_to_stdout, echo_cmd: bool = True) -> int:
    """ Run a command in a shell environment and redirect its stdout and stderr
        and returns the exit code

    Args:
        cmd (str): The command to run
        stdout_handler (Callable[[bytes], None]]): the handle function to process the stdout
    """
    if echo_cmd:
        print(colored(f"> {cmd}", Colors.OKGREEN))
    sys.stdout.flush()
    try:
        # pylint: disable=consider-using-with
        process = subprocess.Popen(
            ["bash", "-c", cmd], stdout=subprocess.PIPE, )
        for line in iter(process.stdout.readline, b''):
            stdout_handler(line)
        return process.wait()
    except FileNotFoundError as error:
        print(colored(f'Cannot find command {error.filename}!', Colors.FAIL))
    finally:
        process.kill()


def decompose_filename(filename: str) -> Tuple[str, Optional[str], str, str]:
    """Returns the (name, text-attribute, extension, dirname) of the file name
    >>> decompose_filename("SAMREF.PF")
    ('SAMREF', None, 'PF', '')
    >>> decompose_filename("/SAMREF.PF")
    ('SAMREF', None, 'PF', '/')
    >>> decompose_filename("SAMREF-TEXT.PF")
    ('SAMREF', 'TEXT', 'PF', '')
    >>> decompose_filename("test-Text.PGM.RPGLE")
    ('test', 'Text', 'PGM.RPGLE', '')
    >>> decompose_filename("../dir1/dir2/test-Text.PGM.RPGLE")
    ('test', 'Text', 'PGM.RPGLE', '../dir1/dir2')
    >>> decompose_filename("SAMHELP-Help_Application_Sam.PNLGRP")
    ('SAMHELP', 'Help_Application_Sam', 'PNLGRP', '')
    >>> decompose_filename("SAMMNU-Main_menu_application_SAMPLE.MENUSRC")
    ('SAMMNU', 'Main_menu_application_SAMPLE', 'MENUSRC', '')
    >>> decompose_filename("verifysql.sqlcblle")
    ('verifysql', None, 'SQLCBLLE', '')
    >>> decompose_filename("anbenei1.index")
    ('anbenei1', None, 'INDEX', '')
    >>> decompose_filename("custinfo1.pfsql")
    ('custinfo1', None, 'PFSQL', '')
    """
    if not filename:
        raise ValueError()

    parts = os.path.basename(filename).split(".")

    ext_len = FILE_MAX_EXT_LENGTH
    while ext_len > 0:
        base, ext = '.'.join(parts[:-ext_len]), '.'.join(parts[-ext_len:]).upper()
        if ext in FILE_TARGET_MAPPING:
            # Split the object name and text attributes
            if len(base.split("-")) == 2:
                name, text_attribute = base.split("-")
            else:
                name = base
                text_attribute = None
            return name, text_attribute, ext, os.path.dirname(filename)
        ext_len -= 1
    if ext_len == 0:
        raise ValueError(f"Cannot decompose filename: {filename} as {ext} is not a recognized file extension")


def is_source_file(filename: str) -> bool:
    """Returns true if the file is a source file
    >>> is_source_file("SAMREF.PF")
    True
    >>> is_source_file("SAMREF-TEXT.PF")
    True
    >>> is_source_file("test-Text.PGM.RPGLE")
    True
    >>> is_source_file("../dir1/dir2/test-Text.PGM.RPGLE")
    True
    >>> is_source_file("Test.PGM.RPGLE")
    True
    >>> is_source_file("Test.PGM")
    False
    """
    try:
        _, _, ext, _ = decompose_filename(filename)
        return ext in FILE_TARGET_MAPPING
    except ValueError:
        return False


def format_datetime(d: datetime) -> str:
    # 2022-03-25-09.33.34.064676
    return d.strftime("%Y-%m-%d-%H.%M.%S.%f")


def replace_file_content(file_path: Path, replace: Callable[[str], str]):
    # Create temp file
    fd, abs_path = mkstemp()
    with os.fdopen(fd, 'w') as new_file:
        with open(file_path, encoding="utf-8") as old_file:
            for line in old_file:
                new_file.write(replace(line))
    # Copy the file permissions from the old file to the new file
    copymode(file_path, abs_path)
    # Remove original file
    os.remove(file_path)
    # Move new file
    move(abs_path, file_path)


def make_include_dirs_absolute(job_log_path: str, parameters: str):
    """
    Return modified parameters with absolute dirs if it includes INCDIR
    joblog_path is the full qualified path to the joblog.json.
        Assumed that the joblog.json path is of the form
        '</project path>/.logs/joblog.json'
    parameters is a string containing all parameters to the compile command
        may contain a substring of the form INCDIR('dir' 'dir2')
    return: the same parameters string with the INCDIR replaced
        to INCDIR('<project path>/dir' '<project path>/dir2')
    Note it is possible to have INCDIR(''dir1'' ''dir2'')

    >>> make_include_dirs_absolute('/a/b/.logs/joblog.json', " PARM1( beginning)INCDIR ('PARAM1'   'PARAM2' "
    ... "''PARAM3'' 'PARAM4' )parm2( after )   ")
    " PARM1( beginning)INCDIR ('/a/b/PARAM1' '/a/b/PARAM2' ''/a/b/PARAM3'' '/a/b/PARAM4')parm2( after )   "
    >>> make_include_dirs_absolute('/a/b/.logs/joblog.json', "INCDIR (''  '''')")
    "INCDIR ('/a/b/' ''/a/b/'')"
    >>> make_include_dirs_absolute('/a/b/cd/efg/hijklmnop/.logs/joblog.json', " INCDIR( 'dir1'  ''dir2'')")
    " INCDIR('/a/b/cd/efg/hijklmnop/dir1' ''/a/b/cd/efg/hijklmnop/dir2'')"
    >>> make_include_dirs_absolute('/a/b/cd/efg/hijklmnop/.logs/joblog.json', " INCDIR( '/a/b/dir1'  ''dir2'')")
    " INCDIR('/a/b/dir1' ''/a/b/cd/efg/hijklmnop/dir2'')"
    >>> make_include_dirs_absolute('/a/b/cd/efg/hijklmnop/.logs/joblog.json', " INCDIR( ''/a/b/dir1''  ''dir2'')")
    " INCDIR(''/a/b/dir1'' ''/a/b/cd/efg/hijklmnop/dir2'')"
    >>> make_include_dirs_absolute('/.logs/joblog.json', " INCDIR('dir2')")
    " INCDIR('/dir2')"
    >>> make_include_dirs_absolute('/a/b/cd/efg/hijklmnop/.logs/joblogs.json', " INCDIR( ''/a/b/dir1''  ''dir2'')")
    " INCDIR( ''/a/b/dir1''  ''dir2'')"
    >>> make_include_dirs_absolute('/a/b/.logs/joblogs.json', "no include path here")
    'no include path here'
    >>> make_include_dirs_absolute('/joblogs.json', "no .logs")
    'no .logs'
    >>> make_include_dirs_absolute('/.logs/joblogs.json', "INCDIR but no paren")
    'INCDIR but no paren'
    >>> make_include_dirs_absolute('/.logs/joblogs.json', "INCDIR( but no close paren")
    'INCDIR( but no close paren'
    """

    # pylint: disable=too-many-locals

    try:
        index_of_job_log_substr = job_log_path.index('.logs/joblog.json')
        cur_dir = job_log_path[0:index_of_job_log_substr]
    # pylint: disable=broad-except
    except Exception:
        return parameters

    try:
        inc_dir_key_word_index = parameters.index('INCDIR')
        start_of_inc_dir = parameters.index('(', inc_dir_key_word_index)
        end_of_inc_dir = parameters.index(')', start_of_inc_dir)
    # pylint: disable=broad-except
    except Exception:
        return parameters

    include_path = []
    include_path_str = parameters[start_of_inc_dir + 1: end_of_inc_dir]
    include_path = include_path_str.split()

    # pylint: disable=consider-using-enumerate
    for i in range(len(include_path)):
        relative_path = include_path[i][1] != '/' and not (
                len(include_path[i]) > 3 and include_path[i][1] == "'" and include_path[i][2] == "/")
        enclosed_by_quotes = include_path[i][1] == "'" and len(include_path[i]) > 2

        if relative_path and cur_dir:
            if enclosed_by_quotes:
                include_path_dir = include_path[i][2:-2]
                include_path[i] = "''" + cur_dir + include_path_dir + "''"
            else:
                include_path_dir = include_path[i][1:-1]
                include_path[i] = "'" + cur_dir + include_path_dir + "'"

    start_of_param_string = parameters[0:start_of_inc_dir + 1]
    end_of_param_string = parameters[end_of_inc_dir:]
    return start_of_param_string + " ".join(include_path) + end_of_param_string


# Returns the line number where the keyword was found at (starting at 1), otherwise 0
def check_keyword_in_file(file_path: str, keyword: str, lines_to_check: int,
                          line_start_check: int = 1) -> int:
    if (line_start_check < 1):
        line_start_check = 1
    lines_counted = 0

    with open(file_path, 'r') as file:
        lines = file.readlines()

        for line_number, line in enumerate(lines[line_start_check-1:], start=line_start_check):
            if lines_counted == lines_to_check:
                break
            if keyword.lower() in line.lower():
                return line_number
            lines_counted += 1
    return 0


# Returns the line at line_number
def get_line(file_path: str, line_number: int) -> str:
    try:
        with open(file_path, "r") as file:
            for _ in range(line_number - 1):
                file.readline()
            return file.readline().rstrip('\n')
    except FileNotFoundError:
        return None


# Returns the file extension from a filepath
def get_file_extension(file_path: Path) -> str:
    extension = file_path.name.split(".", 1)[1]
    if extension.upper() == ".SRC":
        extension = ".PF"
    return extension


def get_style_dict(file_path: Path) -> dict:
    source_extension = get_file_extension(file_path)

    for style_set, style_dict in COMMENT_STYLES:
        if source_extension.upper() in style_set:
            return_dict = copy.deepcopy(style_dict)
            # Handling free form RPG
            if return_dict["style_type"] == "COBOL":
                if check_keyword_in_file(file_path, 'FREE', 1):
                    return_dict["start_comment"] = "//"
                    return_dict["end_comment"] = "*"
                    return_dict["write_on_line"] = 1
            return return_dict

    return None


if __name__ == "__main__":
    import doctest

    doctest.testmod()
