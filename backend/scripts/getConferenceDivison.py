from bs4 import BeautifulSoup
import requests
import os

#Gets ConferenceID, Name, DivisonID


#Caching T
def save_html_to_file(content, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

# Function to load HTML content from a local file
def load_html_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()





def get_divisons():
    #outputs team_id, team_name
    url = "http://onlinecollegebasketball.org/index.php?searchFor=&goButton=Search&type=conference&content=search_results"

    cache_folder = "backend"
    
    cache_filename = os.path.join(cache_folder, f"ConferenceDivsions.html")
    
    
    try:
        # Try to load HTML content from the local cache
        page = load_html_from_file(cache_filename)
        
        
    except FileNotFoundError:
        # If not found, fetch the content from the URL
        page = requests.get(url)

        # Save HTML content to the local cache
        save_html_to_file(page.text, cache_filename)
        page = page.text 


    soup = BeautifulSoup(page, "html.parser")

    x = soup.find("div", {"id":"Main"}).find_all("a")

    conference_info = {}

    for index, info in enumerate(x):
        info = info.text.replace("#"," - ").split(" - ")
        
        if index <= 14:
            division_id = 1
        elif index <= 30:
            division_id = 2
        else:
            division_id = 3
        conference_id = int(info[1])
        conference_name = info[-1]

        conference_info[conference_id] = (conference_name,division_id)

        
    return conference_info

