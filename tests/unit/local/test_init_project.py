import json
import pytest
from pathlib import Path
from unittest.mock import patch
from tempfile import TemporaryDirectory
from makei.init_project import (
    ProjSpec,
    yes,
    prompt,
    create_file,
    update_json_field,
    retrieve_json_val,
    init_project,
)


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing"""
    with TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_yes_function():
    """Test yes function with various inputs"""
    assert yes("yes") is True
    assert yes("Yes") is True
    assert yes("YES") is True
    assert yes("y") is True
    assert yes("Y") is True
    assert yes("") is True  # Empty string defaults to yes
    assert yes("no") is False
    assert yes("No") is False
    assert yes("n") is False
    assert yes("anything") is False


@patch("builtins.input", return_value="test_value")
def test_prompt_with_input(mock_input):
    """Test prompt function with user input"""
    result = prompt("Enter value", "default")

    assert result == "test_value"
    mock_input.assert_called_once_with("Enter value: (default) ")


@patch("builtins.input", return_value="")
def test_prompt_with_default(mock_input):
    """Test prompt function using default value"""
    result = prompt("Enter value", "default_value")

    assert result == "default_value"


@patch("builtins.input", return_value="")
def test_prompt_without_default(mock_input):
    """Test prompt function without default value"""
    result = prompt("Enter value", None)

    assert result is None


def test_create_file_new(temp_directory):
    """Test create_file with new file"""
    file_path = temp_directory / "test.txt"
    content = "Test content"

    create_file(file_path, content)

    assert file_path.exists()
    assert file_path.read_text() == content


def test_create_file_none_content(temp_directory):
    """Test create_file with None content"""
    file_path = temp_directory / "test.txt"

    create_file(file_path, None)

    # File should not be created
    assert not file_path.exists()


@patch("builtins.input", return_value="yes")
def test_create_file_overwrite_existing(mock_input, temp_directory):
    """Test create_file overwrites existing file when confirmed"""
    file_path = temp_directory / "test.txt"
    file_path.write_text("Old content")

    create_file(file_path, "New content")

    assert file_path.read_text() == "New content"


@patch("builtins.input", return_value="no")
def test_create_file_no_overwrite(mock_input, temp_directory):
    """Test create_file doesn't overwrite when declined"""
    file_path = temp_directory / "test.txt"
    file_path.write_text("Old content")

    create_file(file_path, "New content")

    # Content should remain unchanged
    assert file_path.read_text() == "Old content"


def test_create_file_force_overwrite(temp_directory):
    """Test create_file with force=True"""
    file_path = temp_directory / "test.txt"
    file_path.write_text("Old content")

    create_file(file_path, "New content", force=True)

    # Should overwrite without prompting
    assert file_path.read_text() == "New content"


def test_update_json_field_single_key(temp_directory):
    """Test update_json_field with single key"""
    json_path = temp_directory / "test.json"
    initial_data = {"key1": "value1", "key2": "value2"}

    with json_path.open("w") as f:
        json.dump(initial_data, f)

    update_json_field(str(json_path), "key1", "updated_value")

    with json_path.open("r") as f:
        data = json.load(f)

    assert data["key1"] == "updated_value"
    assert data["key2"] == "value2"


def test_update_json_field_nested_key(temp_directory):
    """Test update_json_field with nested keys"""
    json_path = temp_directory / "test.json"
    initial_data = {"key1": "value1", "nested": {"subkey": "old_value"}}

    with json_path.open("w") as f:
        json.dump(initial_data, f)

    update_json_field(str(json_path), "nested", "new_value", "subkey")

    with json_path.open("r") as f:
        data = json.load(f)

    assert data["nested"]["subkey"] == "new_value"


def test_retrieve_json_val_single_key(temp_directory):
    """Test retrieve_json_val with single key"""
    json_path = temp_directory / "test.json"
    test_data = {"key1": "value1", "key2": "value2"}

    with json_path.open("w") as f:
        json.dump(test_data, f)

    result = retrieve_json_val(str(json_path), "key1")

    assert result == "value1"


def test_retrieve_json_val_nested_key(temp_directory):
    """Test retrieve_json_val with nested keys"""
    json_path = temp_directory / "test.json"
    test_data = {"nested": {"subkey": "nested_value"}}

    with json_path.open("w") as f:
        json.dump(test_data, f)

    result = retrieve_json_val(str(json_path), "nested", "subkey")

    assert result == "nested_value"


def test_retrieve_json_val_missing_key(temp_directory):
    """Test retrieve_json_val with missing key"""
    json_path = temp_directory / "test.json"
    test_data = {"key1": "value1"}

    with json_path.open("w") as f:
        json.dump(test_data, f)

    result = retrieve_json_val(str(json_path), "missing_key")

    assert result is None


