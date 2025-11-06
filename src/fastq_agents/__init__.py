"""FASTQ Agent System - Multi-agent system for FASTQ file quality analysis."""

# Version is automatically read from pyproject.toml via package metadata
# This ensures pyproject.toml is the single source of truth
try:
    from importlib.metadata import PackageNotFoundError, version

    __version__ = version("fastq-agent-system")
except PackageNotFoundError:
    # Package is not installed, likely running from source during development
    __version__ = "0.4.0-dev"

__author__ = "Lina L Faller"
__email__ = "Lina.Faller@gmail.com"

# Import main classes when they're created
# from .agents import BaseAgent
# from .models import FASTQData
