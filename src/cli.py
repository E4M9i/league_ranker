# cli.py
# Command-line interface for the league ranking application.

import argparse
import sys
import os

# Try both relative and absolute imports to support both direct execution and package imports
try:
    from .utils import logger
    from .ranker import LeagueRanker
except (ImportError, ValueError):
    # When run directly as a script
    from src.utils import logger
    from src.ranker import LeagueRanker

def main():
    """Main entry point for the league ranking application.

    Parses command-line arguments, processes input matches, and outputs rankings.
    Handles file errors and summarizes processing errors.
    """
    parser = argparse.ArgumentParser(description="Calculate league rankings from match results.")
    parser.add_argument("file", nargs="?", default="-", help="Input file (default: stdin)")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    args = parser.parse_args()

    ranker = LeagueRanker()
    input_source = None
    try:
        input_source = open(args.file) if args.file != "-" else sys.stdin
    except FileNotFoundError:
        logger.error(f"Input file not found : {args.file}")
        print(f"Error: Input file '{args.file}' not found.", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        logger.error(f"Permission denied accessing file: {args.file}")
        print(f"Error: Permission denied accessing file '{args.file}'.", file=sys.stderr)
        sys.exit(1)

    with input_source as f:
        for line in f:
            if not line.strip():
                continue
            if not ranker.process_match(line):
                print(f"Skipping invalid line: {line.strip()}", file=sys.stderr)

    rankings = ranker.generate_rankings()
    
    # Handle output to file or stdout
    if args.output:
        try:
            with open(args.output, 'w') as out_file:
                for line in rankings:
                    out_file.write(f"{line}\n")
            logger.info(f"Rankings written to {args.output}")
        except IOError as e:
            logger.error(f"Error writing to output file: {e}")
            print(f"Error: Failed to write to output file '{args.output}': {e}", file=sys.stderr)
            sys.exit(1)
    else:
        for line in rankings:
            print(line)

    # Summarize errors if any
    if ranker.error_count > 0:
        logger.info(f"Processing completed with {ranker.error_count} errors.")
        print(f"Note: {ranker.error_count} lines were skipped due to errors. See log for details.", file=sys.stderr)

if __name__ == "__main__":
    main() 