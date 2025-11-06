#!/usr/bin/env python3
"""
Check that version is only defined in pyproject.toml and not duplicated elsewhere.

This script ensures we maintain a single source of truth for the version number.
"""

import re
import sys
from pathlib import Path


def check_version_duplication():
    """Check for duplicate version definitions in the codebase."""
    errors = []
    project_root = Path(__file__).parent.parent

    # Define patterns to search for
    version_patterns = [
        # Direct assignment
        r'__version__\s*=\s*["\'](\d+\.\d+\.\d+)["\']',
        # Poetry style (but not in pyproject.toml)
        r'version\s*=\s*["\'](\d+\.\d+\.\d+)["\']',
    ]

    # Files/directories to exclude from the check
    excluded_patterns = [
        "pyproject.toml",  # This is our source of truth
        ".git/",
        ".venv/",
        "venv/",
        "__pycache__/",
        ".pytest_cache/",
        "dist/",
        "build/",
        "*.egg-info/",
        "test_output/",
        "my_reports/",
        "reports/",
    ]

    def should_exclude(path: Path) -> bool:
        """Check if a path should be excluded from version check."""
        path_str = str(path)
        for pattern in excluded_patterns:
            if pattern in path_str:
                return True
        return False

    # Search through Python files
    python_files = project_root.rglob("*.py")

    for py_file in python_files:
        if should_exclude(py_file):
            continue

        # Skip the main __init__.py which uses importlib.metadata
        if py_file.name == "__init__.py" and "src/fastq_agents/__init__.py" in str(
            py_file
        ):
            # Check that it uses importlib.metadata, not hardcoded version
            content = py_file.read_text()
            if '__version__ = "' in content and "importlib.metadata" not in content:
                errors.append(
                    f"❌ {py_file.relative_to(project_root)}: "
                    f"Uses hardcoded __version__ instead of importlib.metadata"
                )
            continue

        try:
            content = py_file.read_text()

            for pattern in version_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    version_str = match.group(1)
                    line_num = content[: match.start()].count("\n") + 1
                    errors.append(
                        f"❌ {py_file.relative_to(project_root)}:{line_num}: "
                        f'Found duplicate version definition: "{version_str}"'
                    )
        except Exception as e:
            print(f"Warning: Could not read {py_file}: {e}", file=sys.stderr)

    if errors:
        print("Version duplication check FAILED:\n")
        for error in errors:
            print(error)
        print(
            "\n💡 Version should only be defined in pyproject.toml."
            "\n   Use importlib.metadata.version() to read it at runtime."
        )
        return False
    else:
        print("✅ Version duplication check PASSED")
        print("   Version is only defined in pyproject.toml (single source of truth)")
        return True


if __name__ == "__main__":
    success = check_version_duplication()
    sys.exit(0 if success else 1)
