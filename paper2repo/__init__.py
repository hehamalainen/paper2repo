"""Paper2Repo - AI-powered multi-agent platform for transforming research papers into code."""

__version__ = "1.0.0"

from pathlib import Path

# Read version from VERSION file
_version_file = Path(__file__).parent.parent / "VERSION"
if _version_file.exists():
    __version__ = _version_file.read_text().strip()
