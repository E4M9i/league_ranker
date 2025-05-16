# ranker.py
# Core logic for ranking teams in the league ranking application.

from typing import List, Dict
from collections import defaultdict
from functools import lru_cache

from .models import Team
from .utils import InvalidMatchFormatError, InvalidScoreError, parse_match

@lru_cache(maxsize=128)
def get_points_string(points: int) -> str:
    """Return the correct point(s) suffix based on value.
    
    Args:
        points (int): The number of points
        
    Returns:
        str: "pt" for 1 point, "pts" for other values
    """
    return "pt" if points == 1 else "pts"

class LeagueRanker:
    def __init__(self):
        self.teams: Dict[str, Team] = defaultdict(Team)
        self.error_count = 0

    def process_match(self, line: str) -> bool:
        """Process a match and update team points.

        Args:
            line (str): A string representing a match result.

        Returns:
            bool: True if the match was processed successfully, False otherwise.
        """
        try:
            parsed = parse_match(line)
            if not parsed:
                return False
            team1_name, score1, team2_name, score2 = parsed

            # Initialize teams if not already present
            if team1_name not in self.teams:
                self.teams[team1_name] = Team(name=team1_name)
            if team2_name not in self.teams:
                self.teams[team2_name] = Team(name=team2_name)

            # Update points based on match result
            if score1 == score2:
                self.teams[team1_name].points += 1
                self.teams[team2_name].points += 1
            elif score1 > score2:
                self.teams[team1_name].points += 3
            else:
                self.teams[team2_name].points += 3
            return True
        except (InvalidMatchFormatError, InvalidScoreError):
            self.error_count += 1
            return False

    def generate_rankings(self) -> List[str]:
        """Generate sorted rankings in the required format.

        Returns:
            List[str]: A list of formatted ranking strings.
        """
        sorted_teams = sorted(self.teams.values())
        result = []
        current_rank = 1
        prev_points = None

        for i, team in enumerate(sorted_teams, 1):
            # Adjust rank for ties
            if prev_points is not None and team.points != prev_points:
                current_rank = i
            prev_points = team.points
            result.append(f"{current_rank}. {team.name}, {team.points} {get_points_string(team.points)}")
        return result 