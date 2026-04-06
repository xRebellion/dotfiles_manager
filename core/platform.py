import os
import sys
from pathlib import Path
from typing import Optional

SUPPORTED_PLATFORMS = ['linux', 'windows', 'macos']


def get_current_platform() -> str:
    """Detect the current platform based on sys.platform."""
    if sys.platform.startswith('linux'):
        return 'linux'
    elif sys.platform == 'win32':
        return 'windows'
    elif sys.platform == 'darwin':
        return 'macos'
    else:
        raise ValueError(f"Unsupported platform: {sys.platform}")


def expand_path(path: str, resolve_symlinks: bool = False) -> Path:
    """Expand ~ and environment variables in path."""
    if not path:
        return Path()
    path = os.path.expandvars(path)
    path = os.path.expanduser(path)
    p = Path(path)
    if resolve_symlinks:
        return p.resolve()
    return p


def get_home_dir() -> Path:
    """Get the user's home directory."""
    return Path.home()


def normalize_path(path: str) -> str:
    """Normalize path to use forward slashes and expand special chars."""
    return os.path.normpath(os.path.expandvars(os.path.expanduser(path)))


def is_valid_platform(platform: str) -> bool:
    """Check if platform is supported."""
    return platform in SUPPORTED_PLATFORMS