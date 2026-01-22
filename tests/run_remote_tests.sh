#!/bin/bash

###############################################################################
# Remote Test Runner for IBM i
#
# This script helps run tests on an IBM i system where ibm_db_dbi is available.
# It handles code synchronization and remote test execution.
#
# Usage:
#   ./run_remote_tests.sh [options]
#
# Options:
#   -h, --host HOST       IBM i hostname or IP address
#   -u, --user USER       IBM i username
#   -p, --path PATH       Remote path on IBM i (default: ~/ibmi-tobi)
#   -t, --tests TESTS     Specific tests to run (default: all)
#   -v, --verbose         Verbose output
#   --sync-only           Only sync code, don't run tests
#   --test-only           Only run tests, don't sync code
#   --help                Show this help message
#
# Examples:
#   # Run all tests
#   ./run_remote_tests.sh -h ibmi.example.com -u testuser
#
#   # Run specific tests
#   ./run_remote_tests.sh -h ibmi.example.com -u testuser -t "tests/unit/test_ibm_job.py"
#
#   # Sync code only
#   ./run_remote_tests.sh -h ibmi.example.com -u testuser --sync-only
#
###############################################################################

set -e  # Exit on error

# Default values
IBM_HOST=""
IBM_USER=""
REMOTE_PATH="~/ibmi-tobi"
TESTS="tests/unit/"
VERBOSE=""
SYNC_ONLY=false
TEST_ONLY=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to show usage
show_usage() {
    grep "^#" "$0" | grep -v "#!/bin/bash" | sed 's/^# //' | sed 's/^#//'
    exit 0
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--host)
            IBM_HOST="$2"
            shift 2
            ;;
        -u|--user)
            IBM_USER="$2"
            shift 2
            ;;
        -p|--path)
            REMOTE_PATH="$2"
            shift 2
            ;;
        -t|--tests)
            TESTS="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        --sync-only)
            SYNC_ONLY=true
            shift
            ;;
        --test-only)
            TEST_ONLY=true
            shift
            ;;
        --help)
            show_usage
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            ;;
    esac
done

# Validate required parameters
if [ -z "$IBM_HOST" ]; then
    print_error "IBM i host is required. Use -h or --host option."
    exit 1
fi

if [ -z "$IBM_USER" ]; then
    print_error "IBM i user is required. Use -u or --user option."
    exit 1
fi

# Test SSH connection
print_info "Testing SSH connection to ${IBM_USER}@${IBM_HOST}..."
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes "${IBM_USER}@${IBM_HOST}" "echo 'Connection successful'" > /dev/null 2>&1; then
    print_error "Cannot connect to ${IBM_USER}@${IBM_HOST}"
    print_info "Please ensure:"
    print_info "  1. SSH keys are set up (run: ssh-copy-id ${IBM_USER}@${IBM_HOST})"
    print_info "  2. You have network access to the IBM i system"
    print_info "  3. The hostname and username are correct"
    exit 1
fi
print_success "SSH connection successful"

# Sync code to IBM i (unless --test-only)
if [ "$TEST_ONLY" = false ]; then
    print_info "Syncing code to ${IBM_USER}@${IBM_HOST}:${REMOTE_PATH}..."
    
    # Create remote directory if it doesn't exist
    ssh "${IBM_USER}@${IBM_HOST}" "mkdir -p ${REMOTE_PATH}"
    
    # Sync code using rsync
    rsync -avz ${VERBOSE} \
        --exclude='.git' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.pytest_cache' \
        --exclude='.vscode' \
        --exclude='*.egg-info' \
        --exclude='build/' \
        --exclude='dist/' \
        --exclude='.DS_Store' \
        ./ "${IBM_USER}@${IBM_HOST}:${REMOTE_PATH}/"
    
    print_success "Code synced successfully"
fi

# Exit if sync-only
if [ "$SYNC_ONLY" = true ]; then
    print_info "Sync complete. Exiting (--sync-only specified)."
    exit 0
fi

# Run tests on IBM i
print_info "Running tests on IBM i..."
print_info "Tests: ${TESTS}"

# Build the remote command
REMOTE_CMD="cd ${REMOTE_PATH} && "

# Check if pytest is installed
REMOTE_CMD+="if ! command -v pytest &> /dev/null; then "
REMOTE_CMD+="echo 'ERROR: pytest not found. Installing...'; "
REMOTE_CMD+="pip3 install pytest pytest-cov; "
REMOTE_CMD+="fi && "

# Run the tests
REMOTE_CMD+="pytest ${TESTS} ${VERBOSE} --tb=short"

# Execute remote command
print_info "Executing: ${REMOTE_CMD}"
echo ""

if ssh -t "${IBM_USER}@${IBM_HOST}" "${REMOTE_CMD}"; then
    echo ""
    print_success "Tests completed successfully!"
    exit 0
else
    echo ""
    print_error "Tests failed!"
    exit 1
fi

# Made with Bob
