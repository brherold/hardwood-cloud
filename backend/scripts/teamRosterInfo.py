from bs4 import BeautifulSoup
import requests
from .pygetPlayerInfo import *
#python -m backend.scripts.teamRosterInfo
from datetime import *
import os
from .driverSetup import *
import time
import warnings
from bs4 import GuessedAtParserWarning

warnings.filterwarnings("ignore", category=GuessedAtParserWarning)




def save_html_to_file(content, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

# Function to load HTML content from a local file
def load_html_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()

def delete_file(filename):
    if os.path.exists(filename):
        os.remove(filename)
    # Clear in-memory cache
    base = os.path.splitext(os.path.basename(filename))[0]
    if "-" in base:
        parts = base.split("-")
        try:
            TEAM_ROSTER_CACHE.pop((int(parts[0]), int(parts[1])), None)
        except Exception:
            pass
    return 





#Outputs dictionary of team w/ team_name, team_id, players and their skills using the team's roster link
TEAM_ROSTER_CACHE = {}

def team_roster_info(teamURL, season):
    teamID = int(teamURL.split("/")[-1])
    cache_key = (teamID, season)
    if cache_key in TEAM_ROSTER_CACHE:
        return TEAM_ROSTER_CACHE[cache_key]

    cache_folder = os.path.join(os.path.dirname(__file__), "..", "TeamRosterPage")
    cache_folder = os.path.abspath(cache_folder)
    os.makedirs(cache_folder, exist_ok=True)  # make sure folder exists

    teamRosterURL = "http://onlinecollegebasketball.org/roster/" + str(teamID)
    cache_filename = os.path.join(cache_folder, f"{teamID}-{season}.html")
    
    minimum_cache_size = 15 * 1024  # 15 KB
    cloudflare_reset_count = 0
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
                if "<h1" not in page or 'id="players"' not in page:
                    print(f"Invalid/corrupted cache detected for team {teamID}, removing...")
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
            driver.get(teamRosterURL)

            page = driver.page_source
            if "Verifying you are human" in page or "Performing security verification" in page:
                print("CLOUDFLARE BLOCK DETECTED on roster page")
                cloudflare_reset_count += 1
                quit_driver()
                continue

            # Give time for the roster page elements to be present
            for _ in range(3):
                if "<h1" in page and ('id="players"' in page or "No players found" in page):
                    break
                time.sleep(1)
                page = driver.page_source

            # Check if page is incomplete or Cloudflare challenge HTML
            if len(page.encode("utf-8")) < minimum_cache_size or "<h1" not in page:
                print(f"⚠️ Incomplete roster page or block detected for team {teamID} (size: {len(page)}), retrying...")
                cloudflare_reset_count += 1
                quit_driver()
                time.sleep(1)
                if cloudflare_reset_count > 10:
                    raise ValueError(f"Could not load valid roster page for team {teamID} after {cloudflare_reset_count} attempts.")
                continue

            save_html_to_file(page, cache_filename)
            break
    try:
        teamRosterSoup = BeautifulSoup(page, "lxml")
    except Exception:
        teamRosterSoup = BeautifulSoup(page, "html.parser")

    #Finds Name of Team
    h1_tag = teamRosterSoup.find("h1")
    if not h1_tag:
        if os.path.exists(cache_filename):
            os.remove(cache_filename)
        raise ValueError(f"Team {teamID} roster page has no <h1> tag.")

    teamName = h1_tag.text.strip("Roster")[:-1]
    teamData = {"teamName": teamName, "teamID": teamID, "players":[]}

    players_table = teamRosterSoup.find("table", id="players")
    if not players_table:
        print(f"⚠️ No players table found for team {teamID} ({teamName})")
        return teamData

    playerRosterList = players_table.find_all("tr")[1:]


    for index, playerSoup in enumerate(playerRosterList):
        '''
        teamData["players"].append({
            "name": player[0].find_all("td")[0]
        })
        '''
        player = playerSoup.find_all("td")[3:]

        playerAthletics = player[0].find("a").get("alt").split("\n")

        teamData["players"].append({
            "name": player[0].text[:-1],
            "playerID": int(playerSoup.find_all("td")[3].find("a").get("href")[8:]),
            "height": convert_to_inches(player[1].text),
            "weight": float(playerAthletics[1].split(":")[1].split(" ")[2]),
            "wingspan": convert_to_inches(playerAthletics[2].split(":")[1][2:]),
            "vertical": Vert_convert_to_inches(playerAthletics[3].split(":")[1][2:]),
            "Pos": player[16].text,
            "Class": player[20].text,
            "IS": int(player[2].text),
            "OS": int(player[3].text),
            "Rng": int(player[4].text),
            "Fin": int(player[5].text),
            "Reb": int(player[6].text),
            "IDef": int(player[7].text),
            "PDef": int(player[8].text),
            "IQ": int(player[9].text),
            "Pass": int(player[10].text),
            "Hnd": int(player[11].text),
            "Drv": int(player[12].text),
            "Str": int(player[13].text),
            "Spd": int(player[14].text),
            "Sta": int(player[15].text),
            "SI": int(player[17].text),
            "POT": int(player[18].text),
            "Stars": int(player[19].text) if player[19].text != "-" else 0
            
        })

        
    
    TEAM_ROSTER_CACHE[cache_key] = teamData
    return teamData

#run in terminal: python -m scripts.teamRosterInfo

#print(team_roster_info("http://onlinecollegebasketball.org/team/533",2051))


