"""FASTQ Agent System - Multi-agent system for FASTQ file quality analysis."""

# Version is automatically read from pyproject.toml via package metadata
# This ensures pyproject.toml is the single source of truth
try:
    from importlib.metadata import PackageNotFoundError, version

    __version__ = version("fastq-agent-system")
except PackageNotFoundError:
    # Package is not installed, fallback to reading from pyproject.toml
    import sys
    from pathlib import Path

    # Use tomllib (Python 3.11+) or tomli (Python < 3.11)
    if sys.version_info >= (3, 11):
        import tomllib
    else:
        try:
            import tomli as tomllib
        except ImportError:
            import tomli as tomllib

    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        pyproject_data = tomllib.load(f)
    __version__ = pyproject_data["tool"]["poetry"]["version"] + "-dev"

__author__ = "Lina L Faller"
__email__ = "Lina.Faller@gmail.com"

# Import main classes when they're created
# from .agents import BaseAgent
# from .models import FASTQData
