import json
import os
from pathlib import Path
from typing import Dict, Optional, Any


DOTFILES_CONFIG = '.dotfiles.json'


class DotfilesConfig:
    def __init__(self, path: Path):
        self.path = path
        self.data: Dict[str, Any] = {}
        self._load()

    def _load(self):
        if self.path.exists():
            with open(self.path, 'r') as f:
                self.data = json.load(f)

    def save(self):
        with open(self.path, 'w') as f:
            json.dump(self.data, f, indent=2)

    @property
    def dotfiles_path(self) -> Optional[str]:
        return self.data.get('dotfiles_path')

    @dotfiles_path.setter
    def dotfiles_path(self, value: str):
        self.data['dotfiles_path'] = value

    @property
    def entries(self) -> Dict[str, Dict[str, str]]:
        return self.data.get('entries', {})

    def get_entry(self, name: str) -> Optional[Dict[str, str]]:
        return self.entries.get(name)

    def add_entry(self, name: str, platforms: Dict[str, str]):
        if 'entries' not in self.data:
            self.data['entries'] = {}
        self.data['entries'][name] = platforms

    def update_entry(self, name: str, platform: str, path: str):
        if name not in self.data.get('entries', {}):
            self.data['entries'][name] = {}
        self.data['entries'][name][platform] = path

    def remove_platform_from_entry(self, name: str, platform: str) -> bool:
        entry = self.get_entry(name)
        if entry and platform in entry:
            del entry[platform]
            return True
        return False

    def remove_entry(self, name: str) -> bool:
        if name in self.entries:
            del self.data['entries'][name]
            return True
        return False


def find_config_file(start_dir: Optional[Path] = None) -> Optional[Path]:
    """Find the .dotfiles.json config file by searching upward."""
    if start_dir is None:
        start_dir = Path.cwd()
    
    current = start_dir.resolve()
    while True:
        config_path = current / DOTFILES_CONFIG
        if config_path.exists():
            return config_path
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def load_config() -> DotfilesConfig:
    """Load the dotfiles config from the nearest config file."""
    config_path = find_config_file()
    if config_path is None:
        raise FileNotFoundError(
            f"No {DOTFILES_CONFIG} found. Run 'dotfiles init' first."
        )
    return DotfilesConfig(config_path)


def get_dotfiles_path() -> Path:
    """Get the dotfiles folder path from config."""
    config = load_config()
    dotfiles_path = config.dotfiles_path
    if dotfiles_path is None:
        raise ValueError("Dotfiles path not configured. Run 'dotfiles init' first.")
    return Path(os.path.expanduser(dotfiles_path))


def load_config_for_dir(dotfiles_dir: Optional[Path] = None) -> tuple:
    """Load config from a specific dotfiles directory.
    
    Args:
        dotfiles_dir: Optional path to dotfiles folder. If None, searches upward.
    
    Returns:
        tuple: (DotfilesConfig, dotfiles_dir Path)
    """
    if dotfiles_dir is not None:
        config_path = dotfiles_dir / DOTFILES_CONFIG
        if not config_path.exists():
            raise FileNotFoundError(
                f"No {DOTFILES_CONFIG} found in {dotfiles_dir}. Run 'dotfiles init' first."
            )
        return DotfilesConfig(config_path), dotfiles_dir
    
    config_path = find_config_file()
    if config_path is None:
        raise FileNotFoundError(
            f"No {DOTFILES_CONFIG} found. Run 'dotfiles init' first or use -d/--dotfiles-dir."
        )
    return DotfilesConfig(config_path), config_path.parent