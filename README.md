# FASTQ Agent System

A multi-agent system for FASTQ file quality analysis using AI-powered agents. This project demonstrates agentic AI patterns by orchestrating specialized agents that work together to analyze genomic sequencing data.

## 🧬 Overview

The FASTQ Agent System breaks down complex FASTQ analysis into specialized, AI-powered agents:

- **Parser Agent**: Reads and parses FASTQ files, extracts basic metrics
- **Analysis Agent**: Interprets quality scores and identifies potential issues
- **Report Agent**: Generates human-readable reports with actionable recommendations
- **Coordinator Agent**: Orchestrates the multi-agent workflow

## 🚀 Features

- **Multi-agent architecture** using Claude API for intelligent analysis
- **Comprehensive FASTQ parsing** with BioPython integration
- **AI-powered quality assessment** and recommendations
- **Beautiful report generation** in multiple formats (HTML, JSON, Markdown)
- **Rich CLI interface** with colorful output and progress indicators
- **Quality scoring and flagging** with automated issue detection
- **Processing recommendations** for downstream analysis optimization
- **Extensible agent framework** for adding new analysis capabilities
- **Type-safe code** with Pydantic models and comprehensive validation

## 📋 Requirements

- Python 3.9+
- Poetry for dependency management
- Anthropic API key for Claude access

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/fastq-agent-system.git
cd fastq-agent-system
```

### 2. Install Poetry

If you don't have Poetry installed:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 3. Install Dependencies

```bash
poetry install
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env
```

Get your API key from [Anthropic Console](https://console.anthropic.com/).

### 5. Set Up Pre-commit Hooks

```bash
poetry run pre-commit install
```

## 🎯 Quick Start

### Test the Installation

```bash
# Test that everything is working
poetry run fastq-analyze hello
```

You should see a welcome message confirming the setup is working.

### Generate Analysis Reports

The main feature is generating comprehensive analysis reports for FASTQ files:

```bash
# Generate an HTML report (opens automatically in browser)
poetry run fastq-analyze generate-report tests/fixtures/sample.fastq --open

# Fast mode for quick analysis (5-10x faster, template-based insights)
poetry run fastq-analyze generate-report path/to/your/file.fastq --fast --open

# Generate different formats
poetry run fastq-analyze generate-report path/to/your/file.fastq --format html
poetry run fastq-analyze generate-report path/to/your/file.fastq --format json
poetry run fastq-analyze generate-report path/to/your/file.fastq --format markdown

# Specify custom output directory
poetry run fastq-analyze generate-report path/to/your/file.fastq --output-dir ./my_reports --format html --open
```

**Performance**: Small datasets (< 50 reads) automatically use fast analysis (~0.5 seconds). Larger datasets can use `--fast` flag for 5-10x speedup.

### Test the Parser (Development)

```bash
# Test the FASTQ parser with sample data
poetry run fastq-analyze test-parser

# Test with your own FASTQ file
poetry run fastq-analyze test-parser --fastq-file path/to/your/file.fastq
```

## 📁 Project Structure

```
fastq-agent-system/
├── src/
│   └── fastq_agents/
│       ├── __init__.py
│       ├── agents/              # Agent implementations
│       │   ├── __init__.py
│       │   ├── base.py         # Base agent class
│       │   ├── parser.py       # FASTQ parsing agent
│       │   ├── analyzer.py     # Quality analysis agent
│       │   ├── reporter.py     # Report generation agent
│       │   └── coordinator.py  # Multi-agent coordinator
│       ├── models/             # Data models
│       │   ├── __init__.py
│       │   ├── fastq_data.py   # FASTQ data structures
│       │   └── reports.py      # Report models
│       ├── utils/              # Utility functions
│       │   ├── __init__.py
│       │   ├── file_handlers.py
│       │   └── metrics.py
│       └── cli.py              # Command line interface
├── tests/                      # Test suite
├── examples/                   # Example usage
├── .env                        # Environment variables (create this)
├── .gitignore                  # Git ignore rules
├── .pre-commit-config.yaml     # Code quality hooks
├── pyproject.toml              # Project configuration
└── README.md                   # This file
```

## 🔧 Development

### Running Tests

```bash
poetry run pytest
```

### Code Formatting

```bash
# Format code
poetry run black src/ tests/
poetry run isort src/ tests/

# Type checking
poetry run mypy src/

# Lint code
poetry run flake8 src/ tests/
```

### Adding Dependencies

```bash
# Add a new dependency
poetry add package_name

