import os
import sys
import pytest
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from core import commands
from core.link_records import DotfilesConfig, DOTFILES_CONFIG


class TestInit:
    def test_init_creates_config(self, tmp_path, capsys):
        os.chdir(tmp_path)
        
        commands.init()
        
        config_path = tmp_path / DOTFILES_CONFIG
        assert config_path.exists()
        
        config = DotfilesConfig(config_path)
        assert config.dotfiles_path == str(tmp_path)
    
    def test_init_fails_if_exists(self, tmp_path, capsys):
        config_path = tmp_path / DOTFILES_CONFIG
        config_path.write_text('{}')
        
        os.chdir(tmp_path)
        
        with pytest.raises(SystemExit):
            commands.init()
        
        captured = capsys.readouterr()
        assert "already exists" in captured.out


class TestAdd:
    def test_add_moves_file(self, tmp_path, capsys):
        dotfiles_dir = tmp_path / "dotfiles"
        dotfiles_dir.mkdir()
        
        config_path = dotfiles_dir / DOTFILES_CONFIG
        config = DotfilesConfig(config_path)
        config.dotfiles_path = str(dotfiles_dir)
        config.save()
        
        source_file = tmp_path / "testfile.conf"
        source_file.write_text("test content")
        
        os.chdir(dotfiles_dir)
        
        commands.add(str(source_file), {})
        
        assert not source_file.exists()
        assert (dotfiles_dir / "testfile.conf").exists()
    
    def test_add_creates_entry(self, tmp_path, capsys):
        dotfiles_dir = tmp_path / "dotfiles"
        dotfiles_dir.mkdir()
        
        config_path = dotfiles_dir / DOTFILES_CONFIG
        config = DotfilesConfig(config_path)
        config.dotfiles_path = str(dotfiles_dir)
        config.save()
        
        source_file = tmp_path / "testfile.conf"
        source_file.write_text("test content")
        
        os.chdir(dotfiles_dir)
        
        commands.add(str(source_file), {})
        
        config = DotfilesConfig(config_path)
        assert "testfile.conf" in config.entries
    
    def test_add_with_multi_platform(self, tmp_path, capsys):
        dotfiles_dir = tmp_path / "dotfiles"
        dotfiles_dir.mkdir()
        
        config_path = dotfiles_dir / DOTFILES_CONFIG
        config = DotfilesConfig(config_path)
        config.dotfiles_path = str(dotfiles_dir)
        config.save()
        
        source_file = tmp_path / "nvim.conf"
        source_file.write_text("test content")
        
        os.chdir(dotfiles_dir)
        
        platforms = {
            "linux": "~/.config/nvim",
            "windows": "%LOCALAPPDATA%/nvim"
        }
        commands.add(str(source_file), platforms)
        
        config = DotfilesConfig(config_path)
        assert config.entries["nvim.conf"]["linux"] == "~/.config/nvim"
        assert config.entries["nvim.conf"]["windows"] == "%LOCALAPPDATA%/nvim"
    
    def test_add_fails_if_not_exists(self, tmp_path, capsys):
        dotfiles_dir = tmp_path / "dotfiles"
        dotfiles_dir.mkdir()
        
        config_path = dotfiles_dir / DOTFILES_CONFIG
        config = DotfilesConfig(config_path)
        config.dotfiles_path = str(dotfiles_dir)
        config.save()
        
        os.chdir(dotfiles_dir)
        
        with pytest.raises(SystemExit):
            commands.add("/nonexistent/path", {})
        
        captured = capsys.readouterr()
        assert "does not exist" in captured.out
    
    def test_add_fails_if_already_in_dotfiles(self, tmp_path, capsys):
        dotfiles_dir = tmp_path / "dotfiles"
        dotfiles_dir.mkdir()
        
        config_path = dotfiles_dir / DOTFILES_CONFIG
        config = DotfilesConfig(config_path)
        config.dotfiles_path = str(dotfiles_dir)
        config.save()
        
        existing_file = dotfiles_dir / "existing.conf"
        existing_file.write_text("test")
        
        os.chdir(dotfiles_dir)
        
        commands.add(str(existing_file), {"linux": "~/.config/existing.conf"})
        
        config = DotfilesConfig(config_path)
        assert "existing.conf" in config.entries
        assert config.entries["existing.conf"]["linux"] == "~/.config/existing.conf"


class TestRecord:
    def _setup(self, tmp_path):
        dotfiles_dir = tmp_path / "dotfiles"
        dotfiles_dir.mkdir()
        config_path = dotfiles_dir / DOTFILES_CONFIG
        config = DotfilesConfig(config_path)
        config.dotfiles_path = str(dotfiles_dir)
        config.save()
        return dotfiles_dir, config_path

    def test_record_stores_tilde_for_home_path(self, tmp_path, capsys, monkeypatch):
        dotfiles_dir, config_path = self._setup(tmp_path)

        home = tmp_path / "home"
        home.mkdir()
        monkeypatch.setenv("HOME", str(home))

        stored = dotfiles_dir / "home" / "AGENTS.md"
        stored.parent.mkdir(parents=True)
        stored.write_text("content")

        link = home / "AGENTS.md"
        link.symlink_to(stored)

        os.chdir(dotfiles_dir)
        commands.record(str(link), dotfiles_dir=dotfiles_dir)

        config = DotfilesConfig(config_path)
        assert config.entries["home/AGENTS.md"]["linux"] == "~/AGENTS.md"

    def test_add_stores_tilde_for_home_path(self, tmp_path, capsys, monkeypatch):
        dotfiles_dir, config_path = self._setup(tmp_path)

        home = tmp_path / "home"
        (home / ".config").mkdir(parents=True)
        monkeypatch.setenv("HOME", str(home))

        source_file = home / "testfile.conf"
        source_file.write_text("test content")

        os.chdir(dotfiles_dir)
        commands.add(str(source_file), {}, dotfiles_dir=dotfiles_dir)

        config = DotfilesConfig(config_path)
        assert config.entries["testfile.conf"]["linux"] == "~/testfile.conf"


