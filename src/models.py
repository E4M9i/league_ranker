# models.py
# Data models for the league ranking application.

from dataclasses import dataclass

@dataclass
class Team:
    name: str
    points: int = 0

    def __lt__(self, other: 'Team') -> bool:
        # Sort by points (descending), then name (ascending)
        return (-self.points, self.name) < (-other.points, other.name) 