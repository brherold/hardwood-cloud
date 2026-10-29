import os
import sys
import re
import time
from bs4 import BeautifulSoup

# Ensure backend directory is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from .helperFunctions import *
from .driverSetup import *
from app_init import *

def team_games_played(team_id, current_season, post_season):
    #Finds all the games played in current season for inputted Team
    teamScheduleUrl = "http://onlinecollegebasketball.org/schedule/" + str(team_id) + "/" + str(current_season)

    
    cache_folder = os.path.join(os.path.dirname(__file__), "..", "TeamsHTML")
    cache_folder = os.path.abspath(cache_folder)
    os.makedirs(cache_folder, exist_ok=True)  # make sure folder exists

    
    cache_filename = os.path.join(cache_folder, f"{team_id}-{current_season}.html")
    

    minimum_cache_size = 15 * 1024  # 5 KB
    cloudflare_reset_count = 0
    
    #If in exhibition/non-conf/conf games currently

    while True:
        try:
            if os.path.exists(cache_filename):
                if os.path.getsize(cache_filename) < minimum_cache_size:
                    os.remove(cache_filename)
                    quit_driver()
                    cloudflare_reset_count += 1
                    raise FileNotFoundError

                page = load_html_from_file(cache_filename)
                if "Verifying you are human" in page or "Performing security verification" in page:
                    print("CLOUDFLARE BLOCK DETECTED on team page")
                    cloudflare_reset_count += 1
                    os.remove(cache_filename)
                    raise FileNotFoundError
                break
            else:
                raise FileNotFoundError
        except FileNotFoundError:
            if cloudflare_reset_count > 7:
                driver = open_hardwood_home_manual()
            elif cloudflare_reset_count > 0 and cloudflare_reset_count <= 7:
                driver = open_hardwood_home_auto()
            else:
                driver = get_driver()
            driver.get(teamScheduleUrl)

            page = driver.page_source
            if "Verifying you are human" in page or "Performing security verification" in page:
                print("CLOUDFLARE BLOCK DETECTED on schedule page")
                cloudflare_reset_count += 1
                quit_driver()
                continue

            save_html_to_file(page, cache_filename)
            break
    # Fast regex extraction of game codes from schedule table
    raw_games = re.findall(r'href=[\'"]/game/(\d+)[\'"]', page)
    seen = set()
    gameList = []
    for g in raw_games:
        if g not in seen:
            seen.add(g)
            gameList.append(g)
    
    return gameList


#cd backend -> python -m scripts.getTeamGames
#print(team_games_played(533,2050, False))

