import unittest
from io import StringIO
from unittest.mock import patch
import sys
import os
import tempfile
import random

# Add the src directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models import Team
from src.ranker import LeagueRanker, get_points_string
from src.utils import parse_match, InvalidMatchFormatError

class TestLeagueRanker(unittest.TestCase):
    def setUp(self):
        self.ranker = LeagueRanker()

    def test_parse_match(self):
        # Test various valid match formats
        test_cases = [
            ("Brazil 3, Germany 3", ("Brazil", 3, "Germany", 3)),
            ("France National Team 1, England National Team 1", 
             ("France National Team", 1, "England National Team", 1)),
            ("Spain 4, Portugal 2", ("Spain", 4, "Portugal", 2))
        ]
        for input_line, expected in test_cases:
            with self.subTest(input_line=input_line):
                result = parse_match(input_line)
                self.assertEqual(result, expected)
                
        # Test invalid formats
        with self.assertRaises(InvalidMatchFormatError):
            parse_match("Brazil 3, Germany")
            
        # Test invalid scores
        with self.assertRaises(InvalidMatchFormatError):
            parse_match("Brazil abc, Germany 3")

    def test_process_match_draw(self):
        self.ranker.process_match("Brazil 2, Germany 2")
        self.assertEqual(self.ranker.teams["Brazil"].points, 1)
        self.assertEqual(self.ranker.teams["Germany"].points, 1)

    def test_process_match_win(self):
        self.ranker.process_match("Argentina 1, England 0")
        self.assertEqual(self.ranker.teams["Argentina"].points, 3)
        self.assertEqual(self.ranker.teams["England"].points, 0)

    def test_generate_rankings(self):
        matches = [
            "Brazil 2, Germany 2",
            "Argentina 1, England 0",
            "Brazil 1, England 1",
            "Argentina 3, Germany 1",
            "Brazil 4, France 0"
        ]
        for match in matches:
            self.ranker.process_match(match)
        rankings = self.ranker.generate_rankings()
        expected = [
            "1. Argentina, 6 pts",
            "2. Brazil, 5 pts",
            "3. England, 1 pt",
            "3. Germany, 1 pt",
            "5. France, 0 pts"
        ]
        self.assertEqual(rankings, expected)

    def test_team_sorting(self):
        teams = [
            Team("Spain", 3),
            Team("Italy", 3),
            Team("Portugal", 6),
            Team("Belgium", 0)
        ]
        sorted_teams = sorted(teams)
        self.assertEqual([t.name for t in sorted_teams], ["Portugal", "Italy", "Spain", "Belgium"])

    @patch("sys.stdout", new_callable=StringIO)
    @patch("argparse.ArgumentParser.parse_args")
    def test_main_with_stdin(self, mock_args, mock_stdout):
        input_data = "Brazil 3, Germany 3\nArgentina 1, England 0\n"
        mock_args.return_value = type('obj', (), {'file': '-', 'output': None})()
        with patch("sys.stdin", StringIO(input_data)):
            from src.cli import main
            main()
        output = mock_stdout.getvalue().strip().split("\n")
        self.assertIn("1. Argentina, 3 pts", output)
        self.assertIn("2. Brazil, 1 pt", output)
        self.assertIn("2. Germany, 1 pt", output)
        self.assertIn("4. England, 0 pts", output)

    # Error Handling Tests
    @patch("sys.stderr", new_callable=StringIO)
    def test_cli_file_not_found(self, mock_stderr):
        with patch("argparse.ArgumentParser.parse_args") as mock_args:
            mock_args.return_value = type('obj', (), {'file': 'nonexistent.txt', 'output': None})()
            with self.assertRaises(SystemExit) as exc_info:
                from src.cli import main
                main()
            self.assertEqual(exc_info.exception.code, 1)
        self.assertIn("not found", mock_stderr.getvalue())

    # Output File Testing
    def test_output_file_permissions(self):
        with tempfile.NamedTemporaryFile() as tmp:
            # Make temp file read-only
            os.chmod(tmp.name, 0o400)
            
            with patch("argparse.ArgumentParser.parse_args") as mock_args:
                mock_args.return_value = type('obj', (), {'file': '-', 'output': tmp.name})()
                with patch("sys.stdin", StringIO("Brazil 1, Germany 1\n")):
                    with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
                        with self.assertRaises(SystemExit) as exc_info:
                            from src.cli import main
                            main()
                        self.assertEqual(exc_info.exception.code, 1)
                    self.assertIn("Permission denied", mock_stderr.getvalue())

    # Edge Case Rankings
    def test_all_teams_zero_points(self):
        # Test when all teams have 0 points (no goals scored)
        teams = ["Brazil", "Germany", "France", "Argentina"]
        matches = []
        for i in range(len(teams)):
            for j in range(i+1, len(teams)):
                matches.append(f"{teams[i]} 0, {teams[j]} 0")
                
        for match in matches:
            self.ranker.process_match(match)
            
        rankings = self.ranker.generate_rankings()
        # All teams should have 1 point each from draws (0-0)
        for i, team in enumerate(sorted(teams)):
            self.assertIn(f"1. {team}, 3 pts", rankings[i])  # Teams get 3 draws = 3 pts

    def test_many_teams_same_points(self):
        # Create teams all with same points
        countries = ["Brazil", "Germany", "France", "Argentina", "England", 
                    "Spain", "Italy", "Portugal", "Belgium", "Netherlands"]
        for country in countries:
            self.ranker.teams[country] = Team(name=country, points=5)
            
        rankings = self.ranker.generate_rankings()
        
        # All should have rank 1 and be sorted alphabetically
        self.assertEqual(len(rankings), 10)
        
        # Get alphabetically sorted team names for verification
        sorted_countries = sorted(countries)
        
        # Check each ranking entry
        for i, country in enumerate(sorted_countries):
            self.assertIn(country, rankings[i])
            self.assertIn("1.", rankings[i])
            self.assertIn("5 pts", rankings[i])

    # Performance Testing
    def test_performance_large_dataset(self):
        import time
        
        # Generate many matches
        countries = ["Brazil", "Germany", "France", "Argentina", "England", 
                     "Spain", "Italy", "Portugal", "Belgium", "Netherlands"]
        matches = []
        
        # Generate matches between every pair of countries multiple times
        for _ in range(1000):  # 1000 tournaments
            for i in range(len(countries)):
                for j in range(i+1, len(countries)):
                    score1, score2 = random.randint(0, 5), random.randint(0, 5)
                    matches.append(f"{countries[i]} {score1}, {countries[j]} {score2}")
        
        start_time = time.time()
        for match in matches:
            self.ranker.process_match(match)
        rankings = self.ranker.generate_rankings()
        duration = time.time() - start_time
        
        # Assert it completes in reasonable time
        self.assertLess(duration, 1.0)  # Should process matches in under 1 second
        self.assertEqual(len(rankings), 10)  # 10 countries in total

    # Testing the LRU cache functionality
    def test_get_points_string_caching(self):
        result1 = get_points_string(1)
        self.assertEqual(result1, "pt")
        
        # Call again with same argument - should use cache
        result2 = get_points_string(1)
        self.assertEqual(result2, "pt")
        
        # Different input
        result3 = get_points_string(2)
        self.assertEqual(result3, "pts")
        
        # Test a sequence of calls to ensure cache works for various inputs
        results = [get_points_string(n) for n in [3, 1, 2, 1, 3]]
        self.assertEqual(results, ["pts", "pt", "pts", "pt", "pts"])

    # Command Line Arguments Tests
    @patch("sys.stdout", new_callable=StringIO)
    def test_cli_help_output(self, mock_stdout):
        with patch("sys.argv", ["league-ranker", "--help"]):
            with self.assertRaises(SystemExit):
                from src.cli import main
                main()
        output = mock_stdout.getvalue()
        self.assertIn("Calculate league rankings", output)

if __name__ == "__main__":
    unittest.main()