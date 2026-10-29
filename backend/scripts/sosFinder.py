from bs4 import BeautifulSoup
import requests
from datetime import datetime
import os
import glob
from .driverSetup  import *


#USE PYTHON ANACADONA 3.8.5 to RUN

#Returns Dictionary key(teamID): value (sos) of all teams and their sos (Strenghth of Schedule)

def save_html_to_file(content, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

# Function to load HTML content from a local file
def load_html_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()

# python -m scripts.sosFinder




def sos_holder():

    url= "http://onlinecollegebasketball.org/rankings/1/2/0"
    
    #Caches for day
    cache_folder = os.path.join(os.path.dirname(__file__), "..", "TeamRankings")
    cache_folder = os.path.abspath(cache_folder)
    os.makedirs(cache_folder, exist_ok=True)  # make sure folder exists
    
    month_day = datetime.now().strftime("%m-%d")
    cache_filename = os.path.join(cache_folder, f"TeamRankings{month_day}.html")
    minimum_cache_size = 300 * 1024  # 300 KB

    if not os.path.exists(cache_filename):
        existing_files = sorted(glob.glob(os.path.join(cache_folder, "TeamRankings*.html")), reverse=True)
        if existing_files and os.path.getsize(existing_files[0]) >= minimum_cache_size:
            cache_filename = existing_files[0]

    cloudflare_reset_count = 0
    while True:
        try:
            # If cache exists but is too small, nuke it and reset driver
            if os.path.exists(cache_filename) and os.path.getsize(cache_filename) < minimum_cache_size:
                os.remove(cache_filename)
                quit_driver()
                cloudflare_reset_count += 1
                raise FileNotFoundError  # force retry logic

            # Try loading from cache
            page = load_html_from_file(cache_filename)
            soup = BeautifulSoup(page, "html.parser")
            if "Verifying you are human" in soup.get_text() or "Performing security verification" in soup.get_text():
                print("CLOUDFLARE BLOCK DETECTED on team page")
                cloudflare_reset_count += 1
                raise FileNotFoundError

            # ✅ Success condition: file exists and is big enough
            if os.path.getsize(cache_filename) > minimum_cache_size:
                break

        except FileNotFoundError:
            if cloudflare_reset_count > 2:
                driver = open_hardwood_home_manual()
            elif cloudflare_reset_count > 0 and cloudflare_reset_count <= 2:
                driver = open_hardwood_home_auto()
            else:
                driver = get_driver()
            driver.get(url)

            page = driver.page_source
            save_html_to_file(page, cache_filename)


        


    soup = BeautifulSoup(page,"html")




    teamsTrArr = soup.find("table").find_all("tr")[1:]



    teamRankDic = {}
    for teamTr in teamsTrArr:
        teamID = teamTr.find_all("td")[1].find("a")["href"].split("/")[-1]
        teamRPI = float(teamTr.find_all("td")[7].text)
        teamSOS = float(teamTr.find_all("td")[8].text)
        teamRankDic[teamID] = teamSOS, teamRPI
        
    return teamRankDic

#print(sos_holder())