@patch("builtins.input")
def test_projspec_initialization(mock_input):
    """Test ProjSpec initialization"""
    # Mock user inputs
    mock_input.side_effect = [
        "My Project",  # description
        "https://github.com/user/repo",  # repository
        "/usr/include",  # include_path
        "MYLIB",  # objlib
        "37",  # tgt_ccsid
        "MYLIB",  # curlib
        "LIB1, LIB2",  # pre_usr_libl
        "LIB3",  # post_usr_libl
        "CHGJOB CCSID(37)",  # set_ibm_i_env_cmd
        "MIT",  # license
    ]

    proj_spec = ProjSpec(None, None)

    assert proj_spec.description == "My Project"
    assert proj_spec.repository == "https://github.com/user/repo"
    assert proj_spec.include_path == ["/usr/include"]
    assert proj_spec.objlib == "MYLIB"
    assert proj_spec.tgt_ccsid == "37"
    assert proj_spec.curlib == "MYLIB"
    assert proj_spec.pre_usr_libl == ["LIB1", "LIB2"]
    assert proj_spec.post_usr_libl == ["LIB3"]
    assert proj_spec.set_ibm_i_env_cmd == ["CHGJOB CCSID(37)"]
    assert proj_spec.license == "MIT"


@patch("builtins.input")
def test_projspec_with_provided_objlib_and_ccsid(mock_input):
    """Test ProjSpec with objlib and tgt_ccsid provided"""
    mock_input.side_effect = [
        "My Project",  # description
        "",  # repository (empty)
        "",  # include_path (empty)
        "MYLIB",  # curlib
        "",  # pre_usr_libl (empty)
        "",  # post_usr_libl (empty)
        "",  # set_ibm_i_env_cmd (empty)
        "",  # license (empty)
    ]

    proj_spec = ProjSpec(objlib="PROVIDEDLIB", tgt_ccsid="1208")

    assert proj_spec.objlib == "PROVIDEDLIB"
    assert proj_spec.tgt_ccsid == "1208"


@patch("builtins.input")
def test_projspec_input_str_to_list(mock_input):
    """Test ProjSpec _input_str_to_list method"""
    mock_input.side_effect = [
        "Test",  # description
        "",  # repository
        "path1, path2, path3",  # include_path
        "LIB",  # objlib
        "37",  # tgt_ccsid
        "LIB",  # curlib
        "LIB1,  LIB2  , LIB3",  # pre_usr_libl with spaces
        "",  # post_usr_libl
        "",  # set_ibm_i_env_cmd
        "",  # license
    ]

    proj_spec = ProjSpec(None, None)

    # Should handle comma-separated values with spaces
    assert proj_spec.include_path == ["path1", "path2", "path3"]
    assert proj_spec.pre_usr_libl == ["LIB1", "LIB2", "LIB3"]
    assert proj_spec.post_usr_libl == []


@patch("builtins.input")
def test_projspec_generate_iproj_json(mock_input):
    """Test ProjSpec generate_iproj_json method"""
    mock_input.side_effect = [
        "Test Project",
        "https://github.com/test/repo",
        "/usr/include",
        "TESTLIB",
        "37",
        "TESTLIB",
        "LIB1",
        "LIB2",
        "CHGJOB CCSID(37)",
        "MIT",
    ]

    proj_spec = ProjSpec(None, None)
    iproj_json_str = proj_spec.generate_iproj_json()

    # Parse the JSON string
    iproj_data = json.loads(iproj_json_str)

    assert iproj_data["description"] == "Test Project"
    assert iproj_data["version"] == "1.0.0"
    assert iproj_data["repository"] == "https://github.com/test/repo"
    assert iproj_data["includePath"] == ["/usr/include"]
    assert iproj_data["objlib"] == "TESTLIB"
    assert iproj_data["tgtCcsid"] == "37"


@patch("builtins.input")
def test_projspec_generate_ibmi_json(mock_input):
    """Test ProjSpec generate_ibmi_json method"""
    mock_input.side_effect = ["Test", "", "", "LIB", "37", "LIB", "", "", "", ""]

    proj_spec = ProjSpec(None, None)
    ibmi_json_str = proj_spec.generate_ibmi_json()

    # Parse the JSON string
    ibmi_data = json.loads(ibmi_json_str)

    assert ibmi_data["version"] == "1.0.0"
    assert ibmi_data["build"]["tgtCcsid"] == "37"


