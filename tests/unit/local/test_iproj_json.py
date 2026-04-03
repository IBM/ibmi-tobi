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
    assert iproj_json.set_ibm_i_env_cmd == ["SETASPGRP ASPGRP(IASP1)", "CRTBNDRPG PGM(HELLO) SRCFILE(QCLLESRC)"]
    assert iproj_json.iasp == "IASP1"
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
                           set_ibm_i_env_cmd=["SETASPGRP ASPGRP(IASP1)", "system", "value(*yes)"],
                           iasp="IASP1",
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
        "setIBMiEnvCmd": ["SETASPGRP ASPGRP(IASP1)", "system", "value(*yes)"],
        "iasp": "IASP1",
        "tgtCcsid": "37",
        "extensions": {"extension_key": "extension_value"}
    }


def test_iproj_json_iasp_without_setaspgrp_fails():
    """Test that providing iasp without SETASPGRP command in setIBMiEnvCmd fails"""
    # This should exit with code 1 because iasp is set but setIBMiEnvCmd doesn't contain SETASPGRP
    assert_exit_with_code(
        1,
        IProjJson,
        description="Test project",
        iasp="IASP1",
        set_ibm_i_env_cmd=["SOME_OTHER_CMD"]
    )


def test_iproj_json_iasp_with_setaspgrp_succeeds():
    """Test that providing iasp with SETASPGRP command in setIBMiEnvCmd succeeds"""
    # This should succeed because iasp is set and setIBMiEnvCmd contains SETASPGRP
    iproj_json = IProjJson(
        description="Test project",
        iasp="IASP1",
        set_ibm_i_env_cmd=["SETASPGRP ASPGRP(IASP1)"]
    )
    assert iproj_json.iasp == "IASP1"
    assert "SETASPGRP ASPGRP(IASP1)" in iproj_json.set_ibm_i_env_cmd


def test_iproj_json_no_iasp_no_setaspgrp_succeeds():
    """Test that not providing iasp works fine even without SETASPGRP"""
    # This should succeed because iasp is not set, so no validation is needed
    iproj_json = IProjJson(
        description="Test project",
        set_ibm_i_env_cmd=["SOME_OTHER_CMD"]
    )
    assert iproj_json.iasp == ""
    assert iproj_json.set_ibm_i_env_cmd == ["SOME_OTHER_CMD"]


def test_iproj_json_iasp_case_insensitive_setaspgrp():
    """Test that SETASPGRP check is case-insensitive"""
    # This should succeed with lowercase setaspgrp
    iproj_json = IProjJson(
        description="Test project",
        iasp="IASP1",
        set_ibm_i_env_cmd=["setaspgrp aspgrp(iasp1)"]
    )
    assert iproj_json.iasp == "IASP1"


def test_iproj_json_setaspgrp_without_iasp_fails():
    """Test that providing SETASPGRP command without iasp fails"""
    # This should exit with code 1 because SETASPGRP is set but iasp is not
    assert_exit_with_code(
        1,
        IProjJson,
        description="Test project",
        set_ibm_i_env_cmd=["SETASPGRP ASPGRP(IASP1)"]
    )
