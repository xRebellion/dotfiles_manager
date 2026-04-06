# dotfiles - Cross-platform dotfiles manager

A simple, link-based dotfiles manager that works across Linux and Windows.

## No Build Required

This is a pure Python script - no compilation or build process needed. Just make it executable and run.

## Installation

```bash
# Make the script executable
chmod +x dotfiles

# Optionally add to your PATH
sudo ln -s /path/to/dotfiles /usr/local/bin/dotfiles
```

## Quick Start

### 1. Initialize a dotfiles folder

```bash
mkdir ~/dotfiles
cd ~/dotfiles
dotfiles init
```

This creates a `.dotfiles.json` config file in the current directory.

### 2. Add dotfiles

You can run dotfiles from anywhere - it will search for the config file upward, or you can specify explicitly:

```bash
# From anywhere - auto-detects dotfiles folder by searching upward
dotfiles add ~/.config/hypr

# Specify dotfiles folder explicitly with -d/--dotfiles-dir
dotfiles add ~/.config/nvim -d ~/dotfiles

# Or use environment variable
export DOTFILES_DIR=~/dotfiles
dotfiles add ~/.config/nvim

# Specify destination path explicitly
dotfiles add ~/.config/nvim --platform linux ~/.config/nvim

# Add for multiple platforms at once
dotfiles add ~/.config/hypr --platform linux ~/.config/hypr --platform windows "%LOCALAPPDATA%/Hypr"
```

The file/folder is moved to the dotfiles folder and a link record is created.

### 3. Sync links

Create symlinks from the dotfiles folder to their original locations:

```bash
# Auto-detect current platform
dotfiles sync

# Specify platform explicitly
dotfiles sync --platform linux
dotfiles sync -d ~/dotfiles --platform windows
```

### 4. Other commands

```bash
# List all tracked dotfiles
dotfiles list

# Edit link record paths
dotfiles edit nvim --platform linux ~/.config/nvim

# Restore files from dotfiles (convert symlink to real files)
dotfiles restore nvim --platform linux

# Remove from tracking (with prompt for file deletion)
dotfiles remove nvim

# Remove only a specific platform from records
dotfiles remove nvim --platform windows
```

## Commands Reference

| Command | Description |
|---------|-------------|
| `-d/--dotfiles-dir <path>` | Specify dotfiles folder (or use DOTFILES_DIR env var) |
| `init` | Initialize current directory as dotfiles folder |
| `add <path>` | Add file/folder to dotfiles (auto-detects platform) |
| `add <path> --platform <plat> [path]` | Add with specific platform destination |
| `edit <name>` | Edit link record paths (interactive) |
| `edit <name> --platform <plat> [path]` | Edit specific platform path |
| `sync` | Sync all links for current platform |
| `sync --platform <plat>` | Sync for specific platform |
| `restore <name>` | Restore from dotfiles (current platform) |
| `restore <name> --platform <plat>` | Restore for specific platform |
| `remove <name>` | Remove entry, prompt for file deletion |
| `remove <name> --platform <plat>` | Remove only platform from records |
| `list` | List all link records |

## Global Options

- `-h, --help` - Show help message
- `-d <path>, --dotfiles-dir <path>` - Path to dotfiles folder
- `--platform <platform>, -p <platform>` - Specify platform (linux, windows, macos)

**Environment Variable**: Set `DOTFILES_DIR=~/dotfiles` to avoid passing `-d` every time.

## Running Tests

```bash
# Run all tests
python3 -m pytest tests/

# Run with verbose output
python3 -m pytest tests/ -v

# Run specific test file
python3 -m pytest tests/test_commands.py -v
```

## Platform Support

- **Linux** - Full support with symlinks
- **Windows** - Full support (may require Developer Mode for symlinks)
- **macos** - Planned future support

## How It Works

1. **Add**: Moves your config file/folder to the dotfiles folder and records the path
2. **Sync**: Creates symlinks from the original location to the dotfiles folder
3. **Restore**: Removes symlink and copies files back to original location
4. **Link records**: Stored in `.dotfiles.json` with per-platform paths