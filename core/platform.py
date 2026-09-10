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


def portable_path(path: str) -> str:
    """Normalize a link path for storage, using ~ instead of an absolute home path.

    Keeps stored entries portable across machines/users, so relocating the
    dotfiles folder or changing the home directory doesn't invalidate records:
        /home/foo/.config/nvim -> ~/.config/nvim
    Paths outside the home directory (and platform-specific forms such as
    %LOCALAPPDATA%/...) are returned normalized but otherwise untouched.
    """
    if not path:
        return path

    normalized = os.path.normpath(os.path.expandvars(os.path.expanduser(path)))
    home = os.path.normpath(os.path.expanduser('~'))

    if normalized == home:
        return '~'
    if normalized.startswith(home + os.sep):
        return '~' + normalized[len(home):]
    return normalized


def is_valid_platform(platform: str) -> bool:
    """Check if platform is supported."""
    return platform in SUPPORTED_PLATFORMS