# TCDB Domain Visualization

A Python tool for visualizing and analyzing protein domain architectures from TCDB (Transporter Classification Database) data. This tool processes CDD (Conserved Domain Database) files and rescue data to generate comprehensive domain visualizations and statistics.

## Features

- **Domain Architecture Visualization**: Generate visual representations of protein domain arrangements
- **Characteristic Domain Analysis**: Identify and visualize domains that are characteristic of specific families
- **Rescue Data Processing**: Specialized handling for rescue family data with filtering logic
- **Multiple Output Formats**: Generate SVG plots, HTML reports, and CSV data exports
- **Comprehensive Statistics**: Domain coverage, frequency analysis, and family statistics
- **Flexible Input Support**: Process both CDD files and rescue data directories

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Option 1: Install from Source (Development Mode)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd TCDB-Preprocess-Pipeline
   ```

2. **Install in development mode**:
   ```bash
   pip install -e .
   ```

   This installs the package in "editable" mode, allowing you to modify the code and see changes immediately without reinstalling.

### Option 2: Install from PyPI (Production)

```bash
pip install tcdb-visualize
```

### Option 3: Install Dependencies Only

If you prefer to run without installing the package:

```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

The tool provides a command-line interface with the `tcdb-visualize` command.

#### Basic Syntax

```bash
tcdb-visualize [OPTIONS] -o OUTPUT_DIR
```

#### Input Options

- **CDD File**: `-c <cdd_file>` or `--cdd <cdd_file>`
- **Rescue Directory**: `-r <rescue_dir>` or `--rescue <rescue_dir>`
- **Family ID**: `-t <family_id>` or `--target <family_id>`

#### Plot Types

- `general`: General domain architecture visualization
- `char`: Characteristic domain analysis
- `arch`: Domain architecture comparison
- `holes`: Inter-domain region (holes) visualization
- `summary`: Summary statistics
- `char_rescue`: Rescue-specific characteristic analysis

#### Output Options

- `-o <output_dir>` or `--output <output_dir>`: Specify output directory
- `-d <csv_file>` or `--data <csv_file>`: Export data to CSV file
- `--log-level <level>`: Set logging level (DEBUG, INFO, WARNING, ERROR)

### Example Commands

#### 1. Process CDD File with General Visualization

```bash
# Generate general domain architecture plots
tcdb-visualize -c data/cdd_files/singles.cdd -p general -t 1.A.1 -o output/

# Generate all plot types for a family
tcdb-visualize -c data/cdd_files/singles.cdd -p all -t 1.A.1 -o output/
```

#### 2. Process Rescue Data with Characteristic Analysis

```bash
# Generate rescue-specific characteristic plots
tcdb-visualize -r data/rescue_files -p char_rescue -t 1.A.12 -o output/

# Generate characteristic domain analysis
tcdb-visualize -r data/rescue_files -p char -t 1.A.12 -o output/
```

#### 3. Generate Multiple Plot Types

```bash
# Generate specific plot types
tcdb-visualize -c data/cdd_files/singles.cdd -p general,char,summary -t 1.A.1 -o output/

# Generate all available plots
tcdb-visualize -r data/rescue_files -p all -t 1.A.12 -o output/
```

#### 4. Export Data to CSV

```bash
# Export domain data to CSV file
tcdb-visualize -c data/cdd_files/singles.cdd -d domain_data.csv -t 1.A.1 -o output/

# Export rescue data to CSV file
tcdb-visualize -r data/rescue_files -d rescue_data.csv -t 1.A.12 -o output/

# Export data with plots
tcdb-visualize -c data/cdd_files/singles.cdd -p general -d domain_data.csv -t 1.A.1 -o output/

# Export data only (no plots)
tcdb-visualize -c data/cdd_files/singles.cdd -d domain_data.csv -t 1.A.1 -o output/
```

#### 5. Advanced Usage with Logging

```bash
# Run with detailed logging
tcdb-visualize -r data/rescue_files -p char_rescue -t 1.A.12 -o output/ --log-level DEBUG

# Run with minimal logging
tcdb-visualize -c data/cdd_files/singles.cdd -p general -t 1.A.1 -o output/ --log-level ERROR
```

