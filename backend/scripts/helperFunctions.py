from bs4 import BeautifulSoup
import requests
import re
def save_html_to_file(content, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

def load_html_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()

def find_current_season(): 
    url = "http://onlinecollegebasketball.org/schedule/1"

    page = requests.get(url)
    print(page)
    soup = BeautifulSoup(page.text, "html.parser")

    return int(soup.find("h1").text.split(" ")[0])


'''
def team_games_played(team_id):
    #Finds all the games played in current season for inputted Team
    teamScheduleUrl = "http://onlinecollegebasketball.org/schedule/" + str(team_id)

    page = requests.get(teamScheduleUrl)
    scheduleSoup = BeautifulSoup(page.text,"html")

    columnList = scheduleSoup.find_all("tr")

    gameList = []
    for row in columnList:
        rowData = row.find_all("td")
        if len(rowData) == 8 and rowData[5].text != "NPY":
            gameList.append("http://onlinecollegebasketball.org" + rowData[5].find("a").get("href"))
    return gameList
'''
