import os
import re
import pytest
from pathlib import Path
from makei.build import BuildEnv
from tests.lib.const import DATA_PATH, MAKEI_PATH


@pytest.fixture
def set_test_directory(request):
    original_cwd = Path.cwd()
    project_name = request.param
    test_dir = Path(f"{DATA_PATH}/build_env/{project_name}").resolve()
    os.chdir(test_dir)
    try:
        yield test_dir
    finally:
        os.chdir(original_cwd)


def normalize_build_env_paths(content: str) -> str:
    # This pattern finds lines starting with TGTCCSID_ or OBJPATH_,
    # then a path that includes 'ibmi-tobi', and replaces
    # the absolute part before 'ibmi-tobi' with '{ROOT_PATH}'.

    def replacer(match):
        prefix = match.group(1)  # TGTCCSID_ or OBJPATH_
        full_path = match.group(2).replace("\\", "/")  # full path including ibmi-tobi and after
        rest = match.group(3)  # everything after the path (:= ...)

        # Find LAST index of 'ibmi-tobi' in path to handle duplicate directory names
        # (e.g., /home/runner/work/ibmi-tobi/ibmi-tobi/tests/...)
        ibmi_index = full_path.rfind('ibmi-tobi')
        if ibmi_index == -1:
            # Fallback if 'ibmi-tobi' not found
            normalized_path = full_path
        else:
            normalized_path = '{ROOT_PATH}/' + full_path[ibmi_index:]

        return f"{prefix}{normalized_path}{rest}"

    pattern = re.compile(r'^(TGTCCSID_|OBJPATH_)(.+?)( := .*)$', re.MULTILINE)

    return pattern.sub(replacer, content)


@pytest.mark.parametrize("set_test_directory", ["sample_project1"], indirect=True)
def test_simple_build_env(set_test_directory):
    test_dir = set_test_directory
    try:
        build_env = BuildEnv()
        assert build_env.src_dir == test_dir
        assert build_env.targets == ["all"]
        assert build_env.make_options == ""
        assert build_env.tobi_path == MAKEI_PATH
        assert build_env.tobi_makefile == MAKEI_PATH / "src" / "mk" / "Makefile"
        assert os.path.exists(build_env.build_vars_path) is True

        assert build_env.iproj_json_path == test_dir / "iproj.json"
        assert os.path.exists(build_env.iproj_json_path) is True
        assert build_env.ibmi_env_cmds == "\\n".join(build_env.iproj_json.__dict__()['setIBMiEnvCmd'])

        assert build_env.success_targets == []
        assert build_env.failed_targets == []
    finally:
        if build_env:
            build_env._post_make()


@pytest.mark.parametrize("set_test_directory", ["sample_project1"], indirect=True)
def test_build_env_with_targets_and_options(set_test_directory):
    try:
        build_env = BuildEnv()
        assert os.path.exists(build_env.build_vars_path) is True

        with open(build_env.build_vars_path, 'r', encoding='utf-8') as actual_file, \
             open(".expectedBuildVarsMk.txt", 'r', encoding='utf-8') as expected_file:

            assert sorted(normalize_build_env_paths(actual_file.read()).splitlines()) == \
                sorted(normalize_build_env_paths(expected_file.read()).splitlines())
    finally:
        if build_env:
            build_env._post_make()
