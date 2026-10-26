import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Tuple

from .platform import get_current_platform, expand_path, portable_path
from .link_records import DotfilesConfig, load_config_for_dir, DOTFILES_CONFIG
from .backup import create_backup


def init(dotfiles_path: Optional[Path] = None):
    """Initialize the current directory as a dotfiles folder."""
    if dotfiles_path is None:
        dotfiles_path = Path.cwd()
    
    config_path = dotfiles_path / DOTFILES_CONFIG
    
    if config_path.exists():
        print(f"Error: {DOTFILES_CONFIG} already exists in {dotfiles_path}")
        print("This directory is already initialized as a dotfiles folder.")
        sys.exit(1)
    
    config = DotfilesConfig(config_path)
    config.dotfiles_path = portable_path(str(dotfiles_path))
    config.save()
    
    print(f"Initialized dotfiles folder at: {dotfiles_path}")
    print(f"Run 'dotfiles add <path>' to start adding dotfiles.")


def add(source_path: str, platforms: Dict[str, str], dotfiles_dir: Path = None):
    """Add a file/folder to the dotfiles."""
    config, dotfiles_dir = load_config_for_dir(dotfiles_dir)
    
    source = expand_path(source_path)
    
    if not source.exists():
        print(f"Error: Path does not exist: {source}")
        sys.exit(1)
    
    name = source.name
    dest = dotfiles_dir / name
    
    source_is_in_dotfiles = dotfiles_dir.resolve() in source.resolve().parents
    
    if source_is_in_dotfiles:
        name = str(source.resolve().relative_to(dotfiles_dir.resolve()))
        if not platforms:
            current_platform = get_current_platform()
            platforms[current_platform] = portable_path(str(source.resolve()))
        config.add_entry(name, platforms)
        config.save()
        print(f"Added '{name}' to dotfiles folder")
        print(f"Run 'dotfiles sync' to create the link")
        return
    else:
        source_path_obj = Path(source_path).expanduser()
        if source_path_obj.is_absolute():
            try:
                relative_to_home = source_path_obj.relative_to(Path.home())
                name = str(relative_to_home)
            except ValueError:
                name = source_path_obj.name
        else:
            name = str(source_path_obj)
        
        dest = dotfiles_dir / name
        if dest.exists():
            print(f"Error: '{name}' already exists in dotfiles folder")
            msg = f"Use 'dotfiles record {source_path}' to record existing symlink, or 'dotfiles add {source_path} -t <path>' to specify link path"
            print(msg)
            sys.exit(1)
        
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(dest))
    
    if not platforms:
        current_platform = get_current_platform()
        platforms[current_platform] = portable_path(str(Path(source_path).expanduser().resolve()))
    
    config.add_entry(name, platforms)
    config.save()
    
    print(f"Added '{name}' to dotfiles folder")
    print(f"Run 'dotfiles sync' to create the link")


def record(source_path: str, platform: Optional[str] = None, path: Optional[str] = None, dotfiles_dir: Path = None):
    """Record an existing symlink without moving it."""
    config, dotfiles_dir = load_config_for_dir(dotfiles_dir)
    
    source = expand_path(source_path)
    
    if not source.exists() and not source.is_symlink():
        print(f"Error: Path does not exist: {source}")
        sys.exit(1)
    
    if not source.is_symlink():
        print(f"Error: 'record' requires a symlink, got: {source}")
        print("Use 'dotfiles add' for regular files/folders")
        sys.exit(1)
    
    source_resolved = source.resolve()
    dotfiles_dir_resolved = dotfiles_dir.resolve()
    name = str(source_resolved.relative_to(dotfiles_dir_resolved))
    dest = dotfiles_dir / name
    
    if not dest.exists():
        print(f"Error: '{name}' does not exist in dotfiles folder: {dotfiles_dir}")
        sys.exit(1)
    
    current_platform = platform if platform else get_current_platform()
    
    if path:
        link_path = path
    else:
        link_path = os.path.abspath(str(source))
    
    link_path = portable_path(link_path)
    config.add_entry(name, {current_platform: link_path})
    config.save()
    
    print(f"Recorded '{name}' for {current_platform}: {link_path}")
    print(f"Run 'dotfiles sync' to verify the link")


def edit(name: str, platform: Optional[str] = None, new_path: Optional[str] = None, dotfiles_dir: Path = None):
    """Edit link record paths for an entry."""
    config, dotfiles_dir = load_config_for_dir(dotfiles_dir)
    entry = config.get_entry(name)
    
    if entry is None:
        print(f"Error: Entry '{name}' not found")
        sys.exit(1)
    
    if platform is not None:
        if new_path is not None:
            stored_path = portable_path(new_path)
            config.update_entry(name, platform, stored_path)
            config.save()
            print(f"Updated {platform} path for '{name}' to: {stored_path}")
        else:
            current_path = entry.get(platform, '')
            print(f"Current {platform} path for '{name}': {current_path}")
            new_value = input(f"Enter new path (or press Enter to keep current): ").strip()
            if new_value:
                stored_path = portable_path(new_value)
                config.update_entry(name, platform, stored_path)
                config.save()
                print(f"Updated {platform} path for '{name}' to: {stored_path}")
            else:
                print("No change made.")
    else:
        print(f"Link record for '{name}':")
        for plat, path in entry.items():
            print(f"  {plat}: {path}")
        
        print("\nEnter platform to edit (or press Enter to cancel):")
        plat_input = input("> ").strip()
        if plat_input and plat_input in entry:
            current_path = entry[plat_input]
            print(f"Current path: {current_path}")
            new_value = input("Enter new path: ").strip()
            if new_value:
                stored_path = portable_path(new_value)
                config.update_entry(name, plat_input, stored_path)
                config.save()
                print(f"Updated {plat_input} path to: {stored_path}")


