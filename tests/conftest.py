"""Shared fixtures across multiple test files."""

import pytest

from run_application import RunApplication

SOURCE_FOLDER = 'src'


@pytest.fixture
def app() -> RunApplication:
    """Class to run the application on the command line."""
    runapp = RunApplication('hex.py')
    runapp.source_folder = SOURCE_FOLDER
    return runapp

@pytest.fixture(params=['-a', '--overwrite-start-address'])
def opt_overwrite_start_address(request) -> str:
    """Test all overwrite start address option variations."""
    return request.param

@pytest.fixture(params=['-B', '--binary'])
def opt_binary(request) -> str:
    """Test all binary option variations."""
    return request.param

@pytest.fixture(params=['-c', '--record-count'])
def opt_record_count(request) -> str:
    """Test all record count option variations."""
    return request.param

@pytest.fixture(params=['-d', '--overwrite-data'])
def opt_overwrite_data(request) -> str:
    """Test all overwrite data option variations."""
    return request.param

@pytest.fixture(params=['-f', '--fill'])
def opt_fill(request) -> str:
    """Test all fill option variations."""
    return request.param

@pytest.fixture(params=['-h', '--help'])
def opt_help(request) -> str:
    """Test all help option variations."""
    return request.param

@pytest.fixture(params=['-I', '--ihex'])
def opt_ihex(request) -> str:
    """Test all ihex option variations."""
    return request.param

@pytest.fixture(params=['-k', '--keep'])
def opt_keep(request) -> str:
    """Test all keep option variations."""
    return request.param

@pytest.fixture(params=['-o', '--output'])
def opt_output(request) -> str:
    """Test all output option variations."""
    return request.param

@pytest.fixture(params=['-r', '--remove'])
def opt_remove(request) -> str:
    """Test all remove option variations."""
    return request.param

@pytest.fixture(params=['-S', '--srec'])
def opt_srec(request) -> str:
    """Test all srec option variations."""
    return request.param

@pytest.fixture(params=['-v', '--write-value'])
def opt_write_value(request) -> str:
    """Test all write value option variations."""
    return request.param

@pytest.fixture(params=['-w', '--write-data'])
def opt_write_data(request) -> str:
    """Test all write data option variations."""
    return request.param
