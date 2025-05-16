# utils.py
# Utility functions and shared components for the league ranking application.

import logging
import sys
import re
from typing import Optional, Tuple
from logging.handlers import RotatingFileHandler

# Configure logging with console and file output
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s')

# Console handler
console_handler = logging.StreamHandler(sys.stderr)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# File handler with rotation
file_handler = RotatingFileHandler('league_rank.log', maxBytes=10485760, backupCount=5)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

class InvalidMatchFormatError(Exception):
    """Raised when a match line does not match the expected format."""
    pass

class InvalidScoreError(Exception):
    """Raised when a score cannot be converted to an integer."""
    pass 

def parse_match(line: str) -> Optional[Tuple[str, int, str, int]]:
    """Parse a match line into (team1, score1, team2, score2).

    Args:
        line (str): A string representing a match result (e.g., "Team1 3, Team2 2").

    Returns:
        Optional[Tuple[str, int, str, int]]: A tuple of team names and scores if valid,
            None otherwise.

    Raises:
        InvalidMatchFormatError: If the line format is invalid.
        InvalidScoreError: If scores cannot be converted to integers.
    """
    pattern = r"^([^,]+)\s+(\d+),\s+([^,]+)\s+(\d+)$"
    match = re.match(pattern, line.strip())
    if not match:
        logger.error(f"Invalid match format: {line}")
        raise InvalidMatchFormatError(f"Invalid match format: {line}")
    team1, score1, team2, score2 = match.groups()
    try:
        return team1, int(score1), team2, int(score2)
    except ValueError as e:
        logger.error(f"Invalid score format in: {line}")
        raise InvalidScoreError(f"Invalid score format in: {line}") from e 