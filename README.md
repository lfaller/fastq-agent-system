# FASTQ Agent System

A multi-agent system for FASTQ file quality analysis using AI-powered agents. This project demonstrates agentic AI patterns by orchestrating specialized agents that work together to analyze genomic sequencing data.

## 🧬 Overview

The FASTQ Agent System breaks down complex FASTQ analysis into specialized, AI-powered agents:

- **Parser Agent**: Reads and parses FASTQ files, extracts basic metrics
- **Analysis Agent**: Interprets quality scores and identifies potential issues
- **Report Agent**: Generates human-readable reports with actionable recommendations
- **Coordinator Agent**: Orchestrates the multi-agent workflow

## 🚀 Features

- Multi-agent architecture using Claude API
- FASTQ file parsing and quality analysis
- Rich CLI interface with beautiful output
- Comprehensive quality reports with recommendations
- Extensible agent framework
- Type-safe code with Pydantic models

## 📋 Requirements

- Python 3.9+
- Poetry for dependency management
- Anthropic API key for Claude access

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
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

### Analyze a FASTQ File (Coming Soon)

```bash
# This will be implemented in the next development phase
poetry run fastq-analyze analyze path/to/your/file.fastq
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

## 📊 Current Status

**✅ Completed:**
- Project structure and configuration
- Poetry setup with all dependencies
- Base agent class implementation
- CLI framework with Rich formatting
- Development tooling (pre-commit, testing, linting)

**🚧 In Progress:**
- Agent implementations (parser, analyzer, reporter, coordinator)
- FASTQ file handling and parsing
- Quality metrics calculation
- Report generation

**📋 Planned:**
- Multi-agent orchestration
- Advanced quality analysis algorithms
- Customizable report templates
- Batch processing capabilities
- Web interface

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
2. Look through existing [Issues](https://github.com/your-username/fastq-agent-system/issues)
3. Create a new issue with a detailed description

---

**Happy analyzing! 🧬✨**
