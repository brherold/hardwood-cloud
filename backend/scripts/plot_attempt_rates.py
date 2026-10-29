"""
Attempt Rates vs. Offensive Rating (ORtg) Graph Generator for Hardwood Analytics.
"""

import os
import sys

# Ensure root directory is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from plot_attempt_rates import generate_attempt_rates_graph, DB_PATH
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Attempt Rates vs. ORtg PNG chart.")
    parser.add_argument("-s", "--season", default="2054", help="Season year (e.g. 2054, or 'all') [default: 2054].")
    parser.add_argument("-g", "--game_type", default="College", help="Game type filter (e.g. 'College', 'Conference', 'all') [default: College].")
    parser.add_argument("-c", "--max_conf", type=int, default=100, help="Maximum conference_id (conference_id <= max_conf) [default: 100].")
    parser.add_argument("-p", "--min_gp", type=int, default=3, help="Minimum games played filter (GP >= min_gp) [default: 3].")
    parser.add_argument("-o", "--output", default="attempt_rates_vs_ortg.png", help="Output PNG file path [default: attempt_rates_vs_ortg.png].")
    parser.add_argument("-d", "--db", default=DB_PATH, help=f"Path to basketball.db [default: {DB_PATH}].")

    args = parser.parse_args()

    generate_attempt_rates_graph(
        season=args.season,
        game_type=args.game_type,
        max_conf=args.max_conf,
        min_gp=args.min_gp,
        db_path=args.db,
        output_file=args.output
    )
