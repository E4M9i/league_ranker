# League Ranking Application

A command-line application that calculates the ranking table for a sports league based on match results.

## Overview

This application processes match results from a file or standard input and generates a ranking table sorted by points. The ranking rules are:
- Win: 3 points
- Draw: 1 point
- Loss: 0 points
- Teams with the same number of points share the same rank and are listed in alphabetical order

## Installation

```bash
# Clone the repository
git clone https://github.com/E4M9i/league_ranker.git
cd league-ranker

# Optional: Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

After installation, the `league-ranker` command becomes available in your environment.

## Usage

### Basic Usage

```bash
# Using the installed command
league-ranker sample_input.txt

# Using stdin with the command
cat sample_input.txt | league-ranker -

# Output to a file
league-ranker sample_input.txt -o rankings.txt

# Using files in other directories
league-ranker path/to/data/matches.txt -o path/to/output/results.txt
```

You can also run the module directly without installation:

```bash
# Process a file using Python module syntax
python -m src.cli sample_input.txt

# Using direct script execution (make sure to use the correct path to the file)
python src/cli.py sample_input.txt

# With files in other directories
python src/cli.py path/to/data/matches.txt -o path/to/output/results.txt

# Use stdin
cat sample_input.txt | python -m src.cli

# Write output to a file
python -m src.cli sample_input.txt -o rankings.txt
```

**Note:** When running without installation, make sure to use the proper path to your input files relative to your current directory. For example, if your file is in a subdirectory called `data`, use `python src/cli.py data/matches.txt`.

### Docker Usage

```bash
# Build the Docker image
docker build -t league-ranker .

# Process a file
docker run -v $(pwd):/app league-ranker sample_input.txt

# Use stdin
cat sample_input.txt | docker run -i league-ranker -

# Write output to file (bind mount ensures file is available on host)
docker run -v $(pwd):/app league-ranker sample_input.txt -o /app/rankings.txt

# Using files in subdirectories
docker run -v $(pwd):/app league-ranker path/to/data/matches.txt -o /app/path/to/output/results.txt

# Using docker compose (note: use space instead of hyphen for newer Docker versions)
docker compose run --rm league-ranker sample_input.txt
```

### Input Format

Each line of the input file should contain a match result in the format:
```
Team Name 1 Score1, Team Name 2 Score2
```

Example from sample_input.txt:
```
South Africa 2, Germany 1
Brazil 3, France 2
Spain 1, Italy 1
South Africa 1, Brazil 1
Germany 2, Spain 2
```

### Output Format

The output will be a ranking table sorted by points (highest to lowest), with alphabetical sorting for teams with the same number of points:

For the above sample input, the output would be something like:
```
1. South Africa, 4 pts
2. Brazil, 4 pts
3. Germany, 1 pt
3. Spain, 1 pt
5. France, 0 pts
6. Italy, 0 pts
```

## Error Handling

- Invalid match formats are skipped and logged
- A summary of errors is provided after processing
- Detailed logs are written to `league_rank.log`

## Development

### Project Structure

- `src/` - Source code
  - `models.py` - Data models
  - `ranker.py` - Core ranking logic
  - `utils.py` - Utility functions and error handling
  - `cli.py` - Command-line interface
  - `cli_wrapper.py` - CLI execution wrapper
  - `__main__.py` - Package entry point
  - `__init__.py` - Package initialization
- `tests/` - Unit tests

### Running Tests

```bash
# Using pytest
pytest tests/

# With coverage report
pytest tests/ --cov=src