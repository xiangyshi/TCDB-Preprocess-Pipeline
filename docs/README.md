# TCDB Domain Visualization - Refactored

A comprehensive Python tool for analyzing protein domain architectures from TCDB (Transport Classification Database) proteins using rpsblast and CDD (Conserved Domain Database) files.

## Overview

This project processes protein domains from TCDB-specific proteins, analyzing domain data from CDD files or rescue files to generate detailed domain architecture analysis and visualizations. It supports various visualization types including domain architecture plots, characteristic analysis, hole detection, and summary statistics.

## New Architecture

The refactored version features a clean, modular architecture with:

- **Clean Architecture**: Separation of concerns with distinct layers
- **Type Hints**: Full type annotation throughout the codebase
- **Better Error Handling**: Comprehensive error handling and validation
- **Modular Design**: Loosely coupled components with clear interfaces
- **Configuration Management**: Centralized configuration with environment support
- **Testing**: Comprehensive test suite with unit and integration tests

## Project Structure

```
src/
├── cli/                    # Command line interface
│   ├── main.py            # Entry point
│   └── argument_parser.py # CLI argument handling
├── core/                   # Core domain models
│   ├── domain.py          # Domain entity
│   ├── system.py          # System entity
│   ├── family.py          # Family entity
│   └── hole.py            # Hole entity
├── services/              # Business logic
│   ├── family_service.py  # Family processing
│   ├── domain_service.py  # Domain analysis
│   └── visualization_service.py # Plot generation
├── parsers/               # Data parsing
│   ├── cdd_parser.py      # CDD file parsing
│   └── rescue_parser.py   # Rescue file parsing
├── visualizers/           # Visualization components
│   ├── domain_visualizer.py # Domain plotting
│   ├── family_visualizer.py # Family plotting
│   └── plot_factory.py    # Plot creation factory
└── utils/                 # Utility functions
    ├── config.py          # Configuration management
    ├── file_utils.py      # File operations
    └── validation.py      # Input validation
```

## Installation

### Prerequisites

- Python 3.8 or higher
- All dependencies listed in `requirements.txt`

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd TCDB-Domain-Visualization
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

## Usage

### Command Line Interface

The main CLI tool is now available as `tcdb-visualize`:

```bash
# Process CDD file with all plots
tcdb-visualize -c singles.cdd -p all -o results/

# Process specific families
tcdb-visualize -c singles.cdd -t "1.A.12,2.A.1" -p "arch,summary"

# Process rescue data
tcdb-visualize -r rescued/ -p char_rescue -o rescue_results/
```

### Programmatic Usage

```python
from src.services.family_service import FamilyService
from src.services.visualization_service import VisualizationService
from src.utils.config import config

# Initialize services
family_service = FamilyService()
visualization_service = VisualizationService()

# Load family data
family_data = family_service.load_family_data("singles.cdd", "cdd", "1.A.12")

# Create family object
family = family_service.create_family(family_data, "1.A.12", "output/")

# Generate plots
visualization_service.generate_all_plots(family)
```

## Configuration

Configuration is managed through environment variables or the `Config` class:

```python
from src.utils.config import config

# Access configuration
output_dir = config.output_directory
merge_domains = config.merge_overlapping_domains
```

### Environment Variables

- `TCDB_OUTPUT_DIR`: Output directory (default: "output/")
- `TCDB_SEQUENCES_DIR`: Sequences directory (default: "data/sequences/")
- `TCDB_MERGE_DOMAINS`: Merge overlapping domains (default: "true")
- `TCDB_HOLE_THRESHOLD`: Hole detection threshold (default: "50")
- `TCDB_CHAR_THRESHOLD`: Characteristic domain threshold (default: "0.5")

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run with coverage
pytest --cov=src tests/
```

## Development

### Code Style

The project uses:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

### Pre-commit Hooks

Install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

## Migration from Original Code

The refactored version maintains backward compatibility with the original CLI interface. To migrate:

1. **Install the new package**: `pip install -e .`
2. **Use the new CLI**: Replace `python domain_extract.py` with `tcdb-visualize`
3. **Update imports**: Use the new module structure in your code

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

[Add your license information here]

## Changelog

### Version 2.0.0
- Complete refactoring with clean architecture
- Added type hints throughout
- Improved error handling and validation
- Modular design with service layer
- Comprehensive test suite
- Better configuration management 