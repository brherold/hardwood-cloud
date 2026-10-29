'''
cd backend
python -m scripts.getTeamConference
'''
from bs4 import BeautifulSoup
import requests
import os
import re
from .driverSetup import *
#Gets Team Conference for that Year


#Caching Team Info for the year
def save_html_to_file(content, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

# Function to load HTML content from a local file
def load_html_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()





TEAM_CONFERENCE_CACHE = {}

def get_team_conference(teamCode, seasonYear):
    cache_key = (int(teamCode), int(seasonYear))
    if cache_key in TEAM_CONFERENCE_CACHE:
        return TEAM_CONFERENCE_CACHE[cache_key]

    teamURL = "http://onlinecollegebasketball.org/team/" + str(teamCode)

    cache_folder = os.path.join(os.path.dirname(__file__), "..", "TeamConferencePage")
    cache_folder = os.path.abspath(cache_folder)
    os.makedirs(cache_folder, exist_ok=True)
    
    cache_filename = os.path.join(cache_folder, f"{teamCode}-{seasonYear}.html")

    minimum_cache_size = 8 * 1024  # 8 KB
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
                break
            else:
                raise FileNotFoundError
        except FileNotFoundError:
            if cloudflare_reset_count > 2:
                driver = open_hardwood_home_manual()
            elif cloudflare_reset_count > 0 and cloudflare_reset_count <= 2:
                driver = open_hardwood_home_auto()
            else:
                driver = get_driver()
            driver.get(teamURL)

            page = driver.page_source
            if "Verifying you are human" in page or "Performing security verification" in page:
                print("CLOUDFLARE BLOCK DETECTED on conference page")
                cloudflare_reset_count += 1
                quit_driver()
                continue

            save_html_to_file(page, cache_filename)
            break
    # Fast regex extract conference link
    m = re.search(r'href=[\'"]/conference/(\d+)[\'"]', page)
    if m:
        conf_id = int(m.group(1))
    else:
        soup = BeautifulSoup(page, "html.parser")
        conf_id = int(soup.find("div", {"id":"Main"}).find_all("a")[1]["href"].split("/")[-1])

    TEAM_CONFERENCE_CACHE[cache_key] = conf_id
    return conf_id
#print(get_team_conference(994,2050))

#cd backend -> python -m scripts.getTeamConference