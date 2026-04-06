import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional


BACKUP_FOLDER = '.dotfiles_backup'


def get_backup_dir() -> Path:
    """Get the backup directory path."""
    return Path(BACKUP_FOLDER)


def create_backup_timestamp() -> str:
    """Create a timestamp string for backup folder."""
    return datetime.now().strftime('%Y%m%d_%H%M%S')


def create_backup(source: Path, name: str, platform: str) -> Optional[Path]:
    """Create a backup of a file or folder."""
    if not source.exists():
        return None
    
    backup_dir = get_backup_dir() / create_backup_timestamp()
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    backup_path = backup_dir / f"{name}_{platform}"
    
    if source.is_symlink():
        target = source.resolve()
        shutil.copy2(target, backup_path)
    elif source.is_dir():
        shutil.copytree(source, backup_path, symlinks=True)
    else:
        shutil.copy2(source, backup_path)
    
    return backup_path


def list_backups() -> list:
    """List all backup folders."""
    backup_dir = get_backup_dir()
    if not backup_dir.exists():
        return []
    
    backups = []
    for item in sorted(backup_dir.iterdir(), reverse=True):
        if item.is_dir():
            backups.append(item)
    return backups


def clean_old_backups(keep_count: int = 5):
    """Remove old backups, keeping only the most recent ones."""
    backups = list_backups()
    if len(backups) <= keep_count:
        return
    
    for backup in backups[keep_count:]:
        shutil.rmtree(backup)