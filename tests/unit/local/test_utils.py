from makei.utils import make_include_dirs_absolute,decompose_filename
import json
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from makei.iproj_json import IProjJson
from makei.ibmi_json import IBMiJson
from makei.utils import objlib_to_path

# flake8: noqa: E501

def test_sanity():
    path = '/a/b/.logs/joblog.json'
    parameters = " some stuff at the begginning  aINCDIR ('PARAM1'   'PARAM2' ''PARAM3'' 'PARAM4' )and some stuff after   "
    expected = " some stuff at the begginning  aINCDIR ('/a/b/PARAM1' '/a/b/PARAM2' ''/a/b/PARAM3'' '/a/b/PARAM4')and some stuff after   "
    assert make_include_dirs_absolute(path, parameters) == expected


def test_empty_params():
    path = '/a/b/.logs/joblog.json'
    parameters = " INCDIR (''  '''')"
    expected = " INCDIR ('/a/b/' ''/a/b/'')"
    assert make_include_dirs_absolute(path, parameters) == expected


def test_longer_job_log_path():
    path = '/a/b/cd/efg/hijklmnop/.logs/joblog.json'
    parameters = " INCDIR( 'dir1'  ''dir2'')"
    expected = " INCDIR('/a/b/cd/efg/hijklmnop/dir1' ''/a/b/cd/efg/hijklmnop/dir2'')"
    assert make_include_dirs_absolute(path, parameters) == expected


def test_doesnt_modify_absolute_path():
    path = '/a/b/cd/efg/hijklmnop/.logs/joblog.json'
    parameters = " INCDIR( '/a/b/dir1'  ''dir2'')"
    expected = " INCDIR('/a/b/dir1' ''/a/b/cd/efg/hijklmnop/dir2'')"
    assert make_include_dirs_absolute(path, parameters) == expected


def test_doesnt_modify_absolute_path_with_double_quotes():
    path = '/a/b/cd/efg/hijklmnop/.logs/joblog.json'
    parameters = " INCDIR( ''/a/b/dir1''  ''dir2'')"
    expected = " INCDIR(''/a/b/dir1'' ''/a/b/cd/efg/hijklmnop/dir2'')"
    assert make_include_dirs_absolute(path, parameters) == expected


def test_no_preceding_path_before_logs():
    path = '/.logs/joblog.json'
    parameters = " INCDIR('dir2')"
    expected = " INCDIR('/dir2')"
    assert make_include_dirs_absolute(path, parameters) == expected


def test_joblob_not_found():
    path = '/a/b/cd/efg/hijklmnop/.logs/joblogs.json'
    parameters = " INCDIR( ''/a/b/dir1'' ''dir2'')"
    expected = " INCDIR( ''/a/b/dir1'' ''dir2'')"
    assert make_include_dirs_absolute(path, parameters) == expected


def test_decompose_filename():
    expected = ('custinfo1', None, 'PFSQL', '')
    assert decompose_filename("custinfo1.pfsql") == expected
    expected = ('CUSTINFO1', None, 'PFSQL', '')
    assert decompose_filename("CUSTINFO1.pfsql") == expected

def test_iproj_json_with_hash_in_objlib():
    """Test IProjJson with objlib containing #"""
    iproj_json = IProjJson(
        description="Test project with # in library",
        version="1.0.0",
        objlib="MYLIB#01",
        curlib="CURLIB#01"
    )
    
    assert iproj_json.objlib == "MYLIB#01"
    assert iproj_json.curlib == "CURLIB#01"

def test_iproj_json_with_hash_in_pre_usr_libl():
    """Test IProjJson with # in pre_usr_libl"""
    iproj_json = IProjJson(
        description="Test project",
        version="1.0.0",
        pre_usr_libl=["LIB#DEV", "LIB#TEST", "LIB#PROD"]
    )
    
    assert "LIB#DEV" in iproj_json.pre_usr_libl
    assert "LIB#TEST" in iproj_json.pre_usr_libl
    assert "LIB#PROD" in iproj_json.pre_usr_libl

def test_iproj_json_with_hash_in_post_usr_libl():
    """Test IProjJson with # in post_usr_libl"""
    iproj_json = IProjJson(
        description="Test project",
        version="1.0.0",
        post_usr_libl=["UTIL#LIB", "DATA#LIB"]
    )
    
    assert "UTIL#LIB" in iproj_json.post_usr_libl
    assert "DATA#LIB" in iproj_json.post_usr_libl


def test_ibmijson_with_hash_in_objlib():
    """Test IBMiJson with objlib containing #"""
    ibmi_json = IBMiJson.from_values(
        tgt_ccsid="37",
        objlib="BUILD#LIB",
        version="1.0.0"
    )
    
    assert ibmi_json.build["objlib"] == "BUILD#LIB"

