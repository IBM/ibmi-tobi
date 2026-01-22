import os
import json
import pytest
from tempfile import NamedTemporaryFile
from makei.config import Config


@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing"""
    config_data = {
        "setting1": "value1",
        "setting2": "value2",
        "nested": {"key": "nested_value"},
    }

    with NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as f:
        json.dump(config_data, f)
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


def test_config_initialization(temp_config_file):
    """Test Config class initialization"""
    config = Config(temp_config_file)

    assert config.config_file == temp_config_file
    assert config._config is not None
    assert isinstance(config._config, dict)


def test_config_load_config(temp_config_file):
    """Test loading configuration from file"""
    config = Config(temp_config_file)
    loaded_config = config.get_config()

    assert loaded_config["setting1"] == "value1"
    assert loaded_config["setting2"] == "value2"
    assert loaded_config["nested"]["key"] == "nested_value"


def test_config_get_config(temp_config_file):
    """Test get_config method returns correct configuration"""
    config = Config(temp_config_file)
    config_data = config.get_config()

    assert "setting1" in config_data
    assert "setting2" in config_data
    assert config_data["setting1"] == "value1"


def test_config_update_config(temp_config_file):
    """Test updating configuration"""
    config = Config(temp_config_file)

    # Update with new values
    new_config = {"setting1": "updated_value1", "new_setting": "new_value"}
    config.update_config(new_config)

    # Verify updates
    updated_config = config.get_config()
    assert updated_config["setting1"] == "updated_value1"
    assert updated_config["new_setting"] == "new_value"
    assert updated_config["setting2"] == "value2"  # Original value preserved


def test_config_save_config(temp_config_file):
    """Test that configuration is saved to file"""
    config = Config(temp_config_file)

    # Update and save
    config.update_config({"test_key": "test_value"})

    # Read file directly to verify save
    with open(temp_config_file, "r", encoding="utf-8") as f:
        saved_data = json.load(f)

    assert saved_data["test_key"] == "test_value"


def test_config_with_empty_file():
    """Test Config with an empty JSON file"""
    with NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as f:
        json.dump({}, f)
        temp_path = f.name

    try:
        config = Config(temp_path)
        assert config.get_config() == {}
    finally:
        os.unlink(temp_path)


def test_config_update_preserves_existing_keys(temp_config_file):
    """Test that update_config preserves keys not in the update"""
    config = Config(temp_config_file)
    original_config = config.get_config().copy()

    # Update only one key
    config.update_config({"setting1": "modified"})

    updated_config = config.get_config()
    assert updated_config["setting1"] == "modified"
    assert updated_config["setting2"] == original_config["setting2"]
    assert updated_config["nested"] == original_config["nested"]


def test_config_multiple_updates(temp_config_file):
    """Test multiple sequential updates"""
    config = Config(temp_config_file)

    config.update_config({"update1": "first"})
    config.update_config({"update2": "second"})
    config.update_config({"update3": "third"})

    final_config = config.get_config()
    assert final_config["update1"] == "first"
    assert final_config["update2"] == "second"
    assert final_config["update3"] == "third"
