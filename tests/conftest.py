import os
import sys
import tempfile
import shutil
import pytest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.link_records import DotfilesConfig, DOTFILES_CONFIG


@pytest.fixture
def tmp_dotfiles_dir(tmp_path):
    """Create a temporary directory initialized as dotfiles folder."""
    dotfiles_dir = tmp_path / "dotfiles"
    dotfiles_dir.mkdir()
    
    config_path = dotfiles_dir / DOTFILES_CONFIG
    config = DotfilesConfig(config_path)
    config.dotfiles_path = str(dotfiles_dir)
    config.save()
    
    yield dotfiles_dir
    
    shutil.rmtree(dotfiles_dir, ignore_errors=True)


@pytest.fixture
def tmp_uninitialized_dir(tmp_path):
    """Create a temporary directory that is not initialized."""
    test_dir = tmp_path / "test"
    test_dir.mkdir()
    yield test_dir
    shutil.rmtree(test_dir, ignore_errors=True)


@pytest.fixture
def sample_entry(tmp_dotfiles_dir):
    """Create a sample entry in the dotfiles config."""
    config_path = tmp_dotfiles_dir / DOTFILES_CONFIG
    config = DotfilesConfig(config_path)
    config.add_entry("test_entry", {
        "linux": "~/.config/test",
        "windows": "%LOCALAPPDATA%/test"
    })
    config.save()
    return tmp_dotfiles_dir


@pytest.fixture
def mock_linux_platform():
    """Mock Linux platform detection."""
    with patch.object(sys, 'platform', 'linux'):
        yield


@pytest.fixture
def mock_windows_platform():
    """Mock Windows platform detection."""
    with patch.object(sys, 'platform', 'win32'):
        yield


@pytest.fixture
def mock_macos_platform():
    """Mock macOS platform detection."""
    with patch.object(sys, 'platform', 'darwin'):
        yield


@pytest.fixture
def create_test_file(tmp_path):
    """Create a test file in a given directory."""
    def _create_file(filename, content="test content"):
        file_path = tmp_path / filename
        file_path.write_text(content)
        return file_path
    return _create_file


@pytest.fixture
def create_test_dir(tmp_path):
    """Create a test directory with files."""
    def _create_dir(dirname, file_count=3):
        dir_path = tmp_path / dirname
        dir_path.mkdir()
        for i in range(file_count):
            (dir_path / f"file{i}.conf").write_text(f"content {i}")
        return dir_path
    return _create_dir