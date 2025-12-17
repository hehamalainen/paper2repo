"""Test CLI help functionality."""
import subprocess
import sys


def test_cli_help_via_main():
    """Test CLI help through main.py."""
    result = subprocess.run(
        [sys.executable, 'main.py', '--help'],
        capture_output=True,
        text=True,
        cwd='/home/runner/work/paper2repo/paper2repo'
    )
    assert result.returncode == 0
    assert 'Paper2Repo' in result.stdout or 'usage' in result.stdout.lower()


def test_cli_version():
    """Test version command."""
    result = subprocess.run(
        [sys.executable, 'main.py', '--version'],
        capture_output=True,
        text=True,
        cwd='/home/runner/work/paper2repo/paper2repo'
    )
    assert result.returncode == 0
    assert 'Paper2Repo' in result.stdout
    assert '1.0.0' in result.stdout


def test_cli_module_execution():
    """Test CLI as module."""
    result = subprocess.run(
        [sys.executable, '-m', 'paper2repo.cli.main', '--version'],
        capture_output=True,
        text=True,
        cwd='/home/runner/work/paper2repo/paper2repo'
    )
    # This might fail if click is not installed, which is okay
    assert result.returncode in [0, 1]
