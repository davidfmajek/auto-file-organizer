"""
test.py

Unit tests for Auto File Organizer components.
Run with pytest.
"""
import os
import json
import shutil
import tempfile
from pathlib import Path
import pytest

from file_scanner import load_config, scan_directories, get_file_metadata
from utils import apply_suggestion
from organizer import suggest_actions

# --- Fixtures ---

@pytest.fixture
def tmp_config(tmp_path):
    cfg = tmp_path / "config.yaml"
    content = {
        'monitor_folders': [str(tmp_path / 'inbox')],
        'check_interval_minutes': 5,
        'auto_confirm': True,
        'root_folder': str(tmp_path / 'organized')
    }
    import yaml
    cfg.write_text(yaml.safe_dump(content))
    # create inbox and organized directories
    (tmp_path / 'inbox').mkdir()
    (tmp_path / 'organized').mkdir()
    return str(cfg)

@pytest.fixture
def sample_text_file(tmp_path):
    inbox = tmp_path / 'inbox'
    inbox.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
    file = inbox / 'note.txt'
    file.write_text('Hello world! This is a test. ' * 10)
    return file

# --- Tests for file_scanner ---

def test_load_config(tmp_config):
    cfg = load_config(tmp_config)
    assert cfg['check_interval_minutes'] == 5
    assert isinstance(cfg['monitor_folders'], list)


def test_scan_directories(tmp_config, sample_text_file, monkeypatch):
    cfg = load_config(tmp_config)
    files = scan_directories(cfg)
    # Expect one file metadata dict
    assert len(files) == 1
    meta = files[0]
    assert meta['name'] == 'note.txt'
    assert 'Hello world' in meta['preview']

# --- Tests for apply_suggestion (utils) ---

def test_apply_suggestion_rename_and_move(tmp_path, sample_text_file):
    # Prepare metadata and suggestion
    fm = get_file_metadata(sample_text_file)
    suggestion = {
        'suggested_name': 'renamed.txt',
        'suggested_folder': 'subdir',
        'delete': False
    }
    # Apply with auto_confirm
    apply_suggestion(fm, suggestion, root_folder=None, auto_confirm=True)
    # Check that file moved and renamed correctly
    dest = sample_text_file.parent / 'subdir' / 'renamed.txt'
    assert dest.exists()


def test_apply_suggestion_delete(tmp_path, sample_text_file):
    fm = get_file_metadata(sample_text_file)
    suggestion = {'delete': True}
    apply_suggestion(fm, suggestion, auto_confirm=True)
    assert not sample_text_file.exists()

# --- Test suggest_actions stub ---

def test_suggest_actions_json_parse(monkeypatch):
    # Monkeypatch LLM chain to return valid JSON
    from organizer import chain
    monkeypatch.setattr(chain, '__call__', lambda **kwargs: json.dumps({
        'suggested_name': 'file1',
        'suggested_folder': 'Docs',
        'delete': False
    }))
    fm = {'name': 'dummy', 'size_bytes': 0, 'created_time': '', 'modified_time': '', 'preview': ''}
    suggestion = suggest_actions(fm)
    assert suggestion['suggested_name'] == 'file1'
    assert suggestion['suggested_folder'] == 'Docs'
    assert suggestion['delete'] is False

# To run the tests:
# pytest -q
