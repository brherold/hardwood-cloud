#updated with player defense and uses playerCode instead of playername (useful for same name players)


from bs4 import BeautifulSoup

import requests
import re
import os
import html
import unicodedata
from datetime import datetime
from .driverSetup import *

import warnings
from bs4 import GuessedAtParserWarning

warnings.filterwarnings("ignore", category=GuessedAtParserWarning)

# Shot distance bounds for each shot_specified
shot_bounds = {
    "three_pointer": (21.0, float('inf')),
    "corner":        (21.0, float('inf')),
    "jumper":        (8.0,  16),
    "fadeaway":      (15.0,  20.0),
    "postup":        (1,  2),
    "layup":         (0.0,  1.0),
    "dunk":          (0.0,  2.0),
    "tip-in":        (0.0,  0),
    "inside":        (3,  12),
    "block":         (1, 2)
}

ideal_dist = {
    "three_pointer": 22.0,
    "corner":        22.0,
    "jumper":        12.0,
    "fadeaway":      18.0,
    "postup":        1.0,
    "layup":         0.0,
    "dunk":          1.0,
    "tip-in":        0.0,
    "inside":        6.0,
    "block":         1.0
}


def save_html_to_file(content, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)


# Function to load HTML content from a local file
def load_html_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()


def clean_text_name(text: str) -> str:
    text = html.unescape(text)
    char_map = {
        'ø': 'o', 'Ø': 'O',
        'æ': 'ae', 'Æ': 'Ae',
        'ß': 'ss',
        'ł': 'l', 'Ł': 'L',
        'đ': 'd', 'Đ': 'D',
        'ð': 'd', 'Ð': 'D',
        'þ': 'th', 'Þ': 'Th',
        'ı': 'i', 'İ': 'I',
    }
    for k, v in char_map.items():
        text = text.replace(k, v)
    text = "".join(
        c for c in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(c)
    )
    for ch in [".", "'", "`", "’", "‘"]:
        text = text.replace(ch, "")
    return text.strip()


def fast_extract_team_shots(page, team_code):
    fn_header = f"function myFunction_t{team_code}("
    idx = page.find(fn_header)
    if idx == -1:
        fn_header2 = f"function myFunction_t{team_code} "
        idx = page.find(fn_header2)
    if idx == -1:
        return []
    end_idx = page.find("</script>", idx)
    if end_idx == -1:
        end_idx = len(page)
    stext = page[idx:end_idx]

    shots = []
    for line in stext.split('\\'):
        if 'shot clock' in line:
            m = re.search(r'(1st Half|2nd Half|2nd Overtime|3rd Overtime|4th Overtime|Overtime\d*|OT\d*)\s+(\d+):(\d+):', line)
            if m:
                half_str = m.group(1).strip()
                mins = int(m.group(2))
                secs = int(m.group(3))
                rest = line[m.end():].strip()
                parts = re.split(r'\s+-\s+(?=made shot|missed shot)', rest, maxsplit=1)
                if len(parts) == 2:
                    player = clean_text_name(parts[0]).title()
                    info = parts[1]
                    d_m = re.search(r'shot from (\d+) (?:feet|foot)', info)
                    dist = int(d_m.group(1)) if d_m else None

                    if '1st' in half_str and 'OT' not in half_str and 'Overtime' not in half_str:
                        half_num = 1
                    elif '2nd' in half_str and 'OT' not in half_str and 'Overtime' not in half_str:
                        half_num = 2
                    elif '2nd' in half_str or 'OT2' in half_str:
                        half_num = 4
                    elif '3rd' in half_str or 'OT3' in half_str:
                        half_num = 5
                    elif '4th' in half_str or 'OT4' in half_str:
                        half_num = 6
                    else:
                        half_num = 3

                    made = "made shot" in info
                    clock_m = re.search(r'shot clock (\d+)', info)
                    shot_clock = int(clock_m.group(1)) if clock_m else None
                    def_m = re.search(r'defended by ([^\[]+)', info)
                    defender = clean_text_name(def_m.group(1).strip()).title() if def_m else None

                    shots.append({
                        'half': half_num,
                        'time_secs': mins * 60 + secs,
                        'time_str': f"{mins}:{secs:02d}",
                        'player': player,
                        'dist': dist,
                        'made': made,
                        'defender': defender,
                        'shot_clock': shot_clock,
                        'info': info,
                        'used': False
                    })
    unique_shots = []
    for s in shots:
        if not unique_shots or (s['half'], s['time_secs'], s['player'], s['dist'], s['made']) != (unique_shots[-1]['half'], unique_shots[-1]['time_secs'], unique_shots[-1]['player'], unique_shots[-1]['dist'], unique_shots[-1]['made']):
            unique_shots.append(s)
    return unique_shots


