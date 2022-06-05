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
