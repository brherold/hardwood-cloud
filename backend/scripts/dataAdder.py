import os
import sys
import sqlite3

# Ensure backend and scripts directories are in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
for p in [BASE_DIR, SCRIPTS_DIR, ROOT_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

current_season = 2055
PostSeason = False
post_season = PostSeason
num_games = None  # target count of regular season games when PostSeason is False (or prompted)
import requests
from bs4 import BeautifulSoup

try:
    from .dbOperations import *
    from .helperFunctions import *
    from .driverSetup import *
    from .roster_schedule_reset import *
    from .getTeamGames import team_games_played
except ImportError:
    from dbOperations import *
    from helperFunctions import *
    from driverSetup import *
    from roster_schedule_reset import *
    from getTeamGames import team_games_played

import time
from app_init import *
from app_init import app
'''
If game not fully added in DB:
    1) Go to dbOperations.py and into add_game_helper function
    2) Comment out the section that checks if game already exists in DB
    3) Comment out db.session.add and db.session.commit() lines at bottom of function
    4) Run this script with the desired game ID in add_game_helper(game_ID)

'''

def get_current_max_regular_games(season_id):
    """Finds the maximum regular season games played so far by any team in this season."""
    try:
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        db_file = os.path.join(root_dir, "instance", "basketball.db")
        if os.path.exists(db_file):
            conn = sqlite3.connect(db_file)
            cur = conn.cursor()
            cur.execute("""
                SELECT MAX(GP) FROM team_avg 
                WHERE season_id = ? AND game_type = 'College' AND stat_type = 'team'
            """, (season_id,))
            row = cur.fetchone()
            conn.close()
            if row and row[0] is not None and row[0] > 0:
                return int(row[0])
    except Exception as e:
        print(f"Note detecting max games from DB: {e}")
    return None

#Gets All games from team_ID and current season
def add_games_team(team_id, PostSeason=None, num_games=None):
    count = 0

    if PostSeason is None:
        raw_post = globals().get("PostSeason", False)
    else:
        raw_post = PostSeason

    if isinstance(raw_post, str):
        is_post_season = raw_post.strip().lower() in ("true", "1", "yes", "y")
    else:
        is_post_season = bool(raw_post)

    target_count = num_games
    if not is_post_season:
        if target_count is None:
            target_count = globals().get("num_games", None)
        if target_count is None:
            prev_max = get_current_max_regular_games(current_season)
            if prev_max is not None:
                # Target count is previous day's regular count + 1 new game + 3 exhibition games = prev_max + 4 (or prev_max + 3+1)
                target_count = prev_max + 4
                globals()["num_games"] = target_count
                print(f"📊 Auto-targeting schedule game count: {target_count} (DB regular games: {prev_max} + 1 new game + 3 exhibition)")

    # Always clear schedule cache so fresh live schedule is pulled for today's new game
    delete_schedule_cache(team_id, current_season)
    # ONE app context for the entire batch
    with app.app_context():
        for game in team_games_played(team_id, current_season, is_post_season):
            if not is_post_season and target_count is not None and count >= target_count:
                print(f"🛑 Reached regular season game count ({count}/{target_count}) for team {team_id}. Stopping.")
                break

            try:
                add_game_helper(game)
                count += 1
                print(f"✅ Added game {game} for team {team_id}: Total added: {count}")

                if not is_post_season and target_count is not None and count >= target_count:
                    print(f"🛑 Reached regular season game count ({count}/{target_count}) for team {team_id}. Stopping.")
                    break

            except Exception as e:
                error_msg = str(e)
                print(f"⚠️ Error on game {game} : {error_msg}")

                # If game not played or boxscore not available -> stop for this team and move to next team
                if "Game not played yet" in error_msg or "Boxscore not available" in error_msg or "list index out of range" in error_msg:
                    print(f"🛑 Game {game} not played / box score not available. Finished with team {team_id}, moving to next team.")
                    break

                # otherwise just skip this game
                continue

    print(f"Added All {count} played games for team: {team_id}")
    print()

add_games_for_team = add_games_team
def updateTeamRoster(team_id):
    try:
        with app.app_context():
            update_team_roster_db(team_id)
        print(f"✅ Updated Team Roster and Player Skills for team: {team_id}")
        return True
    except Exception as e:
        error_msg = str(e)
        print(f"⚠️ Error updating roster for team {team_id} : {error_msg}")
        return False

#updateTeamRoster(533)
#add_games_for_team(1)

# delete_roster_cache(team_id, season_id)
# delete_schedule_cache(team_id, season_id)
#open_hardwood_home_manual()
if __name__ == "__main__":
    import argparse
    from datetime import datetime

    parser = argparse.ArgumentParser(description="Hardwood Data Adder & Automation Scheduler")
    parser.add_argument("--action", choices=["games", "rosters", "both"], default="games",
                        help="Action to perform: 'games' (daily), 'rosters' (Thu/Fri), or 'both'")
    parser.add_argument("--num-games", type=int, default=None,
                        help="Target count of regular season games (optional)")
    parser.add_argument("--post-season", action="store_true", default=False,
                        help="Scrape post season games")
    parser.add_argument("--season", type=int, default=current_season,
                        help=f"Season year (default: {current_season})")
    parser.add_argument("--team", type=int, default=None,
                        help="Single team ID to process (1-1008)")
    parser.add_argument("--start-team", type=int, default=1,
                        help="Start team ID (default: 1)")
    parser.add_argument("--end-team", type=int, default=1009,
                        help="End team ID (default: 1009)")
    parser.add_argument("--no-sync", action="store_true", default=False,
                        help="Skip syncing changes to Turso cloud database")
    args = parser.parse_args()

    start_time = datetime.now()
    print(f"[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] 🚀 Starting dataAdder with action='{args.action}'...")

    team_list = [args.team] if args.team else list(range(args.start_team, args.end_team + 1))
    print(f"Processing {len(team_list)} team(s)...")

    # Auto-calculate game count (+1 of previous day) if not explicitly passed
    target_num_games = args.num_games
    if target_num_games is None and not args.post_season and args.action in ("games", "both"):
        prev_max = get_current_max_regular_games(args.season)
        if prev_max is not None:
            # Target count is previous day's regular count + 1 new game + 3 exhibition games = prev_max + 4
            target_num_games = prev_max + 4
            print(f"📊 Previous day regular game count: {prev_max}. Setting target schedule count to {target_num_games} (+1 new game + 3 exhibition).")
        globals()["num_games"] = target_num_games

    try:
        # 1. Games
        if args.action in ("games", "both"):
            print("--- Processing Games ---")
            for team in team_list:
                add_games_team(team, PostSeason=args.post_season, num_games=target_num_games)
        # 2. Rosters
        if args.action in ("rosters", "both"):
            print("--- Processing Rosters (clearing roster caches for fresh pull) ---")
            for team in team_list:
                delete_roster_cache(team, args.season)
                updateTeamRoster(team)
    finally:
        try:
            quit_driver()
        except Exception:
            pass

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    print(f"[{end_time.strftime('%Y-%m-%d %H:%M:%S')}] ✅ Completed dataAdder in {duration:.1f}s.")

    # Auto-sync to Turso if configured
    if not args.no_sync:
        try:
            # Import turso_sync from project root
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            if root_dir not in sys.path:
                sys.path.insert(0, root_dir)
            import turso_sync
            sync_type = "games" if args.action == "games" else ("rosters" if args.action == "rosters" else "all")
            print(f"🔄 Triggering Turso cloud sync ({sync_type})...")
            turso_sync.run_sync(season_id=args.season, sync_type=sync_type)
        except Exception as e:
            print(f"⚠️ Turso sync note: {e}")