def get_valid_shot_sentences(game_event):
    sentences = [s.strip() for s in re.split(r'[\.\!\?]', game_event) if s.strip()]
    shot_action_patterns = [
        r'\bshoots\b',
        r'\blays\s+it\s+up\b',
        r'\blayup\b',
        r'\blay\s+it\s+up\b',
        r'\bwith\s+a\s+fadeaway\b',
        r'\bfadeaway\s+jumper\b',
        r'\bshoots\s+a\s+jumper\b',
        r'\bjump\s+shot\b',
        r'\bjumper\s+from\b',
        r'\bgoes\s+for\s+the\s+dunk\b',
        r'\battempts\s+to\s+dunk\b',
        r'\bdunks\s+it\b',
        r'\bdunks\b',
        r'\bslam\s+dunk\b',
        r'\btips\s+it\s+in\b',
        r'\btips\s+it\b',
        r'\bshoots\s+a\s+floater\b',
        r'\bwith\s+a\s+floater\b',
        r'\bfloater\b',
        r'\bhook\s+shot\b',
        r'\bwith\s+a\s+hook\b'
    ]
    confirmation_keywords = ["shot goes in", "slam dunk", "tips it in", "tips it", "shot misses", "blocks the shot", "blocked", "air ball"]
    made_keywords = ["shot goes in", "slam dunk", "tips it in", "tips it"]
    charge_keywords = ["offensive foul", "charged with the foul", "charge", "charging"]
    standalone_confirmations = {"slam dunk", "shot goes in", "the shot misses", "shot misses", "the shot goes in"}

    shot_sentences = []
    for idx, sentence in enumerate(sentences):
        s_lower = sentence.lower()
        if s_lower in standalone_confirmations:
            continue
        if any(re.search(pat, s_lower) for pat in shot_action_patterns):
            window_text = ' '.join([sentences[j].lower() for j in range(idx, min(idx + 3, len(sentences)))])

            is_charge = any(ck in window_text for ck in charge_keywords) and not any(mk in window_text for mk in made_keywords)
            if is_charge:
                continue

            has_conf = any(ck in window_text for ck in confirmation_keywords)
            has_on_shot = "on the shot" in window_text or "fouls" in window_text
            has_made = any(mk in window_text for mk in made_keywords)

            is_valid = False
            if has_conf:
                is_valid = True
            elif has_on_shot and not has_made:
                is_valid = False
            else:
                is_valid = True

            if is_valid:
                shot_sentences.append((sentence, s_lower))

    return shot_sentences


def extract_shooter(sentence, offensive_players):
    s_clean = sentence.replace("!", " ").replace(".", " ").replace(",", " ")
    best_player = None
    best_pos = 999999
    for p_name, p_code in offensive_players:
        last_name = p_name.split()[-1]
        pattern = rf'\b(?:{re.escape(p_name)}|{re.escape(last_name)})\b'
        m = re.search(pattern, s_clean)
        if not m:
            m = re.search(rf'\b{re.escape(p_name)}\b', s_clean, re.IGNORECASE)
        if m:
            if m.start() < best_pos:
                best_pos = m.start()
                best_player = p_name
    return best_player


def determine_shot_outcome_for_sentence(shot_sentence, game_event):
    sentences = [s.strip() for s in re.split(r'[\.\!\?]', game_event) if s.strip()]
    shot_s_lower = shot_sentence.lower()

    if any(k in shot_s_lower for k in ["tips it in", "tips it", "slam dunk"]):
        return True

    idx = -1
    for i, s in enumerate(sentences):
        if shot_s_lower in s.lower() or s.lower() in shot_s_lower:
            idx = i
            break

    if idx != -1:
        for j in range(idx + 1, min(idx + 3, len(sentences))):
            s_next = sentences[j].lower()
            if any(mk in s_next for mk in ["shot goes in", "slam dunk"]):
                return True
            if any(mk in s_next for mk in ["shot misses", "air ball", "blocks the shot", "blocked"]):
                return False
            if any(kw in s_next for kw in ["shoots", "lays it up", "tips it", "dunks"]):
                break

    return None


def extract_drive_shot(game_event, has_fg):
    if not has_fg:
        return False
    sentences = [s.strip() for s in re.split(r'[\.\!\?]', game_event) if s.strip()]
    if not sentences:
        return False
    shot_action_patterns = [
        r'\bshoots\b', r'\blays\s+it\s+up\b', r'\blayup\b', r'\blay\s+it\s+up\b',
        r'\bwith\s+a\s+fadeaway\b', r'\bfadeaway\s+jumper\b', r'\bshoots\s+a\s+jumper\b',
        r'\bjump\s+shot\b', r'\bgoes\s+for\s+the\s+dunk\b', r'\battempts\s+to\s+dunk\b',
        r'\bdunks\s+it\b', r'\bdunks\b', r'\bslam\s+dunk\b', r'\btips\s+it\b',
        r'\bfloater\b', r'\bair\s+ball\b'
    ]
    shot_sentence_idx = -1
    for idx, sentence in enumerate(sentences):
        text_lower = sentence.lower()
        if any(re.search(pat, text_lower) for pat in shot_action_patterns):
            shot_sentence_idx = idx
            break
    if shot_sentence_idx == -1:
        return False
    check_indices = []
    if shot_sentence_idx > 0:
        check_indices.append(shot_sentence_idx - 1)
    check_indices.append(shot_sentence_idx)
    for c_idx in check_indices:
        text_lower = sentences[c_idx].lower()
        if "tries to drive" in text_lower or "try to drive" in text_lower:
            return False
        if re.search(r'\bdrives?\s+(?:down|to|by|into|past)\b', text_lower) or re.search(r'\bdrive\s+to\s+the\s+basket\b', text_lower):
            return True
    return False