def sync(platform: Optional[str] = None, dotfiles_dir: Path = None):
    """Sync all links for the specified platform."""
    if platform is None:
        platform = get_current_platform()
    
    config, dotfiles_dir = load_config_for_dir(dotfiles_dir)
    
    entries = config.entries
    if not entries:
        print("No entries found. Run 'dotfiles add' to add dotfiles.")
        return
    
    synced = 0
    errors = []
    
    for name, entry_paths in entries.items():
        dest_path_str = entry_paths.get(platform)
        if not dest_path_str:
            continue
        
        dest_path = expand_path(dest_path_str, resolve_symlinks=False)
        source_path = dotfiles_dir / name
        
        if not source_path.exists():
            errors.append(f"Source not found for '{name}': {source_path}")
            continue
        
        if dest_path.exists():
            if dest_path.is_symlink() and dest_path.resolve() == source_path:
                print(f"Already linked: {name}")
                synced += 1
                continue
            
            backup_name = Path(name).name
            backup_path = create_backup(dest_path, backup_name, platform, dotfiles_dir)
            print(f"Backed up existing: {dest_path}")
            
            if dest_path.is_dir():
                shutil.rmtree(dest_path)
            else:
                dest_path.unlink()
        
        try:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            os.symlink(str(source_path), str(dest_path))
            print(f"Linked: {name} -> {dest_path}")
            synced += 1
        except OSError as e:
            errors.append(f"Failed to link '{name}': {e}")
    
    print(f"\nSynced {synced} entries")
    if errors:
        print("Errors:")
        for err in errors:
            print(f"  {err}")


def restore(name: str, platform: Optional[str] = None, dotfiles_dir: Path = None):
    """Restore a dotfile from the dotfiles folder."""
    if platform is None:
        platform = get_current_platform()
    
    config, dotfiles_dir = load_config_for_dir(dotfiles_dir)
    
    entry = config.get_entry(name)
    if entry is None:
        print(f"Error: Entry '{name}' not found")
        sys.exit(1)
    
    dest_path_str = entry.get(platform)
    if not dest_path_str:
        print(f"Error: No path configured for '{name}' on {platform}")
        sys.exit(1)
    
    dest_path = expand_path(dest_path_str)
    source_path = dotfiles_dir / name
    
    if not source_path.exists():
        print(f"Error: Source not found: {source_path}")
        sys.exit(1)
    
    if dest_path.exists():
        if not dest_path.is_symlink():
            print(f"Error: {dest_path} exists and is not a symlink. Aborting.")
            sys.exit(1)
        
        dest_path.unlink()
    
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_path, dest_path)
    print(f"Restored '{name}' to {dest_path}")
    
    backup_dir = dotfiles_dir / '.dotfiles_backup' / datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"{name}_{platform}"
    shutil.move(str(source_path), str(backup_path))
    print(f"Moved to backup: {backup_path}")


def remove(name: str, platform: Optional[str] = None, dotfiles_dir: Path = None):
    """Remove an entry from link records."""
    config, dotfiles_dir = load_config_for_dir(dotfiles_dir)
    entry = config.get_entry(name)
    
    if entry is None:
        print(f"Error: Entry '{name}' not found")
        sys.exit(1)
    
    if platform is not None:
        if config.remove_platform_from_entry(name, platform):
            config.save()
            print(f"Removed {platform} path from '{name}'")
        else:
            print(f"Error: No path for {platform} in '{name}'")
        return
    
    source_path = dotfiles_dir / name
    
    print(f"Remove entry '{name}' from link records?")
    if source_path.exists():
        print(f"\nThe actual files are at: {source_path}")
        response = input("Delete the actual files too? (y/N): ").strip().lower()
        if response == 'y':
            if source_path.is_dir():
                shutil.rmtree(source_path)
            else:
                source_path.unlink()
            print(f"Deleted: {source_path}")
    
    config.remove_entry(name)
    config.save()
    print(f"Removed entry '{name}'")


def link_status(source_path: Path, dest_str: str, platform: str) -> str:
    """How one record's destination relates to its repo source.

    The link lives at the destination, so the source alone cannot say whether
    the entry works -- a missing link and a stale record both leave the source
    in place. Returns one of:

      ✓  destination is a symlink resolving to the source
      -  destination is absent (this machine has not been synced)
      ✗  source is gone, or the destination is not this link
    """
    if platform != get_current_platform():
        # Another platform's destination cannot be judged from here.
        return ""

    if not source_path.exists() and not source_path.is_symlink():
        return " ✗"

    dest_path = expand_path(dest_str)
    if not dest_path.exists() and not dest_path.is_symlink():
        return " -"

    if dest_path.is_symlink() and dest_path.resolve() == source_path.resolve():
        return " ✓"

    return " ✗"


def list_entries(dotfiles_dir: Path = None):
    """List all link records."""
    config, dotfiles_dir = load_config_for_dir(dotfiles_dir)
    
    entries = config.entries
    if not entries:
        print("No entries found. Run 'dotfiles add' to add dotfiles.")
        return
    
    print(f"Dotfiles folder: {dotfiles_dir}\n")
    print(f"{'Name':<20} {'Platform':<10} {'Path'}")
    print("-" * 60)
    
    for name, entry_paths in entries.items():
        source_path = dotfiles_dir / name
        # Health is a property of the destination link, not of the source alone.
        
        first = True
        for plat, path in entry_paths.items():
            if first:
                print(f"{name:<20} {plat:<10} {path}{link_status(source_path, path, plat)}")
                first = False
            else:
                print(f"{'':<20} {plat:<10} {path}{link_status(source_path, path, plat)}")