from makei.iproj_json import IProjJson
from tests.lib.const import DATA_PATH
from tests.lib.utils import assert_exit_with_code

iproj_json_dir = DATA_PATH / "iproj_jsons"


def test_iproj_json_from_file():
    # Test loading from a valid file
    iproj_json = IProjJson.from_file(iproj_json_dir / "valid.json")
    assert iproj_json.description == "Test project"
    assert iproj_json.version == "1.0.0"
    assert iproj_json.license == "MIT"
    assert iproj_json.repository == "https://github.com/user/project"
    assert iproj_json.include_path == ["libs"]
    assert iproj_json.objlib == "QGPL"
    assert iproj_json.curlib == "*CRTDFT"
    assert iproj_json.pre_usr_libl == ["QSYS"]
    assert iproj_json.post_usr_libl == ["QGPL"]
    assert iproj_json.set_ibm_i_env_cmd == ["CRTBNDRPG PGM(HELLO) SRCFILE(QCLLESRC)"]
    assert iproj_json.tgt_ccsid == "1208"
    assert iproj_json.extensions == {"custom_extension": {"key": "value"}}


def test_iproj_json_from_file_non_existent():
    # Test loading from a non-existent file
    assert_exit_with_code(1, IProjJson.from_file, iproj_json_dir / "non_existent.json")


def test_from_file():
    iproj_json = IProjJson.from_file((iproj_json_dir / "valid.json"))
    assert isinstance(iproj_json, IProjJson)


def test_iproj_json_to_dict():
    iproj_json = IProjJson(description="Test project",
                           version="1.0",
                           license="MIT",
                           repository="https://github.com/test/test",
                           include_path=["/path/to/include"],
                           objlib="QGPL",
                           curlib="QGPL",
                           pre_usr_libl=["MYLIB"],
                           post_usr_libl=["MYLIB"],
                           set_ibm_i_env_cmd=["system", "value(*yes)"],
                           tgt_ccsid="37",
                           extensions={"extension_key": "extension_value"})
    assert iproj_json.__dict__() == {
        "description": "Test project",
        "version": "1.0",
        "license": "MIT",
        "repository": "https://github.com/test/test",
        "includePath": ["/path/to/include"],
        "objlib": "QGPL",
        "curlib": "QGPL",
        "preUsrLibl": ["MYLIB"],
        "postUsrLibl": ["MYLIB"],
        "setIBMiEnvCmd": ["system", "value(*yes)"],
        "tgtCcsid": "37",
        "extensions": {"extension_key": "extension_value"}
    }
