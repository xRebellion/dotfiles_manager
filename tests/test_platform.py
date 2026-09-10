import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.platform import (
    get_current_platform,
    expand_path,
    normalize_path,
    portable_path,
    get_home_dir,
    is_valid_platform,
    SUPPORTED_PLATFORMS
)


class TestGetCurrentPlatform:
    def test_linux_platform(self):
        with patch.object(sys, 'platform', 'linux'):
            assert get_current_platform() == 'linux'
    
    def test_linux_64_platform(self):
        with patch.object(sys, 'platform', 'linux2'):
            assert get_current_platform() == 'linux'
    
    def test_windows_platform(self):
        with patch.object(sys, 'platform', 'win32'):
            assert get_current_platform() == 'windows'
    
    def test_macos_platform(self):
        with patch.object(sys, 'platform', 'darwin'):
            assert get_current_platform() == 'macos'
    
    def test_unsupported_platform(self):
        with patch.object(sys, 'platform', 'freebsd'):
            with pytest.raises(ValueError, match="Unsupported platform"):
                get_current_platform()


class TestExpandPath:
    def test_expand_tilde(self):
        path = expand_path("~")
        assert path == get_home_dir()
    
    def test_expand_tilde_with_subpath(self):
        path = expand_path("~/.config")
        assert str(path).startswith(str(get_home_dir()))
        assert ".config" in str(path)
    
    def test_expand_absolute_path(self):
        path = expand_path("/usr/bin")
        assert path == Path("/usr/bin")
    
    def test_expand_empty_path(self):
        path = expand_path("")
        assert path == Path()


class TestNormalizePath:
    def test_normalize_simple_path(self):
        result = normalize_path("~/.config/nvim")
        assert result is not None
        assert "~" not in result
    
    def test_normalize_windows_env_var(self):
        result = normalize_path("%LOCALAPPDATA%/nvim")
        assert "%LOCALAPPDATA%" not in result or "LOCALAPPDATA" in result


class TestPortablePath:
    def test_home_path_becomes_tilde(self):
        result = portable_path(str(get_home_dir() / ".config" / "nvim"))
        assert result == "~/.config/nvim"

    def test_tilde_path_is_idempotent(self):
        assert portable_path("~/.config/nvim") == "~/.config/nvim"

    def test_home_itself_becomes_tilde(self):
        assert portable_path(str(get_home_dir())) == "~"

    def test_sibling_of_home_is_not_rewritten(self):
        sibling = str(get_home_dir().parent / (get_home_dir().name + "-other") / "x")
        assert portable_path(sibling) == sibling

    def test_path_outside_home_is_unchanged(self):
        assert portable_path("/usr/bin") == "/usr/bin"

    def test_windows_env_var_is_preserved(self):
        assert portable_path("%LOCALAPPDATA%/nvim") == "%LOCALAPPDATA%/nvim"

    def test_empty_path_is_unchanged(self):
        assert portable_path("") == ""


class TestGetHomeDir:
    def test_returns_home_directory(self):
        home = get_home_dir()
        assert home.is_dir()
        assert home.exists()


class TestIsValidPlatform:
    def test_valid_linux(self):
        assert is_valid_platform('linux') is True
    
    def test_valid_windows(self):
        assert is_valid_platform('windows') is True
    
    def test_valid_macos(self):
        assert is_valid_platform('macos') is True
    
    def test_invalid_platform(self):
        assert is_valid_platform('freebsd') is False
        assert is_valid_platform('unknown') is False
    
    def test_supported_platforms_list(self):
        assert 'linux' in SUPPORTED_PLATFORMS
        assert 'windows' in SUPPORTED_PLATFORMS
        assert 'macos' in SUPPORTED_PLATFORMS