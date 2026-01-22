import json
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from makei.ibmi_json import IBMiJson
from makei.const import DEFAULT_TGT_CCSID, DEFAULT_OBJLIB


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing"""
    with TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_ibmijson_initialization():
    """Test IBMiJson initialization"""
    ibmi_json = IBMiJson(version="0.0.1", build={"tgt_ccsid": "37", "objlib": "MYLIB"})

    assert ibmi_json.version == "0.0.1"
    assert ibmi_json.build["tgt_ccsid"] == "37"
    assert ibmi_json.build["objlib"] == "MYLIB"


def test_ibmijson_from_values():
    """Test IBMiJson.from_values class method"""
    ibmi_json = IBMiJson.from_values(tgt_ccsid="37", objlib="TESTLIB", version="1.0.0")

    assert ibmi_json.version == "1.0.0"
    assert ibmi_json.build["tgt_ccsid"] == "37"
    assert ibmi_json.build["objlib"] == "TESTLIB"


def test_ibmijson_from_values_without_version():
    """Test IBMiJson.from_values without version"""
    ibmi_json = IBMiJson.from_values(tgt_ccsid="37", objlib="TESTLIB")

    assert ibmi_json.version is None
    assert ibmi_json.build["tgt_ccsid"] == "37"
    assert ibmi_json.build["objlib"] == "TESTLIB"


def test_ibmijson_from_file_existing(temp_directory):
    """Test IBMiJson.from_file with existing file"""
    # Create a test .ibmi.json file
    ibmi_json_path = temp_directory / ".ibmi.json"
    test_data = {"version": "0.0.1", "build": {"tgtCcsid": "37", "objlib": "MYLIB"}}

    with ibmi_json_path.open("w") as f:
        json.dump(test_data, f)

    # Create parent IBMiJson
    parent = IBMiJson.from_values("1208", "*CURLIB")

    # Load from file
    ibmi_json = IBMiJson.from_file(ibmi_json_path, parent)

    assert ibmi_json.version == "0.0.1"
    assert ibmi_json.build["tgt_ccsid"] == "37"
    assert ibmi_json.build["objlib"] == "MYLIB"


def test_ibmijson_from_file_nonexistent(temp_directory):
    """Test IBMiJson.from_file with non-existent file"""
    ibmi_json_path = temp_directory / ".ibmi.json"

    # Create parent IBMiJson
    parent = IBMiJson.from_values("1208", "PARENTLIB", "1.0.0")

    # Load from non-existent file should return copy of parent
    ibmi_json = IBMiJson.from_file(ibmi_json_path, parent)

    assert ibmi_json.version == parent.version
    assert ibmi_json.build["tgt_ccsid"] == parent.build["tgt_ccsid"]
    assert ibmi_json.build["objlib"] == parent.build["objlib"]


def test_ibmijson_from_file_inherits_from_parent(temp_directory):
    """Test IBMiJson.from_file inherits missing values from parent"""
    # Create a test .ibmi.json file with only tgtCcsid
    ibmi_json_path = temp_directory / ".ibmi.json"
    test_data = {"version": "0.0.1", "build": {"tgtCcsid": "37"}}

    with ibmi_json_path.open("w") as f:
        json.dump(test_data, f)

    # Create parent with objlib
    parent = IBMiJson.from_values("1208", "PARENTLIB")

    # Load from file
    ibmi_json = IBMiJson.from_file(ibmi_json_path, parent)

    assert ibmi_json.build["tgt_ccsid"] == "37"  # From file
    assert ibmi_json.build["objlib"] == "PARENTLIB"  # From parent


def test_ibmijson_from_file_with_variable_substitution(temp_directory, monkeypatch):
    """Test IBMiJson.from_file with variable substitution in objlib"""
    ibmi_json_path = temp_directory / ".ibmi.json"
    test_data = {"version": "0.0.1", "build": {"objlib": "&OBJLIB"}}

    with ibmi_json_path.open("w") as f:
        json.dump(test_data, f)

    # Set environment variable to avoid sys.exit(1)
    monkeypatch.setenv("OBJLIB", "TESTLIB")

    parent = IBMiJson.from_values("37", "PARENTLIB")

    # Load from file - parse_all_variables should be called
    ibmi_json = IBMiJson.from_file(ibmi_json_path, parent)

    # The objlib should be processed by parse_all_variables
    assert "objlib" in ibmi_json.build
    assert ibmi_json.build["objlib"] == "TESTLIB"


def test_ibmijson_dict_with_custom_values():
    """Test __dict__ method with custom values"""
    ibmi_json = IBMiJson(version="1.0.0", build={"tgt_ccsid": "37", "objlib": "MYLIB"})

    result = ibmi_json.__dict__()

    assert result is not None
    assert result["version"] == "1.0.0"
    assert result["build"]["tgtCcsid"] == "37"
    assert result["build"]["objlib"] == "MYLIB"


def test_ibmijson_dict_with_default_values():
    """Test __dict__ method with default values"""
    ibmi_json = IBMiJson(
        version="1.0.0",
        build={"tgt_ccsid": DEFAULT_TGT_CCSID, "objlib": DEFAULT_OBJLIB},
    )

    result = ibmi_json.__dict__()

    # Default values should not be included in build
    assert result is None or "build" not in result or len(result.get("build", {})) == 0


def test_ibmijson_dict_with_empty_values():
    """Test __dict__ method with empty values"""
    ibmi_json = IBMiJson(version="1.0.0", build={"tgt_ccsid": "", "objlib": ""})

    result = ibmi_json.__dict__()

    # Empty values should not be included
    assert result is None or "build" not in result or len(result.get("build", {})) == 0


def test_ibmijson_dict_with_none_values():
    """Test __dict__ method with None values"""
    ibmi_json = IBMiJson(version="1.0.0", build={"tgt_ccsid": None, "objlib": None})

    result = ibmi_json.__dict__()

    # None values should not be included
    assert result is None or "build" not in result or len(result.get("build", {})) == 0


def test_ibmijson_dict_with_mixed_values():
    """Test __dict__ method with mix of default and custom values"""
    ibmi_json = IBMiJson(
        version="1.0.0", build={"tgt_ccsid": "37", "objlib": DEFAULT_OBJLIB}
    )

    result = ibmi_json.__dict__()

    assert result is not None
    assert "build" in result
    assert result["build"]["tgtCcsid"] == "37"
    # Default objlib should not be included
    assert "objlib" not in result["build"]


def test_ibmijson_copy():
    """Test copy method"""
    original = IBMiJson(version="1.0.0", build={"tgt_ccsid": "37", "objlib": "MYLIB"})

    copy = original.copy()

    assert copy.version == original.version
    assert copy.build["tgt_ccsid"] == original.build["tgt_ccsid"]
    assert copy.build["objlib"] == original.build["objlib"]

    # Verify it's a different object
    assert copy is not original
    assert copy.build is not original.build


def test_ibmijson_copy_independence():
    """Test that copy is independent of original"""
    original = IBMiJson(version="1.0.0", build={"tgt_ccsid": "37", "objlib": "MYLIB"})

    copy = original.copy()

    # Modify copy
    copy.build["tgt_ccsid"] = "1208"
    copy.build["objlib"] = "OTHERLIB"

    # Original should be unchanged (now that copy() does deep copy)
    assert original.build["tgt_ccsid"] == "37"
    assert original.build["objlib"] == "MYLIB"


def test_ibmijson_save(temp_directory):
    """Test save method"""
    ibmi_json = IBMiJson(version="1.0.0", build={"tgt_ccsid": "37", "objlib": "MYLIB"})

    save_path = temp_directory / ".ibmi.json"
    ibmi_json.save(str(save_path))

    # Verify file was created
    assert save_path.exists()

    # Verify content
    with save_path.open("r") as f:
        data = json.load(f)

    assert data["version"] == "1.0.0"
    assert data["build"]["tgtCcsid"] == "37"
    assert data["build"]["objlib"] == "MYLIB"


def test_ibmijson_save_creates_file(temp_directory):
    """Test save method creates file if it doesn't exist"""
    ibmi_json = IBMiJson(version="1.0.0", build={"tgt_ccsid": "37", "objlib": "MYLIB"})

    save_path = temp_directory / "new_file.json"

    # File should not exist yet
    assert not save_path.exists()

    ibmi_json.save(str(save_path))

    # File should now exist
    assert save_path.exists()