class TestEdit:
    def test_edit_platform_with_path(self, tmp_path, capsys):
        dotfiles_dir = tmp_path / "dotfiles"
        dotfiles_dir.mkdir()
        
        config_path = dotfiles_dir / DOTFILES_CONFIG
        config = DotfilesConfig(config_path)
        config.dotfiles_path = str(dotfiles_dir)
        config.add_entry("test", {"linux": "~/.config/test"})
        config.save()
        
        os.chdir(dotfiles_dir)
        
        commands.edit("test", "linux", "~/.config/test_new")
        
        config = DotfilesConfig(config_path)
        assert config.entries["test"]["linux"] == "~/.config/test_new"
    
    def test_edit_entry_not_found(self, tmp_path, capsys):
        dotfiles_dir = tmp_path / "dotfiles"
        dotfiles_dir.mkdir()
        
        config_path = dotfiles_dir / DOTFILES_CONFIG
        config = DotfilesConfig(config_path)
        config.dotfiles_path = str(dotfiles_dir)
        config.save()
        
        os.chdir(dotfiles_dir)
        
        with pytest.raises(SystemExit):
            commands.edit("nonexistent", "linux", "~/path")
        
        captured = capsys.readouterr()
        assert "not found" in captured.out


class TestList:
    def test_list_empty(self, tmp_path, capsys):
        dotfiles_dir = tmp_path / "dotfiles"
        dotfiles_dir.mkdir()
        
        config_path = dotfiles_dir / DOTFILES_CONFIG
        config = DotfilesConfig(config_path)
        config.dotfiles_path = str(dotfiles_dir)
        config.save()
        
        os.chdir(dotfiles_dir)
        
        commands.list_entries()
        
        captured = capsys.readouterr()
        assert "No entries found" in captured.out
    
    def test_list_shows_entries(self, tmp_path, capsys):
        dotfiles_dir = tmp_path / "dotfiles"
        dotfiles_dir.mkdir()
        
        config_path = dotfiles_dir / DOTFILES_CONFIG
        config = DotfilesConfig(config_path)
        config.dotfiles_path = str(dotfiles_dir)
        config.add_entry("vim", {"linux": "~/.config/vim"})
        config.save()
        
        os.chdir(dotfiles_dir)
        
        commands.list_entries()
        
        captured = capsys.readouterr()
        assert "vim" in captured.out
        assert "linux" in captured.out


class TestSync:
    def test_sync_skips_missing_platform(self, tmp_path, capsys):
        dotfiles_dir = tmp_path / "dotfiles"
        dotfiles_dir.mkdir()
        
        config_path = dotfiles_dir / DOTFILES_CONFIG
        config = DotfilesConfig(config_path)
        config.dotfiles_path = str(dotfiles_dir)
        config.add_entry("test", {"linux": "/tmp/test_target"})  # Only linux
        config.save()
        
        source_file = dotfiles_dir / "test"
        source_file.write_text("test content")
        
        os.chdir(dotfiles_dir)
        
        commands.sync("windows")  # Sync for windows, but only linux configured
        
        captured = capsys.readouterr()
        assert "Synced 0 entries" in captured.out


class TestRemove:
    def test_remove_platform_only(self, tmp_path, capsys):
        dotfiles_dir = tmp_path / "dotfiles"
        dotfiles_dir.mkdir()
        
        config_path = dotfiles_dir / DOTFILES_CONFIG
        config = DotfilesConfig(config_path)
        config.dotfiles_path = str(dotfiles_dir)
        config.add_entry("test", {"linux": "~/.config/test", "windows": "%LOCALAPPDATA%/test"})
        config.save()
        
        os.chdir(dotfiles_dir)
        
        commands.remove("test", "windows")
        
        config = DotfilesConfig(config_path)
        assert "windows" not in config.entries["test"]
        assert "linux" in config.entries["test"]
    
    def test_remove_entry_not_found(self, tmp_path, capsys):
        dotfiles_dir = tmp_path / "dotfiles"
        dotfiles_dir.mkdir()
        
        config_path = dotfiles_dir / DOTFILES_CONFIG
        config = DotfilesConfig(config_path)
        config.dotfiles_path = str(dotfiles_dir)
        config.save()
        
        os.chdir(dotfiles_dir)
        
        with pytest.raises(SystemExit):
            commands.remove("nonexistent")
        
        captured = capsys.readouterr()
        assert "not found" in captured.out