def test_ibmijson_copy_with_hash_objlib():
    """Test copying IBMiJson with # in objlib"""
    original = IBMiJson.from_values(
        tgt_ccsid="37",
        objlib="ORIG#LIB",
        version="1.0.0"
    )
    
    copy = original.copy()
    
    assert copy.build["objlib"] == "ORIG#LIB"
    assert copy is not original

def test_ibmijson_inheritance_with_hash_objlib():
    """Test IBMiJson inheritance with # in objlib"""
    with TemporaryDirectory() as tmpdir:
        ibmi_json_path = Path(tmpdir) / ".ibmi.json"
        
        # Child only specifies tgtCcsid
        test_data = {
            "version": "1.0.0",
            "build": {
                "tgtCcsid": "1208"
            }
        }
        
        with ibmi_json_path.open("w") as f:
            json.dump(test_data, f)
        
        # Parent has objlib with #
        parent = IBMiJson.from_values("37", "PARENT#LIB")
        ibmi_json = IBMiJson.from_file(ibmi_json_path, parent)
        
        # Should inherit parent's objlib
        assert ibmi_json.build["objlib"] == "PARENT#LIB"
        # But use child's tgtCcsid
        assert ibmi_json.build["tgt_ccsid"] == "1208"

def test_library_with_hash_max_length():
    """Test library name at max length (10 chars) with #"""
    # IBM i library names max 10 characters
    lib_name = "ABCD#12345"  # 10 characters
    path = objlib_to_path(lib_name)
    
    assert lib_name.replace('#','\\#') in path
    assert len(lib_name) == 10

def test_curlib_with_hash():
    """Test current library with # character"""
    curlib = "CURRENT#LIB"
    escaped_curlib = curlib.replace('#', '\\#')
    path = objlib_to_path(curlib)
    
    assert path == f"/QSYS.LIB/{escaped_curlib}.LIB"


def test_library_with_hash_in_compile_command():
    """Test library with # in compile command context"""
    lib = "COMPILE#LIB"
    pgm = "TESTPGM.PGM"
    
    path = objlib_to_path(lib, pgm)
    
    # Simulate compile command path
    assert f"/QSYS.LIB/{lib}.LIB/{pgm}" == path


def test_library_list_with_mixed_hash_libraries():
    """Test library list with mix of # and regular libraries"""
    libraries = [
        "QSYS",
        "LIB#DEV",
        "QGPL",
        "TEST#LIB",
        "MYLIB",
        "PROD#LIB"
    ]
    
    paths = [objlib_to_path(lib) for lib in libraries]
    
    # Verify all paths are constructed correctly
    for i, path in enumerate(paths):
        if libraries[i] == "QSYS":
            continue  # QSYS is special case
        assert libraries[i].replace('#','\\#') in path
        assert path.endswith(".LIB")

def test_object_creation_in_hash_library():
    """Test object creation paths in library with #"""
    lib = "CREATE#LIB"
    objects = {
        "MYPGM": "PGM",
        "MYMOD": "MODULE",
        "MYSRV": "SRVPGM",
        "MYFILE": "FILE"
    }
    
    for obj_name, obj_type in objects.items():
        full_obj = f"{obj_name}.{obj_type}"
        path = objlib_to_path(lib, full_obj)
        
        assert lib in path
        assert obj_name in path
        assert obj_type in path
        assert "#" in path

def test_iproj_json_with_iaspobjlib_library():
    """Test IProjJson with iasp objlib"""
    iproj_json = IProjJson(
        description="Test project with IASP library in objlib",
        version="1.0.0",
        iasp="IASP1",
        objlib="IASPT1",
        curlib="IASPT1",
        set_ibm_i_env_cmd=["SETASPGRP ASPGRP(IASP1)"]
    )
    
    assert iproj_json.objlib == "IASPT1"
    assert iproj_json.curlib == "IASPT1"
    assert iproj_json.iasp == "IASP1"

def test_member_creation_with_iasp():
    """Test IProjJson with iasp library"""
    lib = "IASPT1"
    iasp = "IASP1"
    obj = "SAMREF.FILE"
    path = objlib_to_path(lib, obj,iasp)
    
    # Simulate compile command path
    assert f"/{iasp}/QSYS.LIB/{lib}.LIB/{obj}" == path

def test_object_creation_in_iasp_library():
    """Test object creation paths in iasp library"""
    lib = "IASPT1"
    objects = {
        "MYPGM": "PGM",
        "MYMOD": "MODULE",
        "MYSRV": "SRVPGM",
        "MYFILE": "FILE"
    }
    iasp = "IASP1"
    
    for obj_name, obj_type in objects.items():
        full_obj = f"{obj_name}.{obj_type}"
        path = objlib_to_path(lib, full_obj,iasp)
        
        assert lib in path
        assert obj_name in path
        assert obj_type in path
        assert iasp in path


def test_objlib_to_path_with_iasp_basic():
    """Test objlib_to_path with IASP - basic library path"""
    lib = "TESTLIB"
    iasp = "IASP1"
    path = objlib_to_path(lib, iasp=iasp)
    
    assert path == f"/{iasp}/QSYS.LIB/{lib}.LIB"
    assert iasp in path
    assert lib in path


def test_objlib_to_path_with_iasp_and_object():
    """Test objlib_to_path with IASP and object"""
    lib = "TESTLIB"
    obj = "TESTPGM.PGM"
    iasp = "IASP1"
    path = objlib_to_path(lib, obj, iasp)
    
    assert path == f"/{iasp}/QSYS.LIB/{lib}.LIB/{obj}"
    assert iasp in path
    assert lib in path
    assert obj in path


def test_objlib_to_path_without_iasp():
    """Test objlib_to_path without IASP (default behavior)"""
    lib = "TESTLIB"
    obj = "TESTPGM.PGM"
    path = objlib_to_path(lib, obj, iasp="")
    
    assert path == f"/QSYS.LIB/{lib}.LIB/{obj}"
    assert "/IASP" not in path


def test_objlib_to_path_with_iasp_and_hash():
    """Test objlib_to_path with both IASP and # in library name"""
    lib = "TEST#LIB"
    iasp = "IASP1"
    path = objlib_to_path(lib, iasp=iasp)
    
    # Should escape # and include IASP prefix
    escaped_lib = lib.replace('#', '\\#')
    assert path == f"/{iasp}/QSYS.LIB/{escaped_lib}.LIB"
    assert iasp in path
    assert "\\#" in path

def test_objlib_to_path_iasp_with_file_types():
    """Test objlib_to_path with IASP for different object types"""
    lib = "TESTLIB"
    iasp = "IASP1"
    objects = {
        "TESTPGM.PGM": "program",
        "TESTMOD.MODULE": "module",
        "TESTSRV.SRVPGM": "service program",
        "TESTFILE.FILE": "physical file",
        "TESTCMD.CMD": "command",
        "TESTMENU.MENU": "menu"
    }
    
    for obj, obj_desc in objects.items():
        path = objlib_to_path(lib, obj, iasp)
        assert path == f"/{iasp}/QSYS.LIB/{lib}.LIB/{obj}"
        assert iasp in path, f"IASP missing for {obj_desc}"
        assert obj in path, f"Object missing for {obj_desc}"


def test_objlib_to_path_iasp_empty_string():
    """Test objlib_to_path with empty IASP string (should behave like no IASP)"""
    lib = "TESTLIB"
    obj = "TESTPGM.PGM"
    iasp = ""
    path = objlib_to_path(lib, obj, iasp)
    
    assert path == f"{iasp}/QSYS.LIB/{lib}.LIB/{obj}"
    assert not path.startswith("//")  # No double slash


def test_objlib_to_path_iasp_with_source_files():
    """Test objlib_to_path with IASP for source files"""
    lib = "QRPGLESRC"
    member = "TESTPGM.MBR"
    iasp = "IASP1"
    
    # Source file path
    srcfile_path = objlib_to_path(lib, "QRPGLESRC.FILE", iasp)
    assert srcfile_path == f"/{iasp}/QSYS.LIB/{lib}.LIB/QRPGLESRC.FILE"
    
    # Member path would be constructed differently in actual use
    full_member_path = f"{srcfile_path}/{member}"
    assert iasp in full_member_path
    assert member in full_member_path


def test_objlib_to_path_iasp_library_list_scenario():
    """Test objlib_to_path with IASP in library list scenario"""
    iasp = "IASP1"
    libraries = ["QSYS", "QGPL", "TESTLIB1", "TESTLIB2", "PRODLIB"]
    
    paths = []
    for lib in libraries:
        if lib == "QSYS":
            # QSYS typically doesn't need full path in library list
            continue
        path = objlib_to_path(lib, iasp=iasp)
        paths.append(path)
        assert f"/{iasp}/QSYS.LIB/{lib}.LIB" == path
    
    assert len(paths) == len(libraries) - 1  # Excluding QSYS


def test_objlib_to_path_iasp_with_numeric_names():
    """Test objlib_to_path with IASP containing numbers"""
    lib = "LIB001"
    obj = "PGM001.PGM"
    iasp = "IASP001"
    
    path = objlib_to_path(lib, obj, iasp)
    assert path == f"/{iasp}/QSYS.LIB/{lib}.LIB/{obj}"
    assert "001" in path  # Verify numbers are preserved