### Input Data Format

#### CDD Files
CDD files should contain domain information in the following format:
```
family_id    system_id    accession    domains
1.A.1        sys1         P00001       A:1-50;B:51-100
1.A.1        sys2         P00002       A:1-60;C:61-120
```

#### Rescue Data
Rescue data should be organized in a directory structure:
```
rescue_files/
├── 1.A.12_rescuedDomains.tsv
├── 1.A.13_rescuedDomains.tsv
└── ...
```

Each TSV file should contain:
```
family    system    accession    domains    bitscore    evalue    rescue_round
1.A.12    sys1      P00001       A:1-50     100.5       1e-10     1
1.A.12    sys2      P00002       A:1-60     95.2        1e-8      2
```

### Output Structure

The tool generates the following output structure:

```
output/
├── plots/
│   ├── general/
│   │   └── general-1.A.1.html
│   ├── char/
│   │   └── char-1.A.1.html
│   ├── arch/
│   │   └── arch-1.A.1.html
│   ├── holes/
│   │   └── holes-1.A.1.html
│   └── summary/
│       └── summary-1.A.1.html
├── csv/
│   └── 1.A.1_domain_data.csv
└── svg/
    └── *.svg (individual domain plots)
```

### CSV Data Format

When using the `-d` option, the tool exports data in the following CSV format:

```csv
Accession,Length,Family,Subfamily,Domains,Separators
Q8IUQ4,282,8.A.133,8.A.133.1,"[('CDD438216', 39, 79, 9.6e-07)]","[('CDD438216 to END', 80, 281)]"
O43255,324,8.A.133,8.A.133.1,"[('CDD438216', 78, 119, 1.6e-06)]","[('BEGIN to CDD438216', 0, 77), ('CDD438216 to END', 120, 323)]"
```

**Column Descriptions:**
- **Accession**: Protein accession number
- **Length**: Protein sequence length
- **Family**: TCDB family identifier
- **Subfamily**: System identifier (used as subfamily)
- **Domains**: List of domain tuples in format `(domain_id, start, end, evalue)`
- **Separators**: List of inter-domain region tuples in format `(description, start, end)`

## Configuration

### Environment Variables

You can set the following environment variables:

- `TCDB_LOG_LEVEL`: Set default logging level
- `TCDB_OUTPUT_DIR`: Set default output directory

### Configuration File

Create a `config.ini` file in your working directory:

```ini
[paths]
sequence_dir = data/sequences/
output_dir = output/

[logging]
level = INFO
file = tcdb_visualization.log

[processing]
merge_overlapping = true
fill_holes = true
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_domain.py

# Run with coverage
pytest --cov=src

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Run linting
flake8 src/

# Run type checking
mypy src/

# Format code
black src/
```

### Building Distribution

```bash
# Build source distribution
python setup.py sdist

# Build wheel
python setup.py bdist_wheel

# Install build tools
pip install build twine

# Build package
python -m build
```

## Troubleshooting

### Common Issues

1. **Changes not reflected (Repackaging)**: 
   If you modified the code but don't see changes, you likely need to install in editable mode.
   Run `pip install -e .` once. After that, no "repackaging" is needed; changes apply immediately.

2. **Import Errors**: Ensure you've installed the package correctly with `pip install -e .`

3. **File Not Found**: Check that input files exist and paths are correct

3. **Permission Errors**: Ensure you have write permissions for the output directory

4. **Memory Issues**: For large datasets, consider processing smaller subsets

### Logging

Enable debug logging to troubleshoot issues:

```bash
tcdb-visualize -c data.cdd -p general -t 1.A.1 -o output/ --log-level DEBUG
```

### Getting Help

```bash
# Show help
tcdb-visualize --help

# Show version
tcdb-visualize --version
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

[Add your license information here]

## Citation

If you use this tool in your research, please cite:

[Add citation information here]

## Contact

[Add contact information here]
