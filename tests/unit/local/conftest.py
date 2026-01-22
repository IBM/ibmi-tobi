"""
Pytest configuration and fixtures for unit tests.

This file provides mocks for IBM i-specific modules that are not available
on non-IBM i systems (macOS, Linux, Windows).
"""

import sys
import pytest


# Mock ibm_db_dbi module before any imports
# This must happen before any test modules import makei modules
class MockConnection:
    """Mock database connection"""
    def cursor(self):
        return MockCursor()

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass


class MockCursor:
    """Mock database cursor"""
    def __init__(self):
        self.description = None
        self.rowcount = 0
        self._results = []

    def execute(self, sql, params=None):
        """Mock execute - returns success"""
        return True

    def executemany(self, sql, params_list):
        """Mock executemany"""
        return True

    def fetchone(self):
        """Mock fetchone"""
        if self._results:
            return self._results.pop(0)
        return None

    def fetchall(self):
        """Mock fetchall"""
        results = self._results
        self._results = []
        return results

    def fetchmany(self, size=1):
        """Mock fetchmany"""
        results = self._results[:size]
        self._results = self._results[size:]
        return results

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class MockIbmDbDbi:
    """Mock ibm_db_dbi module"""

    # Add Connection as a class attribute for type hints
    Connection = MockConnection

    @staticmethod
    def connect(*args, **kwargs):
        """Mock connect function"""
        return MockConnection()

    # Mock exception classes
    class Error(Exception):
        pass

    class DatabaseError(Error):
        pass

    class IntegrityError(DatabaseError):
        pass

    class ProgrammingError(DatabaseError):
        pass

    class OperationalError(DatabaseError):
        pass


# Install the mock before any imports
sys.modules['ibm_db_dbi'] = MockIbmDbDbi()


# Common fixtures
@pytest.fixture
def mock_ibm_connection():
    """Provide a mock IBM i database connection"""
    return MockConnection()


@pytest.fixture
def mock_ibm_cursor():
    """Provide a mock IBM i database cursor"""
    return MockCursor()


@pytest.fixture
def temp_directory(tmp_path):
    """Provide a temporary directory for testing"""
    return tmp_path


@pytest.fixture
def sample_iproj_json():
    """Provide sample iproj.json data"""
    return {
        "version": "0.0.1",
        "description": "Test project",
        "objlib": "TESTLIB",
        "curlib": "*CRTDFT",
        "preUsrlibl": [],
        "postUsrlibl": [],
        "setIBMiEnvCmd": [],
        "includePath": ["includes"],
        "repository": "https://github.com/test/repo"
    }


@pytest.fixture
def sample_ibmi_json():
    """Provide sample .ibmi.json data"""
    return {
        "version": "0.0.1",
        "build": {
            "tgtCcsid": "37",
            "objlib": "TESTLIB"
        }
    }


@pytest.fixture
def sample_rules_mk():
    """Provide sample Rules.mk content"""
    return """
# Sample Rules.mk
SUBDIRS = subdir1 subdir2

TEST.PGM: test.RPGLE
\t$(CRTBNDRPG) $(TGTCCSID) $(DBGVIEW)

%.MODULE: %.RPGLE
\t$(CRTRPGMOD) $(TGTCCSID) $(DBGVIEW)
"""


@pytest.fixture
def mock_joblog_data():
    """Provide sample joblog data"""
    return {
        "jobName": "TESTJOB",
        "jobUser": "TESTUSER",
        "jobNumber": "123456",
        "messages": [
            {
                "messageId": "CPF0001",
                "messageType": "INFO",
                "messageText": "Test message",
                "timestamp": "2024-01-01T12:00:00"
            }
        ]
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test (runs with mocks)"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (requires IBM i)"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location/name"""
    for item in items:
        # Auto-mark integration tests
        if "integration" in item.nodeid or "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        # Auto-mark unit tests
        elif "unit" in item.nodeid:
            item.add_marker(pytest.mark.unit)

# Made with Bob