def gameAnalyzer(gameURL):
    cache_folder = os.path.join(os.path.dirname(__file__), "..", "GamesHTML")
    cache_folder = os.path.abspath(cache_folder)
    os.makedirs(cache_folder, exist_ok=True)  # make sure folder exists

    gameURLCode = gameURL.split("/")[-1].replace(".html", "").replace(".htm", "")
    local_cache_filename = os.path.join(cache_folder, f"{gameURLCode}.html")
    read_cache_filename = None

    minimum_cache_size = 5 * 1024  # 5 KB

    possible_cache_folders = [
        cache_folder,
        r"D:\Hardwood\GamesHTML_1",
        r"D:\Hardwood\GamesHTML_2",
        r"D:\Hardwood\GamesHTML",
    ]
    for folder in possible_cache_folders:
        if os.path.isdir(folder):
            cand = os.path.join(folder, f"{gameURLCode}.html")
            if os.path.exists(cand) and os.path.getsize(cand) >= minimum_cache_size:
                read_cache_filename = cand
                break
            cand_htm = os.path.join(folder, f"{gameURLCode}.htm")
            if os.path.exists(cand_htm) and os.path.getsize(cand_htm) >= minimum_cache_size:
                read_cache_filename = cand_htm
                break

    cloudflare_reset_count = 0 
    while True:
        try:
            if read_cache_filename and os.path.exists(read_cache_filename):
                page = load_html_from_file(read_cache_filename)
                soup = BeautifulSoup(page, "html.parser")
                if "Verifying you are human" in soup.get_text() or "Performing security verification" in soup.get_text():
                    print("CLOUDFLARE BLOCK DETECTED on team page")
                    cloudflare_reset_count += 1
                    if read_cache_filename.startswith(cache_folder):
                        os.remove(read_cache_filename)
                    raise FileNotFoundError
                break
            elif os.path.exists(local_cache_filename):
                if os.path.getsize(local_cache_filename) < minimum_cache_size:
                    page = load_html_from_file(local_cache_filename)
                    soup = BeautifulSoup(page, "html.parser")
                    if "Game not played yet" in soup.get_text():
                        break
                    os.remove(local_cache_filename)
                    quit_driver()
                    cloudflare_reset_count += 1
                    raise FileNotFoundError

                page = load_html_from_file(local_cache_filename)
                soup = BeautifulSoup(page, "html.parser")
                if "Verifying you are human" in soup.get_text() or "Performing security verification" in soup.get_text():
                    print("CLOUDFLARE BLOCK DETECTED on team page")
                    cloudflare_reset_count += 1
                    os.remove(local_cache_filename)
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
            driver.get(gameURL)

            page = driver.page_source
            save_html_to_file(page, local_cache_filename)
    soup = BeautifulSoup(page, "html.parser")
    infoList = soup.find_all("td", class_="left")

    gameData = {
        "awayTeam": {
            "name": infoList[1].text.replace("\xa0", " ").strip(),
            "teamCode": (infoList[1].find("a").get("href")).split("/")[2],
            "outcome": 0,
            "stats": {"Min": 0, "FG": [0,0], "3P": [0,0], "FT": [0,0], "PTS": 0, "Off": 0, "Reb": 0, "AST": 0, "STL": 0, "BLK": 0, "TO": 0, "PF": 0, "+/-": 0, "DIST": 0, "PITP": 0, "FBP": 0, "FD": 0, "Fat": "", "Poss": 0, "OPoss": 0, "OPTS": 0, "OFG": [0,0], "O3P": [0,0]},
            "players": [],
            "totalShots": {"Finishing": [0, 0], "Inside Shot": [0, 0], "Mid-Range": [0, 0], "3-Pointer": [0, 0]},
            "shot_distance": {"0-6": [0,0], "7-20": [0,0], "21+": [0,0]},
            "totalDefense": {"Finishing": [0, 0], "Inside Shot": [0, 0], "Mid-Range": [0, 0], "3-Pointer": [0, 0], "Turnovers": [0, 0]},
            "defense": {
                "man-to-man": {"Finishing": [0, 0], "Inside Shot": [0, 0], "Mid-Range": [0, 0], "3-Pointer": [0, 0], "Turnovers": [0, 0]},
                "man-to-man defense packed": {"Finishing": [0, 0], "Inside Shot": [0, 0], "Mid-Range": [0, 0], "3-Pointer": [0, 0], "Turnovers": [0, 0]},
                "man-to-man defense extended": {"Finishing": [0, 0], "Inside Shot": [0, 0], "Mid-Range": [0, 0], "3-Pointer": [0, 0], "Turnovers": [0, 0]},    
                "zone": {"Finishing": [0, 0], "Inside Shot": [0, 0], "Mid-Range": [0, 0], "3-Pointer": [0, 0], "Turnovers": [0, 0]},
                "zone defense packed": {"Finishing": [0, 0], "Inside Shot": [0, 0], "Mid-Range": [0, 0], "3-Pointer": [0, 0], "Turnovers": [0, 0]},
                "zone defense extended": {"Finishing": [0, 0], "Inside Shot": [0, 0], "Mid-Range": [0, 0], "3-Pointer": [0, 0], "Turnovers": [0, 0]},
                "pressure": {"Finishing": [0, 0], "Inside Shot": [0, 0], "Mid-Range": [0, 0], "3-Pointer": [0, 0], "Turnovers": [0, 0]},
                "transition": {"Finishing": [0, 0], "Inside Shot": [0, 0], "Mid-Range": [0, 0], "3-Pointer": [0, 0], "Turnovers": [0, 0]},
                "half-court": {"Finishing": [0, 0], "Inside Shot": [0, 0], "Mid-Range": [0, 0], "3-Pointer": [0, 0], "Turnovers": [0, 0]}
            }
        },
        "homeTeam": {
            "name": infoList[2].text.replace("\xa0", " ").strip(),
            "teamCode": (infoList[2].find("a").get("href")).split("/")[2],
            "outcome": 0,
            "stats": {"Min": 0, "FG": [0,0], "3P": [0,0], "FT": [0,0], "PTS": 0, "Off": 0, "Reb": 0, "AST": 0, "STL": 0, "BLK": 0, "TO": 0, "PF": 0, "+/-": 0, "DIST": 0, "PITP": 0, "FBP": 0, "FD": 0, "Fat": "", "Poss": 0, "OPoss": 0, "OPTS": 0, "OFG": [0,0], "O3P": [0,0]},
            "players": [],
            "totalShots": {"Finishing": [0, 0], "Inside Shot": [0, 0], "Mid-Range": [0, 0], "3-Pointer": [0, 0]},
            "shot_distance": {"0-6": [0,0], "7-20": [0,0], "21+": [0,0]},
            "totalDefense": {"Finishing": [0, 0], "Inside Shot": [0, 0], "Mid-Range": [0, 0], "3-Pointer": [0, 0], "Turnovers": [0, 0]},
            "defense": {
                "man-to-man": {"Finishing": [0, 0], "Inside Shot": [0, 0], "Mid-Range": [0, 0], "3-Pointer": [0, 0], "Turnovers": [0, 0]},
                "man-to-man defense packed": {"Finishing": [0, 0], "Inside Shot": [0, 0], "Mid-Range": [0, 0], "3-Pointer": [0, 0], "Turnovers": [0, 0]},
                "man-to-man defense extended": {"Finishing": [0, 0], "Inside Shot": [0, 0], "Mid-Range": [0, 0], "3-Pointer": [0, 0], "Turnovers": [0, 0]},    
                "zone": {"Finishing": [0, 0], "Inside Shot": [0, 0], "Mid-Range": [0, 0], "3-Pointer": [0, 0], "Turnovers": [0, 0]},
                "zone defense packed": {"Finishing": [0, 0], "Inside Shot": [0, 0], "Mid-Range": [0, 0], "3-Pointer": [0, 0], "Turnovers": [0, 0]},
                "zone defense extended": {"Finishing": [0, 0], "Inside Shot": [0, 0], "Mid-Range": [0, 0], "3-Pointer": [0, 0], "Turnovers": [0, 0]},
                "pressure": {"Finishing": [0, 0], "Inside Shot": [0, 0], "Mid-Range": [0, 0], "3-Pointer": [0, 0], "Turnovers": [0, 0]},
                "transition": {"Finishing": [0, 0], "Inside Shot": [0, 0], "Mid-Range": [0, 0], "3-Pointer": [0, 0], "Turnovers": [0, 0]},
                "half-court": {"Finishing": [0, 0], "Inside Shot": [0, 0], "Mid-Range": [0, 0], "3-Pointer": [0, 0], "Turnovers": [0, 0]}
            }
        }
    }

    # Map player codes and full names from player scripts (myFunction_p...)
    player_dic = {}
    code_to_name = {}
    for m in re.finditer(r'function myFunction_p(\d+)\(\)[^\{]*\{.*?font-weight:bold;[^>]*>([^<]+)</span>', page, re.DOTALL):
        p_code = m.group(1)
        p_name = clean_text_name(m.group(2).strip()).title()
        player_dic[p_name] = p_code
        player_dic[m.group(2).strip()] = p_code
        code_to_name[p_code] = p_name

    curTeam = "awayTeam"
    infoListPlayers = infoList[4:]  # cuts it to the first player in BoxScore
    name_map = {}
    team_roster_tuples = {"awayTeam": [], "homeTeam": []}

    for i in range(len(infoListPlayers)):
        td = infoListPlayers[i]
        if td.text.strip() == "Total":
            if curTeam == "awayTeam":
                curTeam = "homeTeam"
            continue
        if len(td.text.split("\xa0")) > 1:
            raw_name = " ".join(td.text.split("\xa0")[0:-1])[3:].strip()
            name = clean_text_name(raw_name).title()
            playerCode = td.find("a").get("href").split("/")[2]
            position = td.text.split("\xa0")[1:][-1]

            full_name = code_to_name.get(playerCode, name)
            player_dic[full_name] = playerCode
            player_dic[name] = playerCode
            name_map[raw_name] = full_name
            name_map[name] = full_name
            name_map[full_name] = full_name

            team_roster_tuples[curTeam].append((full_name, playerCode))

            # Append player dictionary
            gameData[curTeam]["players"].append({
                "name": full_name,
                "position": position.upper(),
                "playerCode": playerCode,
                "shots": {"Finishing": [0, 0], "Inside Shot": [0, 0], "Mid-Range": [0, 0], "3-Pointer": [0, 0]},
                "shot_distance": {"0-6": [0,0], "7-20": [0,0], "21+": [0,0]},
                "defense": {"Finishing": [0, 0], "Inside Shot": [0, 0], "Mid-Range": [0, 0], "3-Pointer": [0, 0]}, 
                "driving": [0, 0], 
                "stats": {"Start": 0, "Min": 0, "FG": [0,0], "3P": [0,0], "FT": [0,0], "PTS": 0, "Off": 0, "Reb": 0, "AST": 0, "STL": 0, "BLK": 0, "TO": 0, "PF": 0, "+/-": 0, "DIST": 0, "PITP": 0, "FBP": 0, "FD": 0, "Fat": "", "Poss": 0, "OPoss": 0, "OPTS": 0, "OFG": [0,0], "O3P": [0,0]},
                "pos_min": {"PG": 0, "SG": 0, "SF": 0, "PF": 0, "C": 0}
            })

    # Adds player box score stats
    statsInfoArr = soup.find_all("table", class_="box-score")[-1].find_all("tr")[3:]
    awayPlayerCount = 0
    for index, line in enumerate(statsInfoArr):
        if any(char.isalpha() for char in line.text):
            if statsInfoArr[index + 1].text and not statsInfoArr[index + 1].text[0].isdigit():
                break
            awayPlayerCount += 1

    playerTeamLines = []
    for i in statsInfoArr:
        if (i.text and i.text[0].isdigit()) or "Total" in i.text:
            playerTeamLines.append(i)

    curTeam = "awayTeam"
    for index, string in enumerate(playerTeamLines):
        statList = string.find_all("td")[3:]
        minCheck = int(statList[0].text)
        if minCheck < 200:
            playerID = string.find("a").get("href").split("/")[-1]
            for player in gameData[curTeam]["players"]:
                position_mins = statList[0].get("title")
                pos_min_split = position_mins.split(" ")
                if player["playerCode"] == playerID:
                    if curTeam == "awayTeam":
                        player["stats"]["Start"] = 1 if index + 1 <= 5 else 0
                    else:
                        player["stats"]["Start"] = 1 if index - awayPlayerCount <= 5 else 0
                    
                    player["stats"]["Min"] = int(statList[0].text)
                    player["stats"]["FG"][0] = int(statList[1].text.split("-")[0])
                    player["stats"]["FG"][1] = int(statList[1].text.split("-")[1])
                    player["stats"]["3P"][0] = int(statList[2].text.split("-")[0])
                    player["stats"]["3P"][1] = int(statList[2].text.split("-")[1])
                    player["stats"]["FT"][0] = int(statList[3].text.split("-")[0])
                    player["stats"]["FT"][1] = int(statList[3].text.split("-")[1])
                    player["stats"]["PTS"] = int(statList[4].text)
                    player["stats"]["Off"] = int(statList[5].text)
                    player["stats"]["Reb"] = int(statList[6].text)
                    player["stats"]["AST"] = int(statList[7].text)
                    player["stats"]["STL"] = int(statList[8].text)
                    player["stats"]["BLK"] = int(statList[9].text)

                    if "-" in statList[10].text:
                        player["stats"]["TO"] = int(statList[11].text)
                        player["stats"]["PF"] = int(statList[12].text)
                        player["stats"]["+/-"] = int(statList[13].text)                         
                        try: player["stats"]["DIST"] = float(statList[14].text)
                        except: player["stats"]["DIST"] = "-"                                       
                        player["stats"]["PITP"] = int(statList[15].text)
                        player["stats"]["FBP"] = int(statList[16].text)
                        player["stats"]["FD"] = int(statList[17].text)
                        player["stats"]["Fat"] = statList[18].text
                    else:
                        player["stats"]["TO"] = int(statList[10].text)
                        player["stats"]["PF"] = int(statList[11].text)
                        player["stats"]["+/-"] = int(statList[12].text)                         
                        try: player["stats"]["DIST"] = float(statList[13].text)
                        except: player["stats"]["DIST"] = "-"                                       
                        player["stats"]["PITP"] = int(statList[14].text)
                        player["stats"]["FBP"] = int(statList[15].text)
                        player["stats"]["FD"] = int(statList[16].text)
                        player["stats"]["Fat"] = statList[17].text                
                    
                    player["pos_min"]["PG"] = int(pos_min_split[1])
                    player["pos_min"]["SG"] = int(pos_min_split[4])
                    player["pos_min"]["SF"] = int(pos_min_split[7])
                    player["pos_min"]["PF"] = int(pos_min_split[10])
                    player["pos_min"]["C"] = int(pos_min_split[13])
        else:
            team = gameData[curTeam]
            team["stats"]["Min"] = int(statList[0].text)
            team["stats"]["FG"][0] = int(statList[1].text.split("-")[0])
            team["stats"]["FG"][1] = int(statList[1].text.split("-")[1])
            team["stats"]["3P"][0] = int(statList[2].text.split("-")[0])
            team["stats"]["3P"][1] = int(statList[2].text.split("-")[1])
            team["stats"]["FT"][0] = int(statList[3].text.split("-")[0])
            team["stats"]["FT"][1] = int(statList[3].text.split("-")[1])
            team["stats"]["PTS"] = int(statList[4].text)
            team["stats"]["Off"] = int(statList[5].text)
            team["stats"]["Reb"] = int(statList[6].text)
            team["stats"]["AST"] = int(statList[7].text)
            team["stats"]["STL"] = int(statList[8].text)
            team["stats"]["BLK"] = int(statList[9].text)

            if "-" in statList[10].text:
                team["stats"]["TO"] = int(statList[11].text)
                team["stats"]["PF"] = int(statList[12].text)
                team["stats"]["+/-"] = int(statList[13].text)                         
                try: team["stats"]["DIST"] = float(statList[14].text)
                except: team["stats"]["DIST"] = "-"    
                team["stats"]["PITP"] = int(statList[15].text)
                team["stats"]["FBP"] = int(statList[16].text)
                team["stats"]["FD"] = int(statList[17].text)
                team["stats"]["Fat"] = statList[18].text
            else:
                team["stats"]["TO"] = int(statList[10].text)
                team["stats"]["PF"] = int(statList[11].text)
                team["stats"]["+/-"] = int(statList[12].text)                         
                try: team["stats"]["DIST"] = float(statList[13].text)
                except: team["stats"]["DIST"] = "-"    
                team["stats"]["PITP"] = int(statList[14].text)
                team["stats"]["FBP"] = int(statList[15].text)
                team["stats"]["FD"] = int(statList[16].text)
                team["stats"]["Fat"] = statList[17].text
        
        if index + 1 > awayPlayerCount:
            curTeam = "homeTeam"

    # Box score logs
    boxscore_divs = soup.find_all("div", id="Boxscore")
    playbyText = boxscore_divs[1].text
    gameArr = playbyText.split("\n")

    x = boxscore_divs[1].get_text(separator="\n")
    split_content = re.split(r'\n|:', x)
    away_team_name = split_content[8].strip()
    home_team_name = split_content[12].strip()
    gameData["awayTeam"]["name"] = away_team_name
    gameData["homeTeam"]["name"] = home_team_name

    # Extract team script shots
    team_shots = {
        "awayTeam": fast_extract_team_shots(page, gameData["awayTeam"]["teamCode"]),
        "homeTeam": fast_extract_team_shots(page, gameData["homeTeam"]["teamCode"])
    }
    team_pointers = {"awayTeam": 0, "homeTeam": 0}

    # Parse play-by-play events
    name_pattern = re.compile(r'\b(' + '|'.join(re.escape(k) for k in sorted(name_map.keys(), key=len, reverse=True)) + r')\b') if name_map else None
    parsed_events_meta = []
    cur_half = 1
    for string in gameArr[10:]:
        string_str = string.strip()
        if not string_str:
            continue
        if "2nd Half" in string_str:
            cur_half = 2
            continue
        elif "Overtime" in string_str:
            if cur_half >= 3:
                cur_half += 1
            else:
                cur_half = 3
            continue
        if "Tip-off" in string_str or ":" not in string_str or "Game Event" in string_str:
            continue

        m_t = re.search(r'(\d+):(\d+)', string_str)
        t_secs = (int(m_t.group(1)) * 60 + int(m_t.group(2))) if m_t else None

        clean_str = string_str.replace("!", ".")
        dash = "-"
        index = 0
        while index < len(clean_str) and dash != clean_str[index]:
            index += 1
        if index + 2 < len(clean_str):
            clean_str = clean_str[index + 2:]

        event_team_prefix = clean_str.split(":")[0].strip()
        if event_team_prefix == home_team_name:
            team_side = "homeTeam"
            event_body = clean_str[len(event_team_prefix) + 1:].strip()
        elif event_team_prefix == away_team_name:
            team_side = "awayTeam"
            event_body = clean_str[len(event_team_prefix) + 1:].strip()
        else:
            if home_team_name in event_team_prefix:
                team_side = "homeTeam"
            else:
                team_side = "awayTeam"
            event_body = clean_str.split(":", 1)[-1].strip()

        if name_pattern:
            event_body = name_pattern.sub(lambda m: name_map[m.group(0)], event_body)

        parsed_events_meta.append((t_secs, cur_half, team_side, event_body))

    def parse_sentence_spec(sentence, shooter_name=None):
        if shooter_name:
            action_text = re.sub(rf'^\s*(?:{re.escape(shooter_name)}|{re.escape(shooter_name.split()[-1])})\b\s*', '', sentence, flags=re.IGNORECASE).lower()
        else:
            action_text = sentence.lower()

        if "from the corner" in action_text or "in the corner" in action_text or "from corner" in action_text:
            return "corner"
        if any(p in action_text for p in ["three point", "beyond the arc", "from downtown", "from deep"]):
            return "three_pointer"
        if "fadeaway" in action_text:
            return "fadeaway"
        if any(p in action_text for p in ["shoots a jumper", "jump shot", "jumper from the elbow", "jumper from the foul line", "jumper from the base line", "jumper from the baseline"]):
            return "jumper"
        if "from the low post" in action_text or "in the low post" in action_text or "low post" in action_text:
            return "postup"
        if any(p in action_text for p in ["in the paint", "from the inside", "shoots in the paint", "shoots from the inside"]):
            return "inside"
        if "from the block" in action_text or "on the block" in action_text:
            return "block"
        if "mid-range" in action_text or "midrange" in action_text:
            return "midrange"
        if any(p in action_text for p in ["lays it up", "layup", "lay it up"]):
            return "layup"
        if any(p in action_text for p in ["slam dunk", "goes for the dunk", "attempts to dunk", "dunks it", "dunks"]):
            return "dunk"
        if "floater" in action_text:
            return "floater"
        if "tips it in" in action_text or "tips it" in action_text or "tip-in" in action_text:
            return "tip-in"
        if "jumper" in action_text:
            return "jumper"
        return "shot"

    for t_secs, event_half, team, event_body in parsed_events_meta:
        oppTeam = "homeTeam" if team == "awayTeam" else "awayTeam"

        # Find type of defense being played
        try:
            defense = [d for d in gameData["awayTeam"]["defense"] if d in event_body][-1]
        except IndexError:
            defense = "half-court"

        if ("Breakaway" in event_body or "Fast break opportunity" in event_body) and "slow it down" not in event_body:
            defense = "transition"

        shot_sentences = get_valid_shot_sentences(event_body)

        if shot_sentences:
            is_drive_play = extract_drive_shot(event_body, True)
            for orig_sentence, s_lower in shot_sentences:
                shooter_name = extract_shooter(orig_sentence, team_roster_tuples[team])
                made = determine_shot_outcome_for_sentence(orig_sentence, event_body)
                temp_spec = parse_sentence_spec(orig_sentence, shooter_name)

                s_list = team_shots[team]
                cur_ptr = team_pointers[team]
                best_idx = None
                best_score = (999, 999, 999, 999, 999, 999)

                for s_idx in range(len(s_list)):
                    s = s_list[s_idx]
                    if s['used'] or s['half'] != event_half:
                        continue
                    dt = (t_secs - s['time_secs']) if t_secs is not None else 0
                    if dt < -10 or dt > 120:
                        continue

                    p_match = False
                    if shooter_name:
                        sh_lower = shooter_name.lower()
                        s_player = s['player'].lower()
                        if s_player == sh_lower or s_player.split()[-1] == sh_lower.split()[-1]:
                            p_match = True

                    dist = s['dist'] if s['dist'] is not None else 0
                    bounds_ok = True
                    if temp_spec in shot_bounds:
                        min_d, max_d = shot_bounds[temp_spec]
                        if not (min_d <= dist <= max_d):
                            bounds_ok = False
                    elif temp_spec in ["three_pointer", "corner"]:
                        if dist < 21:
                            bounds_ok = False

                    made_match = (made is None or s['made'] == made)
                    idx_diff = abs(s_idx - cur_ptr)
                    ideal_d = ideal_dist.get(temp_spec, 12.0)
                    dist_diff = abs(dist - ideal_d)

                    # Prioritize exact player match, bounds, made match, abs(dt), idx_diff, dist_diff
                    score = (0 if p_match else 1, 0 if bounds_ok else 1, 0 if made_match else 1, abs(dt), idx_diff, dist_diff)
                    if score < best_score:
                        best_score = score
                        best_idx = s_idx

                matched_s = None
                if best_idx is not None and best_score[0] == 0 and best_score[1] == 0:
                    matched_s = s_list[best_idx]
                    matched_s['used'] = True
                    team_pointers[team] = best_idx + 1
                    shot_event_distance = matched_s['dist']
                    offense_player_name = matched_s['player']
                    defense_player_name = matched_s.get('defender')
                    if made is None:
                        shot_attempt = 1 if matched_s['made'] else 0
                    else:
                        shot_attempt = 1 if made else 0
                else:
                    if temp_spec in ["three_pointer", "corner"]:
                        shot_event_distance = 22.0
                    elif temp_spec == "fadeaway":
                        shot_event_distance = 18.0
                    elif temp_spec in ["jumper", "midrange"]:
                        shot_event_distance = 12.0
                    elif temp_spec in ["inside", "floater"]:
                        shot_event_distance = 6.0
                    elif temp_spec in ["layup", "dunk", "postup", "block"]:
                        shot_event_distance = 1.0
                    elif temp_spec == "tip-in":
                        shot_event_distance = 0.0
                    else:
                        shot_event_distance = 12.0
                    shot_attempt = 1 if made else 0
                    offense_player_name = shooter_name
                    defense_player_name = None

                # Categorize shot_type for gameData
                if temp_spec in ["three_pointer", "corner"]:
                    shot_type = "3-Pointer"
                elif temp_spec in ["fadeaway", "jumper", "midrange"]:
                    shot_type = "Mid-Range"
                else:
                    is_finishing_keyword = temp_spec in ["layup", "dunk"]
                    if is_finishing_keyword and (defense == "transition" or is_drive_play):
                        shot_type = "Finishing"
                    else:
                        shot_type = "Inside Shot"

                # Distance key
                if shot_event_distance <= 6:
                    distance_key = "0-6"
                elif shot_event_distance < 21:
                    distance_key = "7-20"
                else:
                    distance_key = "21+"

                # Resolve playerCodes
                offense_playerCode = None
                if offense_player_name:
                    offense_playerCode = player_dic.get(offense_player_name)
                    if not offense_playerCode:
                        for full_p, p_code in team_roster_tuples[team]:
                            if full_p.lower() == offense_player_name.lower() or full_p.split()[-1].lower() == offense_player_name.split()[-1].lower():
                                offense_playerCode = p_code
                                break

                defense_playerCode = None
                if defense_player_name:
                    defense_playerCode = player_dic.get(defense_player_name)
                    if not defense_playerCode:
                        for full_p, p_code in team_roster_tuples[oppTeam]:
                            if full_p.lower() == defense_player_name.lower() or full_p.split()[-1].lower() == defense_player_name.split()[-1].lower():
                                defense_playerCode = p_code
                                break

                # Accumulate team stats
                gameData[team]["totalShots"][shot_type][0] += shot_attempt
                gameData[team]["totalShots"][shot_type][1] += 1

                gameData[team]["shot_distance"][distance_key][0] += shot_attempt
                gameData[team]["shot_distance"][distance_key][1] += 1

                gameData[oppTeam]["stats"]["OFG"][0] += shot_attempt
                gameData[oppTeam]["stats"]["OFG"][1] += 1
                if shot_type == "3-Pointer":
                    gameData[oppTeam]["stats"]["O3P"][0] += shot_attempt
                    gameData[oppTeam]["stats"]["O3P"][1] += 1
                    gameData[oppTeam]["stats"]["OPTS"] += shot_attempt * 3
                else:
                    gameData[oppTeam]["stats"]["OPTS"] += shot_attempt * 2

                gameData[oppTeam]["totalDefense"][shot_type][0] += shot_attempt
                gameData[oppTeam]["totalDefense"][shot_type][1] += 1
                gameData[oppTeam]["totalDefense"]["Turnovers"][1] += 1

                gameData[oppTeam]["defense"][defense][shot_type][0] += shot_attempt
                gameData[oppTeam]["defense"][defense][shot_type][1] += 1
                gameData[oppTeam]["defense"][defense]["Turnovers"][1] += 1

                for player in gameData[team]["players"]:
                    if offense_playerCode and player["playerCode"] == offense_playerCode:
                        player["shots"][shot_type][0] += shot_attempt
                        player["shots"][shot_type][1] += 1
                        player["shot_distance"][distance_key][0] += shot_attempt
                        player["shot_distance"][distance_key][1] += 1

                for player in gameData[oppTeam]["players"]:
                    if defense_playerCode and player["playerCode"] == defense_playerCode:
                        player["defense"][shot_type][0] += shot_attempt
                        player["defense"][shot_type][1] += 1
                        player["stats"]["OFG"][0] += shot_attempt
                        player["stats"]["OFG"][1] += 1
                        if shot_type == "3-Pointer":
                            player["stats"]["O3P"][0] += shot_attempt
                            player["stats"]["O3P"][1] += 1
                            player["stats"]["OPTS"] += shot_attempt * 3
                        else:
                            player["stats"]["OPTS"] += shot_attempt * 2
        else:
            if any(phrase in event_body for phrase in ["steals the pass", "turns the ball over", "on the shot."]):
                gameData[oppTeam]["totalDefense"]["Turnovers"][0] += 1
                gameData[oppTeam]["totalDefense"]["Turnovers"][1] += 1
                gameData[oppTeam]["defense"][defense]["Turnovers"][0] += 1
                gameData[oppTeam]["defense"][defense]["Turnovers"][1] += 1

    # Date and Game IDs
    date = soup.find("div", {"id": "Main"}).find_all("h3")[0]
    type_id = soup.find("div", {"id": "Main"}).find_all("h3")[1]
    first_half_months = ["October","November","December"]
    date_split = date.text[7:].replace(",","").split(" ")
    month = date_split[0]
    year = int(date_split[-1])
    season = year + 1 if month in first_half_months else year

    date_text = date.text[7:]
    formatted_date = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_text)
    date_obj = datetime.strptime(formatted_date, "%B %d, %Y")
    date_int = int(date_obj.strftime("%Y%m%d"))

    game_type_unparsed = type_id.text[15:].split("]")[0].strip().strip("[")
    game_id_unparsed = type_id.text[15:].split(" ")[-2]
    game_type = game_type_unparsed.split(" ")[-1]
    game_id = int(game_id_unparsed.strip("[]#"))

    gameData["seasonYear"] = season
    gameData["gameCode"] = game_id
    gameData["gameType"] = game_type
    gameData["game_date"] = date_int

    if gameData["awayTeam"]["stats"]["PTS"] > gameData["homeTeam"]["stats"]["PTS"]:
        gameData["awayTeam"]["outcome"] = 1
    else:
        gameData["homeTeam"]["outcome"] = 1

    # Calculates # of possessions for each team
    gameData["awayTeam"]["stats"]["Poss"] = round(gameData["awayTeam"]["stats"]["FG"][1] + .48 * gameData["awayTeam"]["stats"]["FT"][1] - gameData["awayTeam"]["stats"]["Off"] + gameData["awayTeam"]["stats"]["TO"], 1)
    gameData["homeTeam"]["stats"]["Poss"] = round(gameData["homeTeam"]["stats"]["FG"][1] + .48 * gameData["homeTeam"]["stats"]["FT"][1] - gameData["homeTeam"]["stats"]["Off"] + gameData["homeTeam"]["stats"]["TO"], 1)
    gameData["awayTeam"]["stats"]["OPoss"] = gameData["homeTeam"]["stats"]["Poss"]
    gameData["homeTeam"]["stats"]["OPoss"] = gameData["awayTeam"]["stats"]["Poss"]

    for curTeam in ["awayTeam", "homeTeam"]:
        for player in gameData[curTeam]["players"]:
            player["stats"]["Poss"] = round(gameData[curTeam]["stats"]["Poss"] * (player["stats"]["Min"] / (.2 * gameData[curTeam]["stats"]["Min"])), 1) if gameData[curTeam]["stats"]["Min"] > 0 else 0
            player["stats"]["OPoss"] = round(gameData[curTeam]["stats"]["OPoss"] * (player["stats"]["Min"] / (.2 * gameData[curTeam]["stats"]["Min"])), 1) if gameData[curTeam]["stats"]["Min"] > 0 else 0

    return gameData

#python -m backend.scripts.pygameAnalyzerAPI
#print(gameAnalyzer("https://onlinecollegebasketball.org/game/1269399")["homeTeam"])