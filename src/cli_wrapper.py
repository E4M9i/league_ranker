# cli_wrapper.py
# Wrapper for the CLI to be used as an entry point without relative imports

import sys
import os

# This wrapper avoids relative import issues when used as entry point
def run_cli():
    # Import the main function using absolute imports
    from src.cli import main
    main()

if __name__ == "__main__":
    run_cli() 