def test_projspec_generate_ibmi_json_static():
    """Test ProjSpec.generate_ibmi_json static method"""
    ibmi_json_str = ProjSpec.generate_ibmi_json(None, "1.0.0", "37")

    ibmi_data = json.loads(ibmi_json_str)

    assert ibmi_data["version"] == "1.0.0"
    assert ibmi_data["build"]["tgtCcsid"] == "37"


@patch("builtins.input")
def test_projspec_generate_rules_mk(mock_input):
    """Test ProjSpec generate_rules_mk method"""
    mock_input.side_effect = ["Test", "", "", "LIB", "37", "LIB", "", "", "", ""]

    proj_spec = ProjSpec(None, None)
    rules_mk = proj_spec.generate_rules_mk()

    assert "SUBDIRS :=" in rules_mk
    assert "https://ibm.github.io/ibmi-tobi" in rules_mk


@patch("builtins.input", side_effect=["yes"])
@patch("makei.init_project.create_file")
def test_init_project_new(mock_create_file, mock_input, temp_directory):
    """Test init_project creating new project"""
    with patch("pathlib.Path.cwd", return_value=temp_directory):
        with patch("builtins.input") as mock_proj_input:
            mock_proj_input.side_effect = [
                "Test Project",
                "",
                "",
                "TESTLIB",
                "37",
                "TESTLIB",
                "",
                "",
                "",
                "",
                "yes",  # Confirm creation
            ]

            init_project(force=False, objlib=None, tgtCcsid=None)

            # Verify create_file was called for iproj.json, .ibmi.json, and Rules.mk
            assert mock_create_file.call_count == 3


@patch("makei.init_project.update_json_field")
def test_init_project_update_objlib(mock_update, temp_directory):
    """Test init_project updating objlib in existing project"""
    with patch("pathlib.Path.cwd", return_value=temp_directory):
        # Create existing iproj.json
        iproj_path = temp_directory / "iproj.json"
        iproj_path.write_text('{"version": "1.0.0", "objlib": "OLDLIB"}')

        init_project(force=False, objlib="NEWLIB", tgtCcsid=None)

        # Verify update_json_field was called
        mock_update.assert_called()


@patch("makei.init_project.update_json_field")
@patch("makei.init_project.create_file")
def test_init_project_update_tgtccsid(mock_create, mock_update, temp_directory):
    """Test init_project updating tgtCcsid in existing project"""
    with patch("pathlib.Path.cwd", return_value=temp_directory):
        # Create existing iproj.json
        iproj_path = temp_directory / "iproj.json"
        iproj_path.write_text('{"version": "1.0.0", "tgtCcsid": "37"}')

        init_project(force=False, objlib=None, tgtCcsid="1208")

        # Verify update was called
        assert mock_update.called or mock_create.called


@patch("builtins.input", return_value="no")
def test_init_project_cancelled(mock_input, temp_directory):
    """Test init_project when user cancels"""
    with patch("pathlib.Path.cwd", return_value=temp_directory):
        with patch("builtins.input") as mock_proj_input:
            mock_proj_input.side_effect = [
                "Test",
                "",
                "",
                "LIB",
                "37",
                "LIB",
                "",
                "",
                "",
                "",
                "no",  # Cancel
            ]

            with pytest.raises(SystemExit):
                init_project(force=False)


def test_projspec_get_repository_with_git_config(temp_directory):
    """Test ProjSpec _get_repository with git config"""
    # Create a mock .git/config file
    git_dir = temp_directory / ".git"
    git_dir.mkdir()
    config_file = git_dir / "config"
    config_content = """[core]
    repositoryformatversion = 0
[remote "origin"]
    url = git@github.com:user/repo.git
    fetch = +refs/heads/*:refs/remotes/origin/*
"""
    config_file.write_text(config_content)

    with patch("pathlib.Path.cwd", return_value=temp_directory):
        with patch("builtins.input") as mock_input:
            mock_input.side_effect = [
                "Test",
                "",  # Will use git config
                "",
                "LIB",
                "37",
                "LIB",
                "",
                "",
                "",
                "",
            ]

            proj_spec = ProjSpec(None, None)

            # Should convert git@ URL to https://
            assert proj_spec.repository == "https://github.com/user/repo.git"


def test_projspec_get_repository_without_git(temp_directory):
    """Test ProjSpec _get_repository without git config"""
    with patch("pathlib.Path.cwd", return_value=temp_directory):
        with patch("builtins.input") as mock_input:
            mock_input.side_effect = [
                "Test",
                "",  # No git config, should return empty
                "",
                "LIB",
                "37",
                "LIB",
                "",
                "",
                "",
                "",
            ]

            proj_spec = ProjSpec(None, None)

            assert proj_spec.repository == ""
