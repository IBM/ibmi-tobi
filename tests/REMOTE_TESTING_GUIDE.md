# IBM i Remote Testing Guide

## Problem Overview

The tests for `test_crtfrmstmf.py`, `test_cvtsrcpf.py`, and `test_ibm_job.py` fail on non-IBM i systems (macOS, Linux, Windows) because they depend on `ibm_db_dbi`, which is only available on IBM i systems.

```
ModuleNotFoundError: No module named 'ibm_db_dbi'
```

## Solution Strategies

### Strategy 1: Remote Testing on IBM i System (Integration Testing)

**Purpose**: Run tests on actual IBM i system to verify real integration.

**How it works**:
- SSH into IBM i system
- Run tests directly on IBM i
- Tests use real `ibm_db_dbi` module
- Validates actual system behavior

**Prerequisites**:
1. Access to IBM i system (SSH credentials)
2. Python 3.9+ installed on IBM i
3. pytest installed on IBM i
4. Project code deployed to IBM i

### Strategy 2: Mock IBM i Dependencies (Local Development)

**Purpose**: Run tests locally on your development machine (macOS/Linux/Windows) by mocking IBM i-specific modules.

**How it works**:
- Create a `conftest.py` file that mocks `ibm_db_dbi` before tests run
- Tests run with mocked database connections
- Fast feedback during development
- No IBM i system required

**Implementation**:

1. **Create `tests/unit/conftest.py`** (already provided in this project)
2. **Run tests locally**:
   ```bash
   cd ibmi-tobi
   pytest tests/unit/test_crtfrmstmf.py tests/unit/test_cvtsrcpf.py tests/unit/test_ibm_job.py -v
   ```
---

**Implementation Steps**:

#### Step 1: Setup IBM i Environment

```bash
# SSH into IBM i system
ssh user@your-ibmi-system.com

# Install Python packages (if not already installed)
pip3 install pytest pytest-cov

# Clone or copy your project to IBM i
cd /home/youruser
git clone https://github.com/your-org/ibmi-tobi.git
cd ibmi-tobi
```

#### Step 2: Run Tests on IBM i

```bash
# Run specific tests
pytest tests/unit/test_crtfrmstmf.py tests/unit/test_cvtsrcpf.py tests/unit/test_ibm_job.py -v

# Run all tests
pytest tests/unit/ -v

# Run with coverage
pytest tests/unit/ --cov=src/makei --cov-report=html
```

---

## Recommended Setup for Your Project

### Phase 1: Local Development (Immediate)

1. **Use the provided `conftest.py`** to mock IBM i dependencies
2. **Mark integration tests** with pytest markers:
   ```python
   import pytest
   
   @pytest.mark.integration
   def test_real_ibmi_connection():
       # This test requires real IBM i
       pass
   ```

3. **Run local tests**:
   ```bash
   # Run all tests except integration
   pytest tests/unit/ -v -m "not integration"
   
   # Run only integration tests (will fail locally)
   pytest tests/unit/ -v -m integration
   ```

### Phase 2: Remote Testing Setup (When Available)

1. **Setup IBM i test environment**:
   - Create dedicated test library (e.g., `BOBTEST`)
   - Setup test user with appropriate permissions
   - Install Python and pytest

2. **Create remote test script**:
   ```bash
   #!/bin/bash
   # run_remote_tests.sh
   
   IBM_HOST="your-ibmi-system.com"
   IBM_USER="testuser"
   
   # Copy code to IBM i
   rsync -avz --exclude='.git' . ${IBM_USER}@${IBM_HOST}:/home/${IBM_USER}/ibmi-tobi/
   
   # Run tests remotely
   ssh ${IBM_USER}@${IBM_HOST} "cd /home/${IBM_USER}/ibmi-tobi && pytest tests/unit/ -v"
   ```

3. **Run remote tests**:
   ```bash
   chmod +x run_remote_tests.sh
   ./run_remote_tests.sh
   ```

### Phase 3: CI/CD Integration (Production)

1. **Setup GitHub Actions with self-hosted runner on IBM i**
2. **Configure automated testing on every commit**
3. **Generate coverage reports**

---

## Test Markers Reference

Add these markers to your tests:

```python
# tests/unit/test_ibm_job.py

import pytest

@pytest.mark.unit
def test_ibmjob_initialization():
    """Unit test - runs with mocks"""
    pass

@pytest.mark.integration
def test_ibmjob_real_connection():
    """Integration test - requires IBM i"""
    pass

@pytest.mark.slow
def test_large_dataset_processing():
    """Slow test - run separately"""
    pass
```

Run specific markers:
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

---

## Troubleshooting

### Issue: Tests still fail with mocked ibm_db_dbi

**Solution**: Ensure `conftest.py` is in the correct location:
```
tests/
  unit/
    conftest.py  ← Must be here
    test_ibm_job.py
    test_crtfrmstmf.py
```

### Issue: SSH connection to IBM i fails

**Solution**: Check network/VPN and SSH keys:
```bash
# Test SSH connection
ssh -v user@ibmi-system.com

# Setup SSH keys
ssh-copy-id user@ibmi-system.com
```

### Issue: Python not found on IBM i

**Solution**: Install Python via yum:
```bash
# On IBM i
yum install python39
yum install python39-pip
```
