from bs4 import BeautifulSoup
import requests
import re
import sys
import os
#sys.path.append(os.path.abspath("../scripts"))
from .helperFunctions import * #have to run like this in terminal: cd backend ->  python -m scripts.pygetPlayerInfo


#Given URL of player, it gets the measureables (Height, Weight, Wingspan, Vertical) and their skills and puts it into a hash

def split_number_and_letter(s):
    s = s.replace('↑', '')
    # Split the string into parts that contain numbers, fractions, letters, single quotes, and double quotes
    return re.findall(r'\d+|[¼½]|[^\d¼½\'"]+|[\'"]', s)

def extract_length(array):
    length = ""
    lengthArr = array[1:-4]
    for i in lengthArr:
        length += i
    
    return length

# For Height and Wingspan
def convert_to_inches(height):
    parts = height.split("'")
    if len(parts) == 2:
        feet = int(parts[0])
        inches_str = parts[1].rstrip('"').strip()  # Removing leading/trailing whitespace
        if inches_str:  # Check if inches part is not empty
            if '½' in inches_str:
                inches_str = inches_str.replace('½', '.5')
            elif '¼' in inches_str:
                inches_str = inches_str.replace('¼', '.25')
            inches = float(inches_str)
        else:
            inches = 0
    elif len(parts) == 1:
        feet = int(parts[0])
        inches = 0
    else:
        return None
    return (feet * 12) + inches

# For Vertical
def Vert_convert_to_inches(height):
    inches_str = height.rstrip('"')  # Removing the inch symbol
    if '½' in inches_str:
        inches_str = inches_str.replace('½', '.5')
    elif '¼' in inches_str:
        inches_str = inches_str.replace('¼', '.25')
    return float(inches_str)



def transform_player_data(input_data,playerURL,soup):
    # Define the mapping from input keys to required keys
    key_mapping = {
        'Age': None,  # Not used in the output
        'InsideShot': 'IS',
        'BasketballIQ': 'IQ',
        'OutsideShot': 'OS',
        'Passing': 'Pass',
        'ShootingRange': 'Rng',
        'BallHandling': 'Hnd',
        #'Weight': 'Weight',
        'Finishing': 'Fin',
        'Driving': 'Drv',
        "Rebounding": 'Reb',
        'Strength': 'Str',
        'InteriorDefense': 'IDef',
        'Speed': 'Spd',
        'PerimeterDefense': 'PDef',
        'Stamina': 'Sta',
        'Weight': 'Weight',
        "Wingspan_inches": "Wingspan_inches",
        "Height_inches" : "Height_inches",
        "Vertical_float": "Vertical_float"
    }
    # Initialize the output dictionary
    output_data = {}
    
    # Apply the mapping to transform the input dictionary
    for key, new_key in key_mapping.items():
        if new_key is not None and key in input_data:
            output_data[new_key] = input_data[key]

    output_data["Player_ID"] = int(playerURL.split("/")[-1])

    season = find_current_season()
    
    output_data["Season_ID"] = season

    pageList = soup.find("th").find_all("a")[1:]

    player_name = pageList[0].find("img")["title"].replace("Bookmark ","")

    team_code = int(pageList[-1].get("href").split("/")[-1])

    output_data["Name"] = player_name
    output_data["Team_ID"] = team_code

    return output_data



def get_player_info(playerURL):
    page = requests.get(playerURL)
    soup = BeautifulSoup(page.text, "html.parser")

    fullinfoList = soup.find("table").find_all("tr")
    for i in range(len(fullinfoList)):
        if "Age" in fullinfoList[i].text:
            start_index = i
        elif "Perimeter Defense" in fullinfoList[i].text:
            end_index = i + 1

    infoList = fullinfoList[start_index:end_index]
    player_info = {}

    for i in range(len(infoList)):
        text = infoList[i].text.strip().replace(" ", "")
        if i == 1:
            find_Outside = text.find("O")
            separated = split_number_and_letter(text[find_Outside:])
        else:
            separated = split_number_and_letter(text)

        if separated:
            

            if 'Height' in separated[0]:
                separated = separated[-4:]
            if 'Wingspan' in separated[0]:
                separated = separated[-4:]
            if 'Vertical' in separated[0]:
                separated = separated[-4:]
            
            # Handle special cases
            if 'Weight' in separated[0]:
                player_info['Weight'] = float(f"{separated[1]}")
                
                start_idx = 2
                separated[start_idx] = separated[start_idx].replace("lbs.","")

            else:
                start_idx = 0

            # Add remaining key-value pairs to the dictionary
            for j in range(start_idx, len(separated), 2):
                key = separated[j].replace(":", "")
                if j + 1 < len(separated):
                    value = separated[j + 1]
                    player_info[key] = int(value)

    player_info["Height_inches"] = convert_to_inches(extract_length(split_number_and_letter(infoList[2].text.strip().replace(" ", ""))))
    player_info["Wingspan_inches"] = convert_to_inches(extract_length(split_number_and_letter(infoList[4].text.strip().replace(" ", ""))))
    player_info["Vertical_float"] = Vert_convert_to_inches(extract_length(split_number_and_letter(infoList[5].text.strip().replace(" ", ""))))

    return transform_player_data(player_info,playerURL,soup)



#print(get_player_info("http://onlinecollegebasketball.org/player/223193"))

