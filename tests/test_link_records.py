import os
import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.link_records import DotfilesConfig, DOTFILES_CONFIG, find_config_file


class TestDotfilesConfigInit:
    def test_config_init_creates_file(self, tmp_path):
        config_path = tmp_path / DOTFILES_CONFIG
        config = DotfilesConfig(config_path)
        config.dotfiles_path = str(tmp_path)
        config.save()
        
        assert config_path.exists()
    
    def test_config_load_existing(self, tmp_path):
        config_path = tmp_path / DOTFILES_CONFIG
        config = DotfilesConfig(config_path)
        config.dotfiles_path = str(tmp_path)
        config.data['entries'] = {'test': {'linux': '~/.config/test'}}
        config.save()
        
        config2 = DotfilesConfig(config_path)
        assert config2.dotfiles_path == str(tmp_path)
        assert config2.entries['test']['linux'] == '~/.config/test'


class TestDotfilesConfigProperties:
    def test_dotfiles_path_property(self, tmp_path):
        config_path = tmp_path / DOTFILES_CONFIG
        config = DotfilesConfig(config_path)
        
        assert config.dotfiles_path is None
        
        config.dotfiles_path = str(tmp_path)
        assert config.dotfiles_path == str(tmp_path)
    
    def test_entries_property(self, tmp_path):
        config_path = tmp_path / DOTFILES_CONFIG
        config = DotfilesConfig(config_path)
        
        assert config.entries == {}
        
        config.data['entries'] = {'test': {'linux': '~/.config/test'}}
        assert config.entries['test']['linux'] == '~/.config/test'


class TestDotfilesConfigEntryOperations:
    def test_add_entry(self, tmp_path):
        config_path = tmp_path / DOTFILES_CONFIG
        config = DotfilesConfig(config_path)
        
        config.add_entry('vim', {'linux': '~/.config/vim'})
        
        assert 'vim' in config.entries
        assert config.entries['vim']['linux'] == '~/.config/vim'
    
    def test_get_entry_exists(self, tmp_path):
        config_path = tmp_path / DOTFILES_CONFIG
        config = DotfilesConfig(config_path)
        config.add_entry('vim', {'linux': '~/.config/vim'})
        
        entry = config.get_entry('vim')
        assert entry is not None
        assert entry['linux'] == '~/.config/vim'
    
    def test_get_entry_not_exists(self, tmp_path):
        config_path = tmp_path / DOTFILES_CONFIG
        config = DotfilesConfig(config_path)
        
        entry = config.get_entry('nonexistent')
        assert entry is None
    
    def test_update_entry(self, tmp_path):
        config_path = tmp_path / DOTFILES_CONFIG
        config = DotfilesConfig(config_path)
        config.add_entry('vim', {'linux': '~/.config/vim'})
        
        config.update_entry('vim', 'windows', '%LOCALAPPDATA%/vim')
        
        assert config.entries['vim']['linux'] == '~/.config/vim'
        assert config.entries['vim']['windows'] == '%LOCALAPPDATA%/vim'
    
    def test_remove_platform_from_entry(self, tmp_path):
        config_path = tmp_path / DOTFILES_CONFIG
        config = DotfilesConfig(config_path)
        config.add_entry('vim', {'linux': '~/.config/vim', 'windows': '%LOCALAPPDATA%/vim'})
        
        result = config.remove_platform_from_entry('vim', 'windows')
        
        assert result is True
        assert 'windows' not in config.entries['vim']
        assert 'linux' in config.entries['vim']
    
    def test_remove_platform_from_entry_not_exists(self, tmp_path):
        config_path = tmp_path / DOTFILES_CONFIG
        config = DotfilesConfig(config_path)
        config.add_entry('vim', {'linux': '~/.config/vim'})
        
        result = config.remove_platform_from_entry('vim', 'windows')
        
        assert result is False
    
    def test_remove_entry(self, tmp_path):
        config_path = tmp_path / DOTFILES_CONFIG
        config = DotfilesConfig(config_path)
        config.add_entry('vim', {'linux': '~/.config/vim'})
        
        result = config.remove_entry('vim')
        
        assert result is True
        assert 'vim' not in config.entries
    
    def test_remove_entry_not_exists(self, tmp_path):
        config_path = tmp_path / DOTFILES_CONFIG
        config = DotfilesConfig(config_path)
        
        result = config.remove_entry('nonexistent')
        
        assert result is False


class TestFindConfigFile:
    def test_find_config_in_current_dir(self, tmp_path):
        config_path = tmp_path / DOTFILES_CONFIG
        config_path.write_text('{}')
        
        result = find_config_file(tmp_path)
        
        assert result == config_path
    
    def test_find_config_in_parent_dir(self, tmp_path):
        config_path = tmp_path / DOTFILES_CONFIG
        config_path.write_text('{}')
        
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        
        result = find_config_file(subdir)
        
        assert result == config_path
    
    def test_find_config_not_found(self, tmp_path):
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        
        result = find_config_file(subdir)
        
        assert result is None