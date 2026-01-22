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