def test_ibmijson_save_overwrites_existing(temp_directory):
    """Test save method overwrites existing file"""
    save_path = temp_directory / ".ibmi.json"

    # Create initial file
    initial_data = {"version": "0.0.1", "build": {}}
    with save_path.open("w") as f:
        json.dump(initial_data, f)

    # Save new data
    ibmi_json = IBMiJson(version="1.0.0", build={"tgt_ccsid": "37", "objlib": "MYLIB"})
    ibmi_json.save(str(save_path))

    # Verify file was overwritten
    with save_path.open("r") as f:
        data = json.load(f)

    assert data["version"] == "1.0.0"
    assert data["build"]["tgtCcsid"] == "37"


def test_ibmijson_roundtrip(temp_directory):
    """Test saving and loading IBMiJson"""
    # Create and save
    original = IBMiJson(version="1.0.0", build={"tgt_ccsid": "37", "objlib": "MYLIB"})

    save_path = temp_directory / ".ibmi.json"
    original.save(str(save_path))

    # Load back
    parent = IBMiJson.from_values("1208", "*CURLIB")
    loaded = IBMiJson.from_file(save_path, parent)

    # Verify values match
    assert loaded.version == original.version
    assert loaded.build["tgt_ccsid"] == original.build["tgt_ccsid"]
    assert loaded.build["objlib"] == original.build["objlib"]


def test_ibmijson_from_file_without_version(temp_directory):
    """Test IBMiJson.from_file with file missing version"""
    ibmi_json_path = temp_directory / ".ibmi.json"
    test_data = {"build": {"tgtCcsid": "37", "objlib": "MYLIB"}}

    with ibmi_json_path.open("w") as f:
        json.dump(test_data, f)

    parent = IBMiJson.from_values("1208", "PARENTLIB")
    ibmi_json = IBMiJson.from_file(ibmi_json_path, parent)

    assert ibmi_json.version is None
    assert ibmi_json.build["tgt_ccsid"] == "37"
    assert ibmi_json.build["objlib"] == "MYLIB"


def test_ibmijson_from_file_without_build(temp_directory):
    """Test IBMiJson.from_file with file missing build section"""
    ibmi_json_path = temp_directory / ".ibmi.json"
    test_data = {"version": "1.0.0"}

    with ibmi_json_path.open("w") as f:
        json.dump(test_data, f)

    parent = IBMiJson.from_values("37", "PARENTLIB", "0.0.1")
    ibmi_json = IBMiJson.from_file(ibmi_json_path, parent)

    # Should inherit from parent when build section is missing
    assert ibmi_json.version == "1.0.0"