# Add a development dependency
poetry add --group dev package_name
```

### Version Management

The project uses a **single source of truth** for versioning in `pyproject.toml`. The version is automatically propagated throughout the codebase using `importlib.metadata`.

#### Bumping the Version

Use Poetry's built-in version command (recommended):

```bash
# Bump patch version (0.4.0 -> 0.4.1)
poetry version patch

# Bump minor version (0.4.0 -> 0.5.0)
poetry version minor

# Bump major version (0.4.0 -> 1.0.0)
poetry version major

# Set specific version
poetry version 1.2.3
```

After bumping the version:

```bash
# Verify the new version
poetry version

# Commit the change
git add pyproject.toml
git commit -m "chore: bump version to $(poetry version -s)"
```

**Important Notes:**
- ✅ **DO** use `poetry version` command to update the version
- ✅ **DO** only change version in `pyproject.toml`
- ❌ **DON'T** manually edit `__version__` in Python files
- ❌ **DON'T** add version definitions in submodules

The pre-commit hook will automatically verify that no duplicate version definitions exist in the codebase.

#### Checking Current Version

```bash
# From command line
poetry version

# From Python code
poetry run python -c "import fastq_agents; print(fastq_agents.__version__)"
```

## 🤖 Agent Architecture

### Base Agent Class

All agents inherit from `BaseAgent` which provides:

- LLM query interface using Claude API
- Consistent logging and error handling
- Standardized input/output patterns
- Configuration management

### Agent Workflow

1. **Input**: FASTQ file path
2. **Parser Agent**: Extracts sequences, quality scores, and basic metrics
3. **Analysis Agent**: Interprets quality data and identifies issues
4. **Report Agent**: Generates comprehensive reports
5. **Coordinator**: Orchestrates the workflow and handles agent communication
6. **Output**: Quality analysis report with recommendations

## 📊 Report Formats

### HTML Reports
- **Professional styling** with modern CSS and responsive design
- **Quality assessment badges** with color-coded ratings
- **Interactive metrics dashboard** showing key statistics
- **AI-generated insights** and recommendations
- **Quality issue flagging** with detailed explanations

### JSON Reports
- **Machine-readable format** for integration with other tools
- **Complete analysis data** including all metrics and recommendations
- **API-friendly structure** for programmatic access

### Markdown Reports
- **Human-readable format** perfect for documentation
- **Version control friendly** for tracking analysis changes
- **Easy integration** with documentation systems

## 🔧 Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `hello` | Test installation and show welcome message | `poetry run fastq-analyze hello` |
| `generate-report` | Create comprehensive analysis report | `poetry run fastq-analyze generate-report file.fastq --format html --open` |
| `test-parser` | Test FASTQ parsing with sample data | `poetry run fastq-analyze test-parser` |
| `debug-env` | Debug environment variable loading | `poetry run fastq-analyze debug-env` |

### Report Generation Options

```bash
poetry run fastq-analyze generate-report [FASTQ_FILE] [OPTIONS]

Options:
  --output-dir TEXT     Output directory for reports [default: ./reports]
  --format TEXT         Report format: html, json, markdown [default: html]
  --open               Open HTML report in browser automatically
  --help               Show help message and exit
```

## 🛡️ Troubleshooting

### SSL/urllib3 Warning

If you see urllib3 SSL warnings on macOS, this is due to LibreSSL vs OpenSSL compatibility. The project pins urllib3 to v1.26.18 to avoid this issue.

### API Key Issues

Make sure your `.env` file contains your Anthropic API key:

```bash
ANTHROPIC_API_KEY=your_actual_api_key_here
```

### Poetry Environment Issues

If you encounter Python version issues:

```bash
# Remove existing environment
poetry env remove python

# Create new environment with correct Python
poetry env use python3.9
poetry install
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and ensure code quality (`poetry run pytest`, `poetry run black .`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Claude](https://anthropic.com/claude) by Anthropic
- Uses [Poetry](https://python-poetry.org/) for dependency management
- CLI powered by [Typer](https://typer.tiangolo.com/) and [Rich](https://rich.readthedocs.io/)
- Bioinformatics support from [BioPython](https://biopython.org/)

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Troubleshooting](#🛡️-troubleshooting) section
2. Look through existing [Issues](https://github.com/YOUR_USERNAME/fastq-agent-system/issues)
3. Create a new issue with a detailed description

---

**Happy analyzing! 🧬✨**
