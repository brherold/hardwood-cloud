import warnings
try:
    from sklearn.exceptions import InconsistentVersionWarning
    warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
except Exception:
    pass
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")
warnings.filterwarnings("ignore", message=".*InconsistentVersionWarning.*")
warnings.filterwarnings("ignore", message=".*X does not have valid feature names.*")
warnings.filterwarnings("ignore", message=".*trying to unpickle estimator.*")
import os
import sys
import re

# Ensure backend directory is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from .pygetPlayerInfo import * #have to run like this in terminal: python -m scripts.pygetPlayerInfo
from models import *
from .pygameAnalyzerAPI import *
from .helperFunctions import *
from .teamRosterInfo import *
from .predict import *
from .predict_TAVG import *
from .getConferenceDivison import *
from .getTeamConference import *
from sqlalchemy import *
from .sosFinder import *
from .predictEPM import *
from extensions import db
from models import Game
from flask import current_app
from app_init import *


from .dataAdder import current_season



team_sos_rpi = sos_holder()

EXISTING_GAME_IDS = set()
_GAMES_LOADED = False

def _ensure_games_cache():
    global _GAMES_LOADED, EXISTING_GAME_IDS
    if not _GAMES_LOADED:
        try:
            EXISTING_GAME_IDS = set(row[0] for row in db.session.query(Game.game_id).all())
            _GAMES_LOADED = True
        except Exception:
            pass

KNOWN_TEAMS = set()
_TEAMS_LOADED = False

def _ensure_teams_cache():
    global _TEAMS_LOADED, KNOWN_TEAMS
    if not _TEAMS_LOADED:
        try:
            KNOWN_TEAMS = set(row[0] for row in db.session.query(Team.team_id).all())
            _TEAMS_LOADED = True
        except Exception:
            pass

ROSTER_LOADED_TEAMS = set()

#Adjust BPM (EPM ) formula is .75*(20*SOS - 10) + .25*BPM 
#20*SOS - 10 -> Scales SOS values similarly to BPM/EPM

#^
def APM_scaler(sos):
    return .75*(20*sos - 10)

def id_to_url(id):
    '''
    Converts either playerID or teamID into urls
    '''
    id = int(id)
    if id > 1020:
        return "http://onlinecollegebasketball.org/player/" + str(id)
    else:
        return "http://onlinecollegebasketball.org/team/" + str(id)


#Shortens names of the defense types
DEFENSE_NAME_MAPPING = {
    "man-to-man": "man",
    "man-to-man defense packed": "m_pck",
    "man-to-man defense extended": "m_ext",
    "zone": "zone",
    "zone defense packed": "z_pck",
    "zone defense extended": "z_ext",
    "pressure": "press",
    "transition": "trans",
    "half-court": "half",
}

# Step 2: Create a function to transform defense names
def transform_defense_names(defense_data):
    """
    Transforms defense names in the defense_data dictionary using the DEFENSE_NAME_MAPPING.
    """
    transformed_data = {}
    for defense_type, stats in defense_data.items():
        # Get the abbreviated name from the mapping
        abbreviated_name = DEFENSE_NAME_MAPPING.get(defense_type, defense_type)
        transformed_data[abbreviated_name] = stats
    return transformed_data


#Finds eFG given FG Made, 3P Made, FG Attempted
def eFg_percentage(FGM,_3PM,FGA):
    
    return round(((FGM + 0.5 * _3PM) / FGA),3) if FGA != 0 else None

#Finds shot% given FGM, FGA
def fg_percentage(FGM,FGA):
    return round((FGM / FGA),3) if FGA != 0 else None
    




#Adds Conference data to Conference Table

def conference_adder():
    conference_data = get_divisons()

    for conference_id in conference_data:
        conference_name, division_id = conference_data[conference_id]

        new_conference = Conference(
            conference_id = conference_id,
            conference_name = conference_name,
            division_id = division_id,
        )
        db.session.add(new_conference)
        db.session.commit()
    return 



def add_to_player(player_id):
    '''
    Adds playerID to player Table
    Adds team and players and players skills if they are not in DB
    '''
    player_url = id_to_url(player_id)

    player_data = get_player_info(player_url)  # Fetch player data using the URL


    if player_data["Team_ID"] == player_data["Player_ID"]:

        #Player is not in a Team (prospect or graduated)
        return None
    

    get_or_add_team(player_data["Team_ID"]) #Add team and their players to DB
    new_player = Player.query.filter_by(player_id=player_id).first()

    return new_player


def add_to_playerSkills(player_id):
    # Adds or updates playerID in PlayerSkills Table
    print(f"Adding skills for {player_id}")
    player_url = id_to_url(player_id)
    player_data = get_player_info(player_url)

    # Check if skills already exist for the player in the current season

    existing_player_skills = PlayerSkills.query.filter_by(player_id=player_id, season_id=current_season).first()

    if existing_player_skills:
        # Update existing player skills
        existing_player_skills.height = player_data["Height_inches"]
        existing_player_skills.weight = player_data["Weight"]
        existing_player_skills.wingspan = player_data["Wingspan_inches"]
        existing_player_skills.vertical = player_data["Vertical_float"]
        existing_player_skills.IS = player_data["IS"]
        existing_player_skills.IQ = player_data["IQ"]
        existing_player_skills.OS = player_data["OS"]
        existing_player_skills.Pass = player_data["Pass"]
        existing_player_skills.Rng = player_data["Rng"]
        existing_player_skills.Hnd = player_data["Hnd"]
        existing_player_skills.Fin = player_data["Fin"]
        existing_player_skills.Drv = player_data["Drv"]
        existing_player_skills.Reb = player_data["Reb"]
        existing_player_skills.Str = player_data["Str"]
        existing_player_skills.IDef = player_data["IDef"]
        existing_player_skills.Spd = player_data["Spd"]
        existing_player_skills.PDef = player_data["PDef"]
        existing_player_skills.Sta = player_data["Sta"]

        db.session.commit()  
        return existing_player_skills, "Player skills updated successfully"
    
    else:
        # If no existing skills, add new skills to the table
        new_player_skills = PlayerSkills(
            player_id=player_data["Player_ID"],
            season_id=player_data["Season_ID"],
            height=player_data["Height_inches"],
            weight=player_data["Weight"],
            wingspan=player_data["Wingspan_inches"],
            vertical=player_data["Vertical_float"],
            IS=player_data["IS"],
            IQ=player_data["IQ"],
            OS=player_data["OS"],
            Pass=player_data["Pass"],
            Rng=player_data["Rng"],
            Hnd=player_data["Hnd"],
            Fin=player_data["Fin"],
            Drv=player_data["Drv"],
            Reb=player_data["Reb"],
            Str=player_data["Str"],
            IDef=player_data["IDef"],
            Spd=player_data["Spd"],
            PDef=player_data["PDef"],
            Sta=player_data["Sta"]
        )

        db.session.add(new_player_skills)  # Add the new player skills to the session
        db.session.commit() 
        print(f"{player_id} skills added")
        return new_player_skills, "Player skills added successfully"

def get_or_add_player(player_id):
    """ 
    NO UPDATING Data
    Checks if player is in Player Table 
    Checks to see if player in current season is in Player Skill table (using seasonID)
    If new player/team adds them aswell as PlayerSkill
    """
    # Check if Player is in DB
    existing_player = Player.query.filter_by(player_id=player_id).first()

    if existing_player:
        #Checks if that player Skills is for the current Season
        

        existing_player_skill_season = PlayerSkills.query.filter_by(player_id=player_id, season_id=current_season).first()

        if not existing_player_skill_season:
            #If the player skills for current season is not in Player Skills Table, add their skills
            add_to_playerSkills(player_id)

        return existing_player

    new_player = add_to_player(player_id)     
    
    if not new_player:
        return None
    
    add_to_playerSkills(player_id)

    
    return new_player  # Return the newly added player


def update_player_helper(player_id):
    #Updates player skills (or adds them into db (player and playerskills Table)
    
    existing_player = Player.query.filter_by(player_id=player_id).first()

    if existing_player:

        get_or_add_team(existing_player.team_id)
        return existing_player
    
    new_player = get_or_add_player(player_id)

    return new_player


def team_data_to_playerDB(team_data):
    """
    Adds new players from team_data to the Player and PlayerSkills tables.
    Does NOT update existing players or skills.
    """
    teamID = team_data["teamID"]
    
    for player in team_data["players"]:
        player_id = player["playerID"]
        player_name = player["name"]

        # Check if player already exists
        existing_player = Player.query.filter_by(player_id=player_id).first()

        if not existing_player:
            # Add new player
            new_player = Player(player_id=player_id, team_id=teamID, name=player_name)
            db.session.add(new_player)

        # Check if player skills already exist for this season
        existing_skills = PlayerSkills.query.filter_by(
            player_id=player_id, season_id=current_season
        ).first()

        if not existing_skills:
            # Add new player skills
            new_player_skills = PlayerSkills(
                player_id=player_id,
                season_id=current_season,
                **{attr: player[attr] for attr in [
                    "Pos", "Class", "height", "weight", "wingspan", "vertical",
                    "IS", "IQ", "OS", "Pass", "Rng", "Hnd", "Fin", "Drv", "Reb",
                    "Str", "IDef", "Spd", "PDef", "Sta", "SI", "POT", "Stars"
                ]}
            )
            db.session.add(new_player_skills)

    # Commit all new players and skills in one transaction
    db.session.commit()
    
def get_or_add_team(team_id):
    '''
    Check or add a team to the DB using the team_id and given season
    '''
    _ensure_teams_cache()
    team_id_int = int(team_id)
    if team_id_int in KNOWN_TEAMS:
        return True

    existing_team = Team.query.filter_by(team_id=team_id_int).first()
    if existing_team:
        KNOWN_TEAMS.add(team_id_int)
        return existing_team
    
    # If the team does not exist, fetch their data
    team_url = id_to_url(team_id_int)
    team_data = team_roster_info(team_url, current_season)
    team_data_to_playerDB(team_data)
    
    new_team = Team(team_id=team_data["teamID"], team_name=team_data["teamName"]) 
    db.session.add(new_team)
    db.session.flush()
    KNOWN_TEAMS.add(team_id_int)
    return new_team


#Updates Team Stat Averages for game
def update_team_avg(team_id,season_id,game_type,stat_type,team_outcome,team_shots, team_shot_distance, team_stats, opponent_stats,team_conference_id, team_driving=None):
    team_avg = db.session.query(TeamAvg).filter_by(team_id = team_id,season_id = season_id,game_type=game_type,stat_type = stat_type).first()
    

    if team_avg:

        #Get opponent avg stats
        opp_avg = db.session.query(TeamAvg).filter_by(team_id = team_id,season_id = season_id,game_type=game_type,stat_type = "opponent").first()
        
        #Accumalate avg
        
        team_avg.GW += team_outcome
        new_games_played = team_avg.GP + 1
        
        team_avg.F_M = round(((team_avg.F_M * team_avg.GP) + team_shots["Finishing"][0]) / new_games_played, 3)
        team_avg.F_A = round(((team_avg.F_A * team_avg.GP) + team_shots["Finishing"][1]) / new_games_played, 3)
        team_avg.F_P = fg_percentage(team_avg.F_M,team_avg.F_A)

        
        team_avg.IS_M = round(((team_avg.IS_M * team_avg.GP) + team_shots["Inside Shot"][0]) / new_games_played, 3)
        team_avg.IS_A = round(((team_avg.IS_A * team_avg.GP) + team_shots["Inside Shot"][1]) / new_games_played, 3)
        team_avg.IS_P = fg_percentage(team_avg.IS_M,team_avg.IS_A)

        
        team_avg.MR_M = round(((team_avg.MR_M * team_avg.GP) + team_shots["Mid-Range"][0]) / new_games_played, 3)
        team_avg.MR_A = round(((team_avg.MR_A * team_avg.GP) + team_shots["Mid-Range"][1]) / new_games_played, 3)
        team_avg.MR_P = fg_percentage(team_avg.MR_M,team_avg.MR_A)

        
        team_avg._3P_M = round(((team_avg._3P_M * team_avg.GP) + team_shots["3-Pointer"][0]) / new_games_played, 3)
        team_avg._3P_A = round(((team_avg._3P_A * team_avg.GP) + team_shots["3-Pointer"][1]) / new_games_played, 3)
        team_avg._3P_P = fg_percentage(team_avg._3P_M,team_avg._3P_A)

        
        team_avg.Min = round(((team_avg.Min * team_avg.GP) + team_stats["Min"]) / new_games_played, 3)
        team_avg.PTS = round(((team_avg.PTS * team_avg.GP) + team_stats["PTS"]) / new_games_played, 3)

        team_avg.FG_M = round(((team_avg.FG_M * team_avg.GP) + team_stats["FG"][0]) / new_games_played, 3)
        team_avg.FG_A = round(((team_avg.FG_A * team_avg.GP) + team_stats["FG"][1]) / new_games_played, 3)
        team_avg.eFG_P = eFg_percentage(team_avg.FG_M,team_avg._3P_M,team_avg.FG_A)

        team_avg._2P_M = round(((team_avg._2P_M * team_avg.GP) +  (team_stats["FG"][0] - team_shots["3-Pointer"][0])) / new_games_played, 3)
        team_avg._2P_A = round(((team_avg._2P_A * team_avg.GP) + (team_stats["FG"][1] - team_shots["3-Pointer"][1])) / new_games_played, 3)
        team_avg._2P_P = fg_percentage(team_avg._2P_M,team_avg._2P_A)

        team_avg.FT_M = round(((team_avg.FT_M * team_avg.GP) + team_stats["FT"][0]) / new_games_played, 3)
        team_avg.FT_A = round(((team_avg.FT_A * team_avg.GP) + team_stats["FT"][1]) / new_games_played, 3)
        team_avg.FT_P = fg_percentage(team_avg.FT_M,team_avg.FT_A)


        team_avg.Off = round(((team_avg.Off * team_avg.GP) + team_stats["Off"]) / new_games_played, 3)
        team_avg.Rebs = round(((team_avg.Rebs * team_avg.GP) + team_stats["Reb"]) / new_games_played, 3)
        team_avg.Def = team_avg.Rebs - team_avg.Off
        team_avg.AST = round(((team_avg.AST * team_avg.GP) + team_stats["AST"]) / new_games_played, 3)
        team_avg.STL = round(((team_avg.STL * team_avg.GP) + team_stats["STL"]) / new_games_played, 3)
        team_avg.BLK = round(((team_avg.BLK * team_avg.GP) + team_stats["BLK"]) / new_games_played, 3)
        team_avg.TO = round(((team_avg.TO * team_avg.GP) + team_stats["TO"]) / new_games_played, 3)
        team_avg.PF = round(((team_avg.PF * team_avg.GP) + team_stats["PF"]) / new_games_played, 3)
        team_avg.PLUS = round(((team_avg.PLUS * team_avg.GP) + team_stats["+/-"]) / new_games_played, 3)
        
        #No updating DIST if it is None ("-")
        if team_stats["DIST"] != "-":
            if team_avg.DIST is None:
                team_avg.DIST = round(float(team_stats["DIST"]),1)
            else:
                team_avg.DIST = round(((team_avg.DIST * team_avg.GP) + float(team_stats["DIST"])) / new_games_played,3)



        team_avg.PITP = round(((team_avg.PITP * team_avg.GP) + team_stats["PITP"]) / new_games_played,3)
        team_avg.FBP = round(((team_avg.FBP * team_avg.GP) + team_stats["FBP"]) / new_games_played,3)
        team_avg.FD = round(((team_avg.FD * team_avg.GP) + team_stats["FD"]) / new_games_played,3)
        team_avg.Poss = round(((team_avg.Poss * team_avg.GP) + team_stats["Poss"]) / new_games_played,3)

        
        team_avg.Rim_M = round(((team_avg.Rim_M * team_avg.GP) + team_shot_distance["0-6"][0]) / new_games_played, 3)
        team_avg.Rim_A = round(((team_avg.Rim_A * team_avg.GP) + team_shot_distance["0-6"][1]) / new_games_played, 3)
        team_avg.Rim_P = fg_percentage(team_avg.Rim_M,team_avg.Rim_A)
        
        team_avg.Mid_M = round(((team_avg.Mid_M * team_avg.GP) + team_shot_distance["7-20"][0]) / new_games_played, 3)
        team_avg.Mid_A = round(((team_avg.Mid_A * team_avg.GP) + team_shot_distance["7-20"][1]) / new_games_played, 3)
        team_avg.Mid_P = fg_percentage(team_avg.Mid_M,team_avg.Mid_A)

        if team_driving is not None:
            prev_dr_m = team_avg.DR_M if team_avg.DR_M is not None else 0
            prev_dr_a = team_avg.DR_A if team_avg.DR_A is not None else 0
            team_avg.DR_M = round(((prev_dr_m * team_avg.GP) + team_driving[0]) / new_games_played, 3)
            team_avg.DR_A = round(((prev_dr_a * team_avg.GP) + team_driving[1]) / new_games_played, 3)
            team_avg.DR_P = fg_percentage(team_avg.DR_M, team_avg.DR_A)


        if stat_type != "opponent":
            #Prep for BPM Training 
            
            # Format: [Poss,Pts,FGA,FTA,Off,AST,TO,FD]
            off_values = [team_avg.Poss, team_avg.PTS,team_avg.FG_A,
                            team_avg.FT_A,team_avg.Off,team_avg.AST,
                            team_avg.TO,team_avg.FD]
            
            # Format: [OPoss,OPTS,OFGA,OFTA,DReb,STL,PF]
            def_values = [opp_avg.Poss, opp_avg.PTS,opp_avg.FG_A, opp_avg.FT_A,
                            team_avg.Def, team_avg.STL,
                            team_avg.PF]

            bpm_values = predict_bpm_tavg("team",off_values,def_values)

            team_avg.OBPM = bpm_values[0]
            team_avg.DBPM = bpm_values[1]
            team_avg.BPM =  bpm_values[2]



            team_sos = team_sos_rpi[team_id][0]
            team_avg.SOS = team_sos
            team_avg.RPI = team_sos_rpi[team_id][1]



            #For Calculating Adjusted BPM (uses SOS)
            if game_type == "College":
                
                '''
                team_avg.AOBPM = round(.75 * team_avg.OBPM + 25 * (team_sos - .5), 1)
                team_avg.ADBPM = round(.75 * team_avg.DBPM + 25 * (team_sos - .5), 1)
                team_avg.ABPM =  team_avg.AOBPM + team_avg.ADBPM
                '''
                team_avg.AOBPM = round(.25 * team_avg.OBPM + APM_scaler(team_sos), 1)
                team_avg.ADBPM = round(.25 * team_avg.DBPM + APM_scaler(team_sos), 1)
                team_avg.ABPM =  team_avg.AOBPM + team_avg.ADBPM                
            
            
            #Only calculate ORB% and DRB% for stat_type == "team"
            #Query to get opponent rebound stats to calculate 
            

            denom = (team_avg.Off + opp_avg.Def)
            team_avg.ORB_P = round(100 *team_avg.Off / (denom),1) if denom != 0 else 0

            denom = (team_avg.Def + opp_avg.Off)
            team_avg.DRB_P = round(100 *team_avg.Def / (denom),1) if denom != 0 else 0

        #Advanced Statistics
        team_avg.TS = round((team_avg.PTS) / (2 * (team_avg.FG_A + 0.48 * team_avg.FT_A)), 3) if (team_avg.FG_A + 0.48 * team_avg.FT_A) != 0 else 0

        team_avg._3PAr = round(team_avg._3P_A / team_avg.FG_A, 3) if team_avg.FG_A != 0 else 0

        
        team_avg.FTr = round(team_avg.FT_A / team_avg.FG_A, 3) if team_avg.FG_A != 0 else 0

        team_avg.ORtg = round(100*(team_avg.PTS / team_avg.Poss),1)

        team_avg.NetRtg = round(team_avg.ORtg - opp_avg.ORtg,1) if stat_type != "opponent" else None


        denom = team_avg.FG_A + 0.48 * team_avg.FT_A + team_avg.TO
        team_avg.TO_P = round(100 * team_avg.TO / denom, 1) if denom != 0 else 0

        team_avg.FT_FG_A = round(team_avg.FT_M / team_avg.FG_A,3)



            
        team_avg.GP = new_games_played #Last because Needed to calculate Avg for Stats Before
            


    else:

       
        if stat_type != "opponent":
            #Prep for BPM Training 
            off_values = [team_stats["Poss"], team_stats["PTS"],team_stats["FG"][1],
                            team_stats["FT"][1],team_stats["Off"],team_stats["AST"],
                            team_stats["TO"],team_stats["FD"]]
            
            # Format: [OPoss,OPTS,OFGA,OFTA,DReb,STL,PF]
            def_values = [team_stats["OPoss"], team_stats["OPTS"],team_stats["OFG"][1],opponent_stats["FT"][1],
                            team_stats["Reb"] -  team_stats["Off"], team_stats["STL"],
                            team_stats["PF"]]

            bpm_values = predict_bpm_tavg("team",off_values,def_values)
        else:
            #No BPM for opponent stats
            bpm_values = []
        
        
    #First game for team
        team_avg = TeamAvg(
        
            team_id=team_id,
            season_id = season_id,
            game_type=game_type, 
            conference_id = team_conference_id,
            stat_type = stat_type,

            GW = team_outcome,
            GP = 1,

            F_M =team_shots["Finishing"][0],
            F_A =team_shots["Finishing"][1],
            F_P = fg_percentage(team_shots["Finishing"][0],team_shots["Finishing"][1]),

            
            IS_M =team_shots["Inside Shot"][0],
            IS_A =team_shots["Inside Shot"][1],
            IS_P = fg_percentage(team_shots["Inside Shot"][0],team_shots["Inside Shot"][1]),

            
            MR_M =team_shots["Mid-Range"][0],
            MR_A =team_shots["Mid-Range"][1],
            MR_P = fg_percentage(team_shots["Mid-Range"][0],team_shots["Mid-Range"][1]),

            
            _3P_M = team_shots["3-Pointer"][0],
            _3P_A =team_shots["3-Pointer"][1],
            _3P_P = fg_percentage(team_shots["3-Pointer"][0],team_shots["3-Pointer"][1]),

            _2P_M = team_stats["FG"][0] - team_shots["3-Pointer"][0],
            _2P_A = team_stats["FG"][1] - team_shots["3-Pointer"][1],
            _2P_P = fg_percentage(team_stats["FG"][0] - team_shots["3-Pointer"][0] , team_stats["FG"][1] - team_shots["3-Pointer"][1]),


           
            Min = team_stats["Min"],
            PTS = team_stats["PTS"],
            
            FG_M = team_stats["FG"][0],
            FG_A = team_stats["FG"][1],
            eFG_P = eFg_percentage(team_stats["FG"][0],team_shots["3-Pointer"][0],team_stats["FG"][1]),

            
            FT_M = team_stats["FT"][0],
            FT_A =  team_stats["FT"][1],
            FT_P = fg_percentage(team_stats["FT"][0],team_stats["FT"][1]),
            
            Off = team_stats["Off"],
            Def = team_stats["Reb"] - team_stats["Off"],
            Rebs = team_stats["Reb"],
            AST = team_stats["AST"],
            STL = team_stats["STL"],
            BLK = team_stats["BLK"],
            TO = team_stats["TO"],
            PF = team_stats["PF"],
            PLUS = team_stats["+/-"],
            DIST = float(team_stats["DIST"]) if team_stats["DIST"] != "-" else None,
            PITP = team_stats["PITP"],
            FBP = team_stats["FBP"],
            FD = team_stats["FD"],
            Poss = team_stats["Poss"],

            Rim_M =team_shot_distance["0-6"][0],
            Rim_A =team_shot_distance["0-6"][1],
            Rim_P = fg_percentage(team_shot_distance["0-6"][0],team_shot_distance["0-6"][1]),

            Mid_M =team_shot_distance["7-20"][0],
            Mid_A =team_shot_distance["7-20"][1],
            Mid_P = fg_percentage(team_shot_distance["7-20"][0],team_shot_distance["7-20"][1]),


            DR_M = team_driving[0] if team_driving is not None else 0,
            DR_A = team_driving[1] if team_driving is not None else 0,
            DR_P = fg_percentage(team_driving[0], team_driving[1]) if team_driving is not None and team_driving[1] > 0 else None,

 
            
            OBPM = bpm_values[0] if bpm_values else None, 
            DBPM = bpm_values[1] if bpm_values else None, 
            BPM =  bpm_values[2] if bpm_values else None,
                                                                
            AOBPM = round(.25 * bpm_values[0] + APM_scaler(team_sos_rpi[team_id][0]), 1) if bpm_values and game_type == "College" else None, 
            ADBPM = round(.25 * bpm_values[1] + APM_scaler(team_sos_rpi[team_id][0]), 1) if bpm_values and game_type == "College" else None, 
            ABPM =  round(.25 * bpm_values[0] + APM_scaler(team_sos_rpi[team_id][0]), 1)  + round(.25 * bpm_values[1] + APM_scaler(team_sos_rpi[team_id][0]), 1) if bpm_values and game_type == "College" else None,



            #Advanced Statistics
            TS = round((team_stats["PTS"]) / (2 * (team_stats["FG"][1] + 0.48 * team_stats["FT"][1])), 3) \
                if (team_stats["FG"][1] + 0.48 * team_stats["FT"][1]) != 0 else 0,

            _3PAr = round(team_shots["3-Pointer"][1] / team_stats["FG"][1], 3) if team_stats["FG"][1] != 0 else 0,

            FTr = round(team_stats["FT"][1] / team_stats["FG"][1], 3) if team_stats["FG"][1] != 0 else 0,

            ORtg = round(100 * (team_stats["PTS"] / team_stats["Poss"]), 1),

            NetRtg = (
                None if stat_type == "opponent"
                else round((100 * ((team_stats["PTS"]/team_stats["Poss"]) - (opponent_stats["PTS"]/opponent_stats["Poss"]))),1)
            ),
            

            TO_P = round(100 * team_stats["TO"] / 
                (team_stats["FG"][1] + 0.48 * team_stats["FT"][1] + team_stats["TO"]), 1) \
                if (team_stats["FG"][1] + 0.48 * team_stats["FT"][1] + team_stats["TO"]) != 0 else 0,
            
            FT_FG_A = round(team_stats["FT"][0] / team_stats["FG"][1],3),

            ORB_P = (
                None if stat_type == "opponent"
                else round(100 * team_stats["Off"] / (team_stats["Off"] + (opponent_stats["Reb"] - opponent_stats["Off"])), 1)
                if (team_stats["Off"] + (opponent_stats["Reb"] - opponent_stats["Off"])) != 0
                else 0
            ),
            DRB_P = (
                None if stat_type == "opponent"
                else round(100 * (team_stats["Reb"] - team_stats["Off"]) / ((team_stats["Reb"] - team_stats["Off"]) + opponent_stats["Off"]), 1)
                if ((team_stats["Reb"] - team_stats["Off"]) + opponent_stats["Off"]) != 0
                else 0
            ) ,

            SOS = team_sos_rpi[team_id][0] if stat_type == "team" else None,
            RPI = team_sos_rpi[team_id][1] if stat_type == "team" else None,
        )
        db.session.add(team_avg)
    db.session.flush()

  




def create_team_stats(game_id, team_id, team_outcome, team_shots, team_shot_distance, team_stats, opponent_shots, team_driving=None, opponent_shot_distance=None, opponent_driving=None):
    """
    Helper function to create a TeamStats table.
    """


    
                        #       [PTS, FGA, FTA, Off, AST, TO, FD]
    #Prep for BPM Training 
    Poss = team_stats["Poss"]
    O_Poss = team_stats["OPoss"]
    off_values = [team_stats["PTS"],team_stats["FG"][1],
                      team_stats["FT"][1],team_stats["Off"],team_stats["AST"],
                      team_stats["TO"],team_stats["FD"]]
    
                        #def_values = [OPTS, OFGA, Def, STL, PF]
    def_values = [ team_stats["OPTS"],team_stats["OFG"][1],
                      team_stats["Reb"] -  team_stats["Off"], team_stats["STL"],
                      team_stats["PF"]]

    bpm_values = predict_bpm("team",Poss,O_Poss,off_values,def_values)#predict_bpm("team",off_values,def_values)


    return TeamStats(
        game_id=game_id,
        team_id=team_id,
        outcome= team_outcome,
        #season_id=season_id,
        F_M =team_shots["Finishing"][0],
        F_A =team_shots["Finishing"][1],
        F_P = fg_percentage(team_shots["Finishing"][0],team_shots["Finishing"][1]),

        
        IS_M =team_shots["Inside Shot"][0],
        IS_A =team_shots["Inside Shot"][1],
        IS_P = fg_percentage(team_shots["Inside Shot"][0],team_shots["Inside Shot"][1]),

        
        MR_M =team_shots["Mid-Range"][0],
        MR_A =team_shots["Mid-Range"][1],
        MR_P = fg_percentage(team_shots["Mid-Range"][0],team_shots["Mid-Range"][1]),

        
        _3P_M = team_shots["3-Pointer"][0],
        _3P_A =team_shots["3-Pointer"][1],
        _3P_P = fg_percentage(team_shots["3-Pointer"][0],team_shots["3-Pointer"][1]),

        _2P_M = team_stats["FG"][0] - team_shots["3-Pointer"][0],
        _2P_A = team_stats["FG"][1] - team_shots["3-Pointer"][1],
        _2P_P = fg_percentage(team_stats["FG"][0] - team_shots["3-Pointer"][0] , team_stats["FG"][1] - team_shots["3-Pointer"][1]),

        O_PTS = team_stats["OPTS"],
        O_FG_M = team_stats["OFG"][0],
        O_FG_A = team_stats["OFG"][1],
        O_eFG_P = eFg_percentage(team_stats["OFG"][0],opponent_shots["3-Pointer"][0],team_stats["OFG"][1]),

        
        O_3P_M = opponent_shots["3-Pointer"][0],
        O_3P_A = opponent_shots["3-Pointer"][1],
        O_3P_P = fg_percentage(opponent_shots["3-Pointer"][0],opponent_shots["3-Pointer"][1]),

        
        O_2P_M = team_stats["OFG"][0] - team_stats["O3P"][0],
        O_2P_A = team_stats["OFG"][1] - team_stats["O3P"][1],
        O_2P_P = fg_percentage(team_stats["OFG"][0] - team_stats["O3P"][0], team_stats["OFG"][1] - team_stats["O3P"][1]),
       
        O_F_M = opponent_shots["Finishing"][0],
        O_F_A = opponent_shots["Finishing"][1],
        O_F_P = fg_percentage(opponent_shots["Finishing"][0],opponent_shots["Finishing"][1]),
       
        O_IS_M = opponent_shots["Inside Shot"][0],
        O_IS_A = opponent_shots["Inside Shot"][1],
        O_IS_P = fg_percentage(opponent_shots["Inside Shot"][0],opponent_shots["Inside Shot"][1]),

        O_MR_M = opponent_shots["Mid-Range"][0],
        O_MR_A = opponent_shots["Mid-Range"][1],
        O_MR_P = fg_percentage(opponent_shots["Mid-Range"][0],opponent_shots["Mid-Range"][1]),

        O_Poss = team_stats["OPoss"],
        Min = team_stats["Min"],
        PTS = team_stats["PTS"],
        
        FG_M = team_stats["FG"][0],
        FG_A = team_stats["FG"][1],
        eFG_P = eFg_percentage(team_stats["FG"][0],team_shots["3-Pointer"][0],team_stats["FG"][1]),

        
        FT_M = team_stats["FT"][0],
        FT_A =  team_stats["FT"][1],
        FT_P = fg_percentage(team_stats["FT"][0],team_stats["FT"][1]),
        
        Off = team_stats["Off"],
        Def = team_stats["Reb"] - team_stats["Off"],
        Rebs = team_stats["Reb"],
        AST = team_stats["AST"],
        STL = team_stats["STL"],
        BLK = team_stats["BLK"],
        TO = team_stats["TO"],
        PF = team_stats["PF"],
        PLUS = team_stats["+/-"],
        DIST = float(team_stats["DIST"]) if team_stats["DIST"] != "-" else None,
        PITP = team_stats["PITP"],
        FBP = team_stats["FBP"],
        FD = team_stats["FD"],
        Fat = team_stats["Fat"],
        Poss = team_stats["Poss"],

        Rim_M =team_shot_distance["0-6"][0],
        Rim_A =team_shot_distance["0-6"][1],
        Rim_P = fg_percentage(team_shot_distance["0-6"][0],team_shot_distance["0-6"][1]),

        Mid_M =team_shot_distance["7-20"][0],
        Mid_A =team_shot_distance["7-20"][1],
        Mid_P = fg_percentage(team_shot_distance["7-20"][0],team_shot_distance["7-20"][1]),


        DR_M = team_driving[0] if team_driving is not None else 0,
        DR_A = team_driving[1] if team_driving is not None else 0,
        DR_P = fg_percentage(team_driving[0], team_driving[1]) if team_driving is not None and team_driving[1] > 0 else None,

        O_Rim_M = opponent_shot_distance["0-6"][0] if opponent_shot_distance is not None else 0,
        O_Rim_A = opponent_shot_distance["0-6"][1] if opponent_shot_distance is not None else 0,
        O_Rim_P = fg_percentage(opponent_shot_distance["0-6"][0], opponent_shot_distance["0-6"][1]) if opponent_shot_distance is not None else None,

        O_Mid_M = opponent_shot_distance["7-20"][0] if opponent_shot_distance is not None else 0,
        O_Mid_A = opponent_shot_distance["7-20"][1] if opponent_shot_distance is not None else 0,
        O_Mid_P = fg_percentage(opponent_shot_distance["7-20"][0], opponent_shot_distance["7-20"][1]) if opponent_shot_distance is not None else None,

        O_DR_M = opponent_driving[0] if opponent_driving is not None else 0,
        O_DR_A = opponent_driving[1] if opponent_driving is not None else 0,
        O_DR_P = fg_percentage(opponent_driving[0], opponent_driving[1]) if opponent_driving is not None else None,
        OBPM = bpm_values[0], 
        DBPM = bpm_values[1], 
        BPM =  bpm_values[2],

    )

    

def game_data_to_team_stats(game_data):
    """
    Takes in game_data from gameAnalyzer(game_id) and inputs stats into DB (TeamStats).
    """
        
    try:
        # Extract game data
        game_id = int(game_data["gameCode"])
        #season_id = game_data["seasonYear"] - 2042

        home_team_data = game_data["homeTeam"]
        away_team_data = game_data["awayTeam"]

        home_team_id = home_team_data["teamCode"]
        away_team_id = away_team_data["teamCode"]

        home_team_outcome = home_team_data["outcome"]
        away_team_outcome = away_team_data["outcome"]

        home_team_shots = home_team_data["totalShots"]
        away_team_shots = away_team_data["totalShots"]

        home_team_shot_distance = home_team_data["shot_distance"]
        away_team_shot_distance = away_team_data["shot_distance"]

        home_team_stats = home_team_data["stats"]
        away_team_stats = away_team_data["stats"]
        # Create TeamStats instances

        home_team_stats = create_team_stats(
            game_id,
            home_team_id,
            home_team_outcome,
            home_team_shots,
            home_team_shot_distance,
            home_team_stats,
            away_team_shots,
            team_driving=home_team_data.get("driving"),
            opponent_shot_distance=away_team_data.get("shot_distance"),
            opponent_driving=away_team_data.get("driving")
        )

        away_team_stats = create_team_stats(
            game_id,
            away_team_id,
            away_team_outcome,
            away_team_shots,
            away_team_shot_distance,
            away_team_stats,
            home_team_shots,
            team_driving=away_team_data.get("driving"),
            opponent_shot_distance=home_team_data.get("shot_distance"),
            opponent_driving=home_team_data.get("driving")
        )




        # Add to the database session
        db.session.add(home_team_stats)
        db.session.add(away_team_stats)

        


        db.session.flush()

    except KeyError as e:
        print(f"Missing key in game_data: {e}")
        db.session.rollback()  # Rollback the transaction in case of an error
    except Exception as e:
        print(f"An error occurred: {e}")
        db.session.rollback()  # Rollback the transaction in case of an error

def create_off_def_stats (game_id,team_id,def_type,defense):
    """
    Helper function to create a TeamStats table.
    [0] -> offenseStats
    [1] -> defenseStats
    """
    shot_dist = defense.get("shot_distance", {"0-6": [0,0], "7-20": [0,0], "21+": [0,0]})
    ft_stat = defense.get("Free Throw", [0, 0])
    drv_stat = defense.get("driving", [0, 0])

    return (OffenseStats(
        game_id = game_id,
        team_id = team_id,
        defense_type = def_type,
        plays = defense["Turnovers"][1],
        F_M = defense["Finishing"][0],
        F_A = defense["Finishing"][1],
        IS_M = defense["Inside Shot"][0],
        IS_A = defense["Inside Shot"][1],
        MR_M = defense["Mid-Range"][0],
        MR_A = defense["Mid-Range"][1],
        _3P_M = defense["3-Pointer"][0],
        _3P_A = defense["3-Pointer"][1],
        Rim_M = shot_dist["0-6"][0],
        Rim_A = shot_dist["0-6"][1],
        Mid_M = shot_dist["7-20"][0],
        Mid_A = shot_dist["7-20"][1],
        FT_M = ft_stat[0],
        FT_A = ft_stat[1],
        DR_M = drv_stat[0],
        DR_A = drv_stat[1],
        TOV = defense["Turnovers"][0]
    ), DefenseStats(
        game_id = game_id,
        team_id = team_id,
        defense_type = def_type,
        plays = defense["Turnovers"][1],
        F_M = defense["Finishing"][0],
        F_A = defense["Finishing"][1],
        IS_M = defense["Inside Shot"][0],
        IS_A = defense["Inside Shot"][1],
        MR_M = defense["Mid-Range"][0],
        MR_A = defense["Mid-Range"][1],
        _3P_M = defense["3-Pointer"][0],
        _3P_A = defense["3-Pointer"][1],
        Rim_M = shot_dist["0-6"][0],
        Rim_A = shot_dist["0-6"][1],
        Mid_M = shot_dist["7-20"][0],
        Mid_A = shot_dist["7-20"][1],
        FT_M = ft_stat[0],
        FT_A = ft_stat[1],
        DR_M = drv_stat[0],
        DR_A = drv_stat[1],
        TOV = defense["Turnovers"][0]
    ))

def game_data_to_team_off_deff_stats(game_data):
    """
    Takes in game_data from gameAnalyzer(game_id) and inputs stats into DB (offense_stats + defensive_stats).
    
    """
    try:
        # Extract game data
        game_id = int(game_data["gameCode"])
        season_id = game_data["seasonYear"]

        home_team_data = game_data["homeTeam"]
        away_team_data = game_data["awayTeam"]

        home_team_id = home_team_data["teamCode"]
        away_team_id = away_team_data["teamCode"]

        home_team_defense = home_team_data["defense"]
        away_team_defense = away_team_data["defense"]

        # Create TeamStats/OffenseStats/DefenseStats instances
        for def_type in home_team_defense:
            home_team_off = create_off_def_stats(
                game_id,
                home_team_id,
                def_type,
                away_team_defense[def_type])[0]
            
            home_team_def = create_off_def_stats(
                game_id,
                home_team_id,
                def_type,
                home_team_defense[def_type]
            )[1]

            away_team_off = create_off_def_stats(
                game_id,
                away_team_id,
                def_type,
                home_team_defense[def_type])[0]
            
            away_team_def = create_off_def_stats(
                game_id,
                away_team_id,
                def_type,
                away_team_defense[def_type]
            )[1]

            # Add to the database session
            db.session.add(home_team_off)
            db.session.add(away_team_off)
            db.session.add(home_team_def)
            db.session.add(away_team_def)
            pass
        db.session.flush()

    except KeyError as e:
        print(f"Missing key in game_data: {e}")
        db.session.rollback()  # Rollback the transaction in case of an error
    except Exception as e:
        print(f"An error occurred: {e}")
        db.session.rollback()  # Rollback the transaction in case of an error


def create_player_stats(player_id,game_id,player_position,player_shots, player_shot_distance, player_defense,player_stats, player_pos_min, player_driving=None, player_defense_distance=None):
    '''
    Inputs player_id, game_id, player_shots,... and puts in PlayerStats db 
    '''

    #Prep for BPM Training 
    Poss = player_stats["Poss"]
    O_Poss = player_stats["OPoss"]
    
    #off_values = [PTS, FGA, FTA, Off, AST, TO, FD]
    off_values = [ player_stats["PTS"],player_stats["FG"][1],
                      player_stats["FT"][1],player_stats["Off"],player_stats["AST"],
                      player_stats["TO"],player_stats["FD"]]
    
    #def_values = [OPTS, OFGA, Def, STL, PF]
    def_values = [player_stats["OPTS"],player_stats["OFG"][1],
                      player_stats["Reb"] -  player_stats["Off"], player_stats["STL"],
                      player_stats["PF"]]

    PG_bpm = predict_bpm("PG",Poss, O_Poss, off_values, def_values)
    SG_bpm = predict_bpm("SG",Poss, O_Poss, off_values, def_values)
    SF_bpm = predict_bpm("SF",Poss, O_Poss, off_values, def_values)
    PF_bpm = predict_bpm("PF",Poss, O_Poss, off_values, def_values)
    C_bpm = predict_bpm("C",Poss, O_Poss, off_values, def_values)
    
    if player_stats["Min"] == 0:
        player_stats["Min"] = 1

    pg_weight, sg_weight, sf_weight, pf_weight, c_weight = player_pos_min["PG"]/player_stats["Min"], player_pos_min["SG"]/player_stats["Min"], player_pos_min["SF"]/player_stats["Min"], player_pos_min["PF"]/player_stats["Min"], player_pos_min["C"]/player_stats["Min"]  
    
    bpm_values = tuple(
    round(a*pg_weight + b*sg_weight + c*sf_weight + d*pf_weight + e*c_weight, 1)
    for a, b, c, d, e in zip(PG_bpm, SG_bpm, SF_bpm, PF_bpm, C_bpm)
    )            
        

    #EPM+
                    #['FG_A','_2P_M','_3P_M','FT_M','AST','TO','Off']
    off_values_epm = [player_stats["FG"][1],player_stats["FG"][0] - player_stats["3P"][0],player_stats["3P"][0], player_stats["FT"][0], 
                        player_stats["AST"], player_stats["TO"], player_stats["Off"]]
                    #['O_FG_A','O_2P_M','O_3P_M','STL','PF','Def']
    def_values_epm  = [player_stats["OFG"][1],  player_stats["OFG"][0] - player_stats["O3P"][0] 
                       ,player_stats["O3P"][0], player_stats["STL"],player_stats["PF"], player_stats["Reb"] -  player_stats["Off"]]

    PG_epm = predict_epm("PG",Poss, O_Poss, off_values_epm, def_values_epm)
    SG_epm = predict_epm("SG",Poss, O_Poss, off_values_epm, def_values_epm)
    SF_epm = predict_epm("SF",Poss, O_Poss, off_values_epm, def_values_epm)
    PF_epm = predict_epm("PF",Poss, O_Poss, off_values_epm, def_values_epm)
    C_epm = predict_epm("C",Poss, O_Poss, off_values_epm, def_values_epm)
    

    epm_values = tuple(
    round(a*pg_weight + b*sg_weight + c*sf_weight + d*pf_weight + e*c_weight, 1)
    for a, b, c, d, e in zip(PG_epm, SG_epm, SF_epm, PF_epm, C_epm)
    )  

    return PlayerStats(
        player_id = player_id,
        game_id=game_id,
        Pos = player_position,
        GS = player_stats["Start"],
        PG_Min = player_pos_min.get("PG", 0),
        SG_Min = player_pos_min.get("SG", 0),
        SF_Min = player_pos_min.get("SF", 0),
        PF_Min = player_pos_min.get("PF", 0),
        C_Min = player_pos_min.get("C", 0),
        Min = player_stats["Min"],
        PTS = player_stats["PTS"],
        FG_M = player_stats["FG"][0],
        FG_A = player_stats["FG"][1],
        eFG_P = eFg_percentage(player_stats["FG"][0],player_shots["3-Pointer"][0],player_stats["FG"][1]),
        
        _2P_M = player_stats["FG"][0] - player_shots["3-Pointer"][0],
        _2P_A = player_stats["FG"][1] - player_shots["3-Pointer"][1],
        _2P_P = fg_percentage((player_stats["FG"][0] - player_shots["3-Pointer"][0]),(player_stats["FG"][1] - player_shots["3-Pointer"][1])),
        
        _3P_M = player_shots["3-Pointer"][0],
        _3P_A = player_shots["3-Pointer"][1],
        _3P_P = fg_percentage(player_shots["3-Pointer"][0],player_shots["3-Pointer"][1]),
        
        FT_M = player_stats["FT"][0],
        FT_A =  player_stats["FT"][1],
        FT_P = fg_percentage(player_stats["FT"][0],player_stats["FT"][1]),
        
        Off = player_stats["Off"],
        Def = player_stats["Reb"] - player_stats["Off"],
        Rebs = player_stats["Reb"],
        AST = player_stats["AST"],
        STL = player_stats["STL"],
        BLK = player_stats["BLK"],
        TO = player_stats["TO"],
        PF = player_stats["PF"],
        PLUS = player_stats["+/-"],
        DIST = float(player_stats["DIST"]) if player_stats["DIST"] != "-" else None,
        PITP = player_stats["PITP"],
        FBP = player_stats["FBP"],
        FD = player_stats["FD"],
        Fat = player_stats["Fat"],
        Poss = player_stats["Poss"],

        Rim_M = player_shot_distance["0-6"][0],
        Rim_A = player_shot_distance["0-6"][1],
        Rim_P = fg_percentage(player_shot_distance["0-6"][0],player_shot_distance["0-6"][1]),

        Mid_M =player_shot_distance["7-20"][0],
        Mid_A =player_shot_distance["7-20"][1],
        Mid_P = fg_percentage(player_shot_distance["7-20"][0],player_shot_distance["7-20"][1]),

        DR_M = player_driving[0] if player_driving is not None else None,
        DR_A = player_driving[1] if player_driving is not None else None,
        DR_P = fg_percentage(player_driving[0], player_driving[1]) if player_driving is not None and player_driving[1] > 0 else None,

        O_Rim_M = player_defense_distance["0-6"][0] if player_defense_distance is not None else 0,
        O_Rim_A = player_defense_distance["0-6"][1] if player_defense_distance is not None else 0,
        O_Rim_P = fg_percentage(player_defense_distance["0-6"][0], player_defense_distance["0-6"][1]) if player_defense_distance is not None else None,

        O_Mid_M = player_defense_distance["7-20"][0] if player_defense_distance is not None else 0,
        O_Mid_A = player_defense_distance["7-20"][1] if player_defense_distance is not None else 0,
        O_Mid_P = fg_percentage(player_defense_distance["7-20"][0], player_defense_distance["7-20"][1]) if player_defense_distance is not None else None,

        F_M = player_shots["Finishing"][0],
        F_A = player_shots["Finishing"][1],
        F_P = fg_percentage(player_shots["Finishing"][0],player_shots["Finishing"][1]),

        IS_M = player_shots["Inside Shot"][0],
        IS_A = player_shots["Inside Shot"][1],
        IS_P = fg_percentage(player_shots["Inside Shot"][0],player_shots["Inside Shot"][1]),
       
        MR_M = player_shots["Mid-Range"][0],
        MR_A = player_shots["Mid-Range"][1],
        MR_P = fg_percentage(player_shots["Mid-Range"][0],player_shots["Mid-Range"][1]),

        O_PTS = player_stats["OPTS"],
        O_FG_M = player_stats["OFG"][0],
        O_FG_A = player_stats["OFG"][1],
        O_eFG_P = eFg_percentage(player_stats["OFG"][0],player_defense["3-Pointer"][0],player_stats["OFG"][1]),
       
        O_F_M = player_defense["Finishing"][0],
        O_F_A = player_defense["Finishing"][1],
        O_F_P = fg_percentage(player_defense["Finishing"][0],player_defense["Finishing"][1]),
       
        O_IS_M = player_defense["Inside Shot"][0],
        O_IS_A = player_defense["Inside Shot"][1],
        O_IS_P = fg_percentage(player_defense["Inside Shot"][0],player_defense["Inside Shot"][1]),
       
        O_MR_M = player_defense["Mid-Range"][0],
        O_MR_A = player_defense["Mid-Range"][1],
        O_MR_P = fg_percentage(player_defense["Mid-Range"][0],player_defense["Mid-Range"][1]),

        O_3P_M = player_defense["3-Pointer"][0],
        O_3P_A = player_defense["3-Pointer"][1],
        O_3P_P = fg_percentage(player_defense["3-Pointer"][0],player_defense["3-Pointer"][1]),

        O_2P_M = player_stats["OFG"][0] - player_stats["O3P"][0],
        O_2P_A = player_stats["OFG"][1] - player_stats["O3P"][1],
        O_2P_P = fg_percentage(player_stats["OFG"][0] - player_stats["O3P"][0], player_stats["OFG"][1] - player_stats["O3P"][1]),

        O_Poss = player_stats["OPoss"],
            
        OBPM = bpm_values[0], 
        DBPM = bpm_values[1], 
        BPM =  bpm_values[2],

        OEPM = epm_values[0],
        DEPM = epm_values[1], 
        EPM = epm_values[2]
        )
    

def add_player_stats(game_data):
    '''
    Takes in game_data from gameAnalyzer(game_id) and inputs the player's stats in PlayerStats
    '''
    try:
        # Extract game data
        game_id = int(game_data["gameCode"])
        season_year = game_data["seasonYear"]

        home_team_data = game_data["homeTeam"]
        away_team_data = game_data["awayTeam"]

        home_team_id = home_team_data["teamCode"]
        away_team_id = away_team_data["teamCode"]

        home_team_players = home_team_data["players"] #array of players
        away_team_players = away_team_data["players"]



        #Adds home team's players into PlayerStats Table
        for player in home_team_players:
            #print(player)
            player_name = player["name"]
            player_id = player["playerCode"]
            player_position = player["position"]
            player_shots = player["shots"]
            player_shot_distance = player["shot_distance"]
            player_defense = player["defense"]
            player_stats = player["stats"]
            new_player = create_player_stats(player_id,game_id,player_position,player_shots,player_shot_distance, player_defense,player_stats,player["pos_min"], player_driving=player.get("driving"), player_defense_distance=player.get("defense_distance"))
            
            
            db.session.add(new_player)
            

            
            #Add players in Players Table and PlayerSkills Table if game in currrent season
            if season_year == current_season:
                #update_player_helper(player_id) 
                get_or_add_player(player_id)
                db.session.add(new_player)
            
            pass

        #Adds away team's players into PlayerStats Table
        for player in away_team_players:
            player_name = player["name"]
            player_id = player["playerCode"]
            player_position = player["position"]
            player_shots = player["shots"]
            player_shot_distance = player["shot_distance"]
            player_defense = player["defense"]
            player_stats = player["stats"]
            new_player = create_player_stats(player_id,game_id,player_position,player_shots,player_shot_distance,player_defense,player_stats,player["pos_min"], player_driving=player.get("driving"), player_defense_distance=player.get("defense_distance"))

            db.session.add(new_player)
            
            
            
            #Add players in Players Table and PlayerSkills Table if game in currrent season
            if season_year == current_season:
                #update_player_helper(player_id)
                get_or_add_player(player_id)
                db.session.add(new_player)      
              
            pass
        db.session.flush()



    except KeyError as e:
        print(f"Missing key in game_data: {e}")
        db.session.rollback()  # Rollback the transaction in case of an error
    except Exception as e:
        print(f"An error occurred: {e}")
        db.session.rollback()  # Rollback the transaction in case of an error

#Gets position player played most in (in player avg) for caclulating BPM and EPM
def get_position_with_minutes(player_id, season_id, game_type):
    pos_min = db.session.query(PlayerAvg).filter_by(
        player_id=player_id,
        season_id=season_id,
        game_type=game_type
    ).first()

    minutes = {
        'PG': pos_min.PG_Min,
        'SG': pos_min.SG_Min,
        'SF': pos_min.SF_Min,
        'PF': pos_min.PF_Min,
        'C': pos_min.C_Min
    }

    return minutes

#Updates Player Stat Averages for game
def update_player_avg(player_id,season_id,game_type,player_position,player_shots,player_shot_distance,player_defense,player_stats,player_pos_min, player_driving=None, player_defense_distance=None):
    player_avg = db.session.query(PlayerAvg).filter_by(player_id = player_id,season_id = season_id,game_type=game_type).first()
    #Gets Team and Opponent Team Avg Stats (for calculating advanced statistics like AST%)
    team_id_of_player = db.session.query(Player.team_id).filter_by(player_id=player_id).scalar()
    team_avg = db.session.query(TeamAvg).filter_by(team_id=team_id_of_player, season_id = season_id,game_type=game_type,stat_type="team").first()
    opp_team_avg = db.session.query(TeamAvg).filter_by(team_id=team_id_of_player, season_id = season_id,game_type=game_type,stat_type="opponent").first()
    
    

    if player_avg:
        
        #Accumalate avg
        

        new_games_played = player_avg.GP + 1

        player_avg.GS = player_avg.GS + player_stats["Start"]
         
        player_avg.PG_Min = round(((player_avg.PG_Min * player_avg.GP) + player_pos_min["PG"]) / new_games_played, 3) 
        player_avg.SG_Min = round(((player_avg.SG_Min * player_avg.GP) + player_pos_min["SG"]) / new_games_played, 3) 
        player_avg.SF_Min = round(((player_avg.SF_Min * player_avg.GP) + player_pos_min["SF"]) / new_games_played, 3) 
        player_avg.PF_Min = round(((player_avg.PF_Min * player_avg.GP) + player_pos_min["PF"]) / new_games_played, 3) 
        player_avg.C_Min = round(((player_avg.C_Min * player_avg.GP) + player_pos_min["C"]) / new_games_played, 3) 
        
        player_avg.F_M = round(((player_avg.F_M * player_avg.GP) + player_shots["Finishing"][0]) / new_games_played, 3)
        player_avg.F_A = round(((player_avg.F_A * player_avg.GP) + player_shots["Finishing"][1]) / new_games_played, 3)
        player_avg.F_P = fg_percentage(player_avg.F_M,player_avg.F_A)
        
       
        player_avg.IS_M = round(((player_avg.IS_M * player_avg.GP) + player_shots["Inside Shot"][0]) / new_games_played, 3)
        player_avg.IS_A = round(((player_avg.IS_A * player_avg.GP) + player_shots["Inside Shot"][1]) / new_games_played, 3)
        player_avg.IS_P = fg_percentage(player_avg.IS_M,player_avg.IS_A)
       
        player_avg.MR_M = round(((player_avg.MR_M * player_avg.GP) + player_shots["Mid-Range"][0]) / new_games_played, 3)
        player_avg.MR_A = round(((player_avg.MR_A * player_avg.GP) + player_shots["Mid-Range"][1]) / new_games_played, 3)
        player_avg.MR_P = fg_percentage(player_avg.MR_M,player_avg.MR_A)
        
        player_avg._3P_M = round(((player_avg._3P_M * player_avg.GP) + player_shots["3-Pointer"][0]) / new_games_played, 3)
        player_avg._3P_A = round(((player_avg._3P_A * player_avg.GP) + player_shots["3-Pointer"][1]) / new_games_played, 3)
        player_avg._3P_P = fg_percentage(player_avg._3P_M,player_avg._3P_A)

        
        player_avg.O_PTS = round(((player_avg.O_PTS * player_avg.GP) + player_stats["OPTS"]) / new_games_played, 3)
        player_avg.O_FG_M = round(((player_avg.O_FG_M * player_avg.GP) + player_stats["OFG"][0]) / new_games_played, 3)
        player_avg.O_FG_A = round(((player_avg.O_FG_A * player_avg.GP) + player_stats["OFG"][1]) / new_games_played, 3)
        player_avg.O_3P_M = round(((player_avg.O_3P_M * player_avg.GP) + player_defense["3-Pointer"][0]) / new_games_played, 3)
        player_avg.O_3P_A = round(((player_avg.O_3P_A * player_avg.GP) + player_defense["3-Pointer"][1]) / new_games_played, 3)
        player_avg.O_3P_P = fg_percentage(player_avg.O_3P_M,player_avg.O_3P_A)
        
        player_avg.O_eFG_P = eFg_percentage(player_avg.O_FG_M,player_avg.O_3P_M,player_avg.O_FG_A)

        player_avg.O_2P_M = round(((player_avg.O_2P_M * player_avg.GP) +  (player_stats["OFG"][0] - player_defense["3-Pointer"][0])) / new_games_played, 3)
        player_avg.O_2P_A = round(((player_avg.O_2P_A * player_avg.GP) + (player_stats["OFG"][1] - player_defense["3-Pointer"][1])) / new_games_played, 3)
        player_avg.O_2P_P = fg_percentage(player_avg.O_2P_M,player_avg.O_2P_A) 
        
        player_avg.O_F_M = round(((player_avg.O_F_M * player_avg.GP) + player_defense["Finishing"][0]) / new_games_played, 3)
        player_avg.O_F_A = round(((player_avg.O_F_A * player_avg.GP) + player_defense["Finishing"][1]) / new_games_played, 3)
        player_avg.O_F_P = fg_percentage(player_avg.O_F_M,player_avg.O_F_A)
        
        player_avg.O_IS_M = round(((player_avg.O_IS_M * player_avg.GP) + player_defense["Inside Shot"][0]) / new_games_played, 3)
        player_avg.O_IS_A = round(((player_avg.O_IS_A * player_avg.GP) + player_defense["Inside Shot"][1]) / new_games_played, 3)
        player_avg.O_IS_P = fg_percentage(player_avg.O_IS_M,player_avg.O_IS_A)
        
        player_avg.O_MR_M = round(((player_avg.O_MR_M * player_avg.GP) + player_defense["Mid-Range"][0]) / new_games_played, 3)
        player_avg.O_MR_A = round(((player_avg.O_MR_A * player_avg.GP) + player_defense["Mid-Range"][1]) / new_games_played, 3)
        player_avg.O_MR_P = fg_percentage(player_avg.O_MR_M,player_avg.O_MR_A)
        
        player_avg.O_Poss = round(((player_avg.O_Poss * player_avg.GP) + player_stats["OPoss"]) / new_games_played, 3)
        player_avg.Min = round(((player_avg.Min * player_avg.GP) + player_stats["Min"]) / new_games_played, 3)
        player_avg.PTS = round(((player_avg.PTS * player_avg.GP) + player_stats["PTS"]) / new_games_played, 3)
        
        player_avg.FG_M = round(((player_avg.FG_M * player_avg.GP) + player_stats["FG"][0]) / new_games_played, 3)
        player_avg.FG_A = round(((player_avg.FG_A * player_avg.GP) + player_stats["FG"][1]) / new_games_played, 3)
        player_avg.eFG_P = eFg_percentage(player_avg.FG_M,player_avg._3P_M,player_avg.FG_A)

        player_avg._2P_M = round(((player_avg._2P_M * player_avg.GP) +  (player_stats["FG"][0] - player_shots["3-Pointer"][0])) / new_games_played, 3)
        player_avg._2P_A = round(((player_avg._2P_A * player_avg.GP) + (player_stats["FG"][1] - player_shots["3-Pointer"][1])) / new_games_played, 3)
        player_avg._2P_P = fg_percentage(player_avg._2P_M,player_avg._2P_A)
        
        player_avg.FT_M = round(((player_avg.FT_M * player_avg.GP) + player_stats["FT"][0]) / new_games_played, 3)
        player_avg.FT_A = round(((player_avg.FT_A * player_avg.GP) + player_stats["FT"][1]) / new_games_played, 3)
        player_avg.FT_P = fg_percentage(player_avg.FT_M,player_avg.FT_A)
        

        player_avg.Off = round(((player_avg.Off * player_avg.GP) + player_stats["Off"]) / new_games_played, 3)
        player_avg.Rebs = round(((player_avg.Rebs * player_avg.GP) + player_stats["Reb"]) / new_games_played, 3)
        player_avg.Def = player_avg.Rebs - player_avg.Off
        player_avg.AST = round(((player_avg.AST * player_avg.GP) + player_stats["AST"]) / new_games_played, 3)
        player_avg.STL = round(((player_avg.STL * player_avg.GP) + player_stats["STL"]) / new_games_played, 3)
        player_avg.BLK = round(((player_avg.BLK * player_avg.GP) + player_stats["BLK"]) / new_games_played, 3)
        player_avg.TO = round(((player_avg.TO * player_avg.GP) + player_stats["TO"]) / new_games_played, 3)

        if player_driving is not None:
            prev_dr_m = player_avg.DR_M if player_avg.DR_M is not None else 0
            prev_dr_a = player_avg.DR_A if player_avg.DR_A is not None else 0
            player_avg.DR_M = round(((prev_dr_m * player_avg.GP) + player_driving[0]) / new_games_played, 3)
            player_avg.DR_A = round(((prev_dr_a * player_avg.GP) + player_driving[1]) / new_games_played, 3)
            player_avg.DR_P = fg_percentage(player_avg.DR_M, player_avg.DR_A)

        if player_defense_distance is not None:
            prev_orim_m = player_avg.O_Rim_M if player_avg.O_Rim_M is not None else 0
            prev_orim_a = player_avg.O_Rim_A if player_avg.O_Rim_A is not None else 0
            player_avg.O_Rim_M = round(((prev_orim_m * player_avg.GP) + player_defense_distance["0-6"][0]) / new_games_played, 3)
            player_avg.O_Rim_A = round(((prev_orim_a * player_avg.GP) + player_defense_distance["0-6"][1]) / new_games_played, 3)
            player_avg.O_Rim_P = fg_percentage(player_avg.O_Rim_M, player_avg.O_Rim_A)

            prev_omid_m = player_avg.O_Mid_M if player_avg.O_Mid_M is not None else 0
            prev_omid_a = player_avg.O_Mid_A if player_avg.O_Mid_A is not None else 0
            player_avg.O_Mid_M = round(((prev_omid_m * player_avg.GP) + player_defense_distance["7-20"][0]) / new_games_played, 3)
            player_avg.O_Mid_A = round(((prev_omid_a * player_avg.GP) + player_defense_distance["7-20"][1]) / new_games_played, 3)
            player_avg.O_Mid_P = fg_percentage(player_avg.O_Mid_M, player_avg.O_Mid_A)
        player_avg.PF = round(((player_avg.PF * player_avg.GP) + player_stats["PF"]) / new_games_played, 3)
        player_avg.PLUS = round(((player_avg.PLUS * player_avg.GP) + player_stats["+/-"]) / new_games_played, 3)

        # No updating DIST if it is None ("-")
        if player_stats["DIST"] != "-":
            if player_avg.DIST is None:
                player_avg.DIST = round(float(player_stats["DIST"]), 1)
            else:
                player_avg.DIST = round(((player_avg.DIST * player_avg.GP) + float(player_stats["DIST"])) / new_games_played, 3)

        player_avg.PITP = round(((player_avg.PITP * player_avg.GP) + player_stats["PITP"]) / new_games_played, 3)
        player_avg.FBP = round(((player_avg.FBP * player_avg.GP) + player_stats["FBP"]) / new_games_played, 3)
        player_avg.FD = round(((player_avg.FD * player_avg.GP) + player_stats["FD"]) / new_games_played, 3)
        player_avg.Poss = round(((player_avg.Poss * player_avg.GP) + player_stats["Poss"]) / new_games_played, 3)

        player_avg.Rim_M = round(((player_avg.Rim_M * player_avg.GP) + player_shot_distance["0-6"][0]) / new_games_played, 3)
        player_avg.Rim_A = round(((player_avg.Rim_A * player_avg.GP) + player_shot_distance["0-6"][1]) / new_games_played, 3)
        player_avg.Rim_P = fg_percentage(player_avg.Rim_M,player_avg.Rim_A)

        player_avg.Mid_M = round(((player_avg.Mid_M * player_avg.GP) + player_shot_distance["7-20"][0]) / new_games_played, 3)
        player_avg.Mid_A = round(((player_avg.Mid_A * player_avg.GP) + player_shot_distance["7-20"][1]) / new_games_played, 3)
        player_avg.Mid_P = fg_percentage(player_avg.Mid_M,player_avg.Mid_A)

        # Prep for BPM Training 
        positional_minutes = get_position_with_minutes(player_id,season_id,game_type) #Gets postion player has played most in 
        
        
        
        Poss = player_avg.Poss
        O_Poss = player_avg.O_Poss
        off_values = [player_avg.PTS, player_avg.FG_A,
                    player_avg.FT_A, player_avg.Off, player_avg.AST,
                    player_avg.TO, player_avg.FD]
        
        def_values = [player_avg.O_PTS,player_avg.O_FG_A,
                        player_avg.Rebs -  player_avg.Off, player_avg.STL,
                        player_avg.PF]

        
        PG_bpm = predict_bpm("PG",Poss, O_Poss, off_values, def_values)
        SG_bpm = predict_bpm("SG",Poss, O_Poss, off_values, def_values)
        SF_bpm = predict_bpm("SF",Poss, O_Poss, off_values, def_values)
        PF_bpm = predict_bpm("PF",Poss, O_Poss, off_values, def_values)
        C_bpm = predict_bpm("C",Poss, O_Poss, off_values, def_values)
        
        if player_avg.Min == 0:
            player_avg.Min = 1

        pg_weight, sg_weight, sf_weight, pf_weight, c_weight = positional_minutes["PG"]/player_avg.Min, positional_minutes["SG"]/player_avg.Min, positional_minutes["SF"]/player_avg.Min, positional_minutes["PF"]/player_avg.Min, positional_minutes["C"]/player_avg.Min  
        
        bpm_values = tuple(
        round(a*pg_weight + b*sg_weight + c*sf_weight + d*pf_weight + e*c_weight, 1)
        for a, b, c, d, e in zip(PG_bpm, SG_bpm, SF_bpm, PF_bpm, C_bpm)
        )


        player_avg.OBPM = bpm_values[0]
        player_avg.DBPM = bpm_values[1]
        player_avg.BPM = bpm_values[2]
        
        #EPM 
                        #['FG_A','_2P_M','_3P_M','FT_M','AST','TO','Off']
        off_values_epm = [player_avg.FG_A, player_avg._2P_M, player_avg._3P_M, player_avg.FT_M,
                         player_avg.AST, player_avg.TO, player_avg.Off]
              
                        #['O_FG_A','O_2P_M','O_3P_M','STL','PF','Def']
        def_values_epm  = [player_avg.O_FG_A, player_avg.O_2P_M, player_avg.O_3P_M, player_avg.STL, player_avg.PF, player_avg.Def]
                        

        #epm_values = predict_epm(player_postion_played_most if player_postion_played_most else player_position,Poss, O_Poss, off_values_epm,def_values_epm)

        PG_epm = predict_epm("PG",Poss, O_Poss, off_values_epm, def_values_epm)
        SG_epm = predict_epm("SG",Poss, O_Poss, off_values_epm, def_values_epm)
        SF_epm = predict_epm("SF",Poss, O_Poss, off_values_epm, def_values_epm)
        PF_epm = predict_epm("PF",Poss, O_Poss, off_values_epm, def_values_epm)
        C_epm = predict_epm("C",Poss, O_Poss, off_values_epm, def_values_epm)
        


        epm_values = tuple(
        round(a*pg_weight + b*sg_weight + c*sf_weight + d*pf_weight + e*c_weight, 1)
        for a, b, c, d, e in zip(PG_epm, SG_epm, SF_epm, PF_epm, C_epm)
        )       
        
        
        
        player_avg.OEPM = epm_values[0]
        player_avg.DEPM = epm_values[1]
        player_avg.EPM = epm_values[2]




        #For Calculating Adjusted BPM (uses SOS)
        if game_type == "College":
            team_id_of_player = str(team_id_of_player)

            
            team_sos = team_sos_rpi[team_id_of_player][0]
            player_avg.AOBPM = round(.25 * player_avg.OBPM + APM_scaler(team_sos), 1)
            player_avg.ADBPM = round(.25 * player_avg.DBPM + APM_scaler(team_sos), 1)
            player_avg.ABPM =  player_avg.AOBPM + player_avg.ADBPM

            player_avg.AOEPM = round(.25 * player_avg.OEPM + APM_scaler(team_sos), 1)
            player_avg.ADEPM = round(.25 * player_avg.DEPM + APM_scaler(team_sos), 1)
            player_avg.AEPM =  player_avg.AOEPM + player_avg.ADEPM
                     
        
        #Advanced Statistics
        player_avg.TS = round((player_avg.PTS) / (2 * (player_avg.FG_A + 0.48 * player_avg.FT_A)), 3) if (player_avg.FG_A + 0.48 * player_avg.FT_A) != 0 else 0

        player_avg._3PAr = round(player_avg._3P_A / player_avg.FG_A, 3) if player_avg.FG_A != 0 else 0

        player_avg.FTr = round(player_avg.FT_A / player_avg.FG_A, 3) if player_avg.FG_A != 0 else 0

        denom = player_avg.Min * (team_avg.Off + opp_team_avg.Def)
        player_avg.ORB_P = round(100 * (player_avg.Off * (team_avg.Min / 5)) / denom, 1) if denom != 0 else 0

        denom = player_avg.Min * (team_avg.Def + opp_team_avg.Off)
        player_avg.DRB_P = round(100 * (player_avg.Def * (team_avg.Min / 5)) / denom, 1) if denom != 0 else 0

        denom = player_avg.Min * (team_avg.Rebs + opp_team_avg.Rebs)
        player_avg.TRB_P = round(100 * (player_avg.Rebs * (team_avg.Min / 5)) / denom, 1) if denom != 0 else 0

        denom = ((player_avg.Min / (team_avg.Min / 5)) * team_avg.FG_M) - player_avg.FG_M
        player_avg.AST_P = round(100 * player_avg.AST / denom, 1) if denom != 0 else 0

        denom = player_avg.Min * opp_team_avg.Poss
        player_avg.STL_P = round(100 * (player_avg.STL * (team_avg.Min / 5)) / denom, 1) if denom != 0 else 0

        denom = player_avg.Min * (opp_team_avg.FG_A - opp_team_avg._3P_A)
        player_avg.BLK_P = round(100 * (player_avg.BLK * (team_avg.Min / 5)) / denom, 1) if denom != 0 else 0

        denom = player_avg.FG_A + 0.48 * player_avg.FT_A + player_avg.TO
        player_avg.TO_P = round(100 * player_avg.TO / denom, 1) if denom != 0 else 0

        denom = player_avg.Min * (team_avg.FG_A + 0.48 * team_avg.FT_A + team_avg.TO)
        player_avg.USG_P = round(100 * ((player_avg.FG_A + 0.48 * player_avg.FT_A + player_avg.TO) * (team_avg.Min / 5)) / denom, 1) if denom != 0 else 0
        
        player_avg.GP = new_games_played  # Last because Needed to calculate Avg for Stats Before
                


    else:
        
        team_game_stats = (
            db.session.query(TeamStats)
            .filter_by(team_id=team_id_of_player)
            .order_by(desc(TeamStats.game_id))  # Sorting by game_id in descending order
            .first()
        )

        game_result = (
            db.session.query(TeamStats.game_id)
            .filter_by(team_id=team_id_of_player)
            .order_by(desc(TeamStats.game_id))  # Sorting by game_id in descending order
            .first()
        )

        # Accessing the game_id from the result
        game_id = game_result[0] if game_result else None

        # Gets opponent stats from the same game
        opp_team_game_stats = (
            db.session.query(TeamStats)
            .filter(TeamStats.game_id == game_id)  
            .filter(TeamStats.team_id != team_id_of_player)  
            .first()  
        )
        
       
        
        #Prep for BPM Training 
        Poss = player_stats["Poss"]
        O_Poss = player_stats["OPoss"]

        off_values = [player_stats["PTS"],player_stats["FG"][1],
                        player_stats["FT"][1],player_stats["Off"],player_stats["AST"],
                        player_stats["TO"],player_stats["FD"]]

        def_values = [ player_stats["OPTS"],player_stats["OFG"][1],
                        player_stats["Reb"] -  player_stats["Off"], player_stats["STL"],
                        player_stats["PF"]]

        
        PG_bpm = predict_bpm("PG",Poss, O_Poss, off_values, def_values)
        SG_bpm = predict_bpm("SG",Poss, O_Poss, off_values, def_values)
        SF_bpm = predict_bpm("SF",Poss, O_Poss, off_values, def_values)
        PF_bpm = predict_bpm("PF",Poss, O_Poss, off_values, def_values)
        C_bpm = predict_bpm("C",Poss, O_Poss, off_values, def_values)
        
        if player_stats["Min"] == 0:
            player_stats["Min"] = 1

        pg_weight, sg_weight, sf_weight, pf_weight, c_weight = player_pos_min["PG"]/player_stats["Min"], player_pos_min["SG"]/player_stats["Min"], player_pos_min["SF"]/player_stats["Min"], player_pos_min["PF"]/player_stats["Min"], player_pos_min["C"]/player_stats["Min"]  
        
        bpm_values = tuple(
        round(a*pg_weight + b*sg_weight + c*sf_weight + d*pf_weight + e*c_weight, 1)
        for a, b, c, d, e in zip(PG_bpm, SG_bpm, SF_bpm, PF_bpm, C_bpm)
        )        
        
        
        #EPM Training
                #['FG_A','_2P_M','_3P_M','FT_M','AST','TO','Off']
        off_values_epm = [player_stats["FG"][1],player_stats["FG"][0] - player_stats["3P"][0],player_stats["3P"][0], player_stats["FT"][0], 
                            player_stats["AST"], player_stats["TO"], player_stats["Off"]]
                        #['O_FG_A','O_2P_M','O_3P_M','STL','PF','Def']
        def_values_epm  = [player_stats["OFG"][1],  player_stats["OFG"][0] - player_stats["O3P"][0] 
                            ,player_stats["O3P"][0], player_stats["STL"],player_stats["PF"], player_stats["Reb"] -  player_stats["Off"]]

        PG_epm = predict_epm("PG",Poss, O_Poss, off_values_epm, def_values_epm)
        SG_epm = predict_epm("SG",Poss, O_Poss, off_values_epm, def_values_epm)
        SF_epm = predict_epm("SF",Poss, O_Poss, off_values_epm, def_values_epm)
        PF_epm = predict_epm("PF",Poss, O_Poss, off_values_epm, def_values_epm)
        C_epm = predict_epm("C",Poss, O_Poss, off_values_epm, def_values_epm)
        


        epm_values = tuple(
        round(a*pg_weight + b*sg_weight + c*sf_weight + d*pf_weight + e*c_weight, 1)
        for a, b, c, d, e in zip(PG_epm, SG_epm, SF_epm, PF_epm, C_epm)
        )              

        if game_type == "College":
            team_id_of_player = str(team_id_of_player)
            team_sos = team_sos_rpi[team_id_of_player][0]
            
        
    #First game for player
        player_avg = PlayerAvg(
        
            player_id=player_id,
            season_id = season_id,
            game_type=game_type, 

            GP = 1,
            GS = player_stats["Start"],
            
            PG_Min = player_pos_min["PG"],
            SG_Min = player_pos_min["SG"],
            SF_Min = player_pos_min["SF"],
            PF_Min = player_pos_min["PF"],
            C_Min = player_pos_min["C"],

            F_M =player_shots["Finishing"][0],
            F_A =player_shots["Finishing"][1],
            F_P = fg_percentage(player_shots["Finishing"][0],player_shots["Finishing"][1]),    
            
            IS_M =player_shots["Inside Shot"][0],
            IS_A =player_shots["Inside Shot"][1],
            
            IS_P = fg_percentage(player_shots["Inside Shot"][0],player_shots["Inside Shot"][1]),
            MR_M =player_shots["Mid-Range"][0],
            MR_A =player_shots["Mid-Range"][1],
            MR_P = fg_percentage(player_shots["Mid-Range"][0],player_shots["Mid-Range"][1]), 
            
            
            _3P_M = player_shots["3-Pointer"][0],   
            _3P_A = player_shots["3-Pointer"][1],
            _3P_P = fg_percentage(player_shots["3-Pointer"][0],player_shots["3-Pointer"][1]), 
            

            _2P_M = player_stats["FG"][0] - player_shots["3-Pointer"][0],
            _2P_A = player_stats["FG"][1] - player_shots["3-Pointer"][1],
            _2P_P = fg_percentage((player_stats["FG"][0] - player_shots["3-Pointer"][0]),(player_stats["FG"][1] - player_shots["3-Pointer"][1])),
            
            
            O_PTS = player_stats["OPTS"],
            O_FG_M = player_stats["OFG"][0],
            O_FG_A = player_stats["OFG"][1],
            O_eFG_P = eFg_percentage(player_stats["OFG"][0],player_defense["3-Pointer"][0],player_stats["OFG"][1]),
            O_3P_M = player_defense["3-Pointer"][0],
            O_3P_A = player_defense["3-Pointer"][1],
            O_3P_P = fg_percentage(player_defense["3-Pointer"][0],player_defense["3-Pointer"][1]),

            O_2P_M = player_stats["OFG"][0] - player_defense["3-Pointer"][0],
            O_2P_A = player_stats["OFG"][1] - player_defense["3-Pointer"][1],
            O_2P_P = fg_percentage((player_stats["FG"][0] - player_defense["3-Pointer"][0]),(player_stats["FG"][1] - player_defense["3-Pointer"][1])),
            

            

            O_F_M = player_defense["Finishing"][0],
            O_F_A = player_defense["Finishing"][1],
            O_F_P = fg_percentage(player_defense["Finishing"][0],player_defense["Finishing"][1]),
            
            O_IS_M = player_defense["Inside Shot"][0],
            O_IS_A = player_defense["Inside Shot"][1],
            O_IS_P = fg_percentage(player_defense["Inside Shot"][0],player_defense["Inside Shot"][1]),
            
            O_MR_M = player_defense["Mid-Range"][0],
            O_MR_A = player_defense["Mid-Range"][1],
            O_MR_P = fg_percentage(player_defense["Mid-Range"][0],player_defense["Mid-Range"][1]),
            
            O_Poss = player_stats["OPoss"],
            Min = player_stats["Min"],
            PTS = player_stats["PTS"],
            FG_M = player_stats["FG"][0],
            FG_A = player_stats["FG"][1],

            eFG_P = eFg_percentage(player_stats["FG"][0],player_shots["3-Pointer"][0],player_stats["FG"][1]),

            FT_M = player_stats["FT"][0],
            FT_A =  player_stats["FT"][1],
            FT_P =  fg_percentage(player_stats["FT"][0],player_stats["FT"][1]),
            
            Off = player_stats["Off"],
            Def = player_stats["Reb"] - player_stats["Off"],
            Rebs = player_stats["Reb"],
            AST = player_stats["AST"],
            STL = player_stats["STL"],
            BLK = player_stats["BLK"],
            TO = player_stats["TO"],
            PF = player_stats["PF"],
            PLUS = player_stats["+/-"],
            DIST = float(player_stats["DIST"]) if player_stats["DIST"] != "-" else None,
            PITP = player_stats["PITP"],
            FBP = player_stats["FBP"],
            FD = player_stats["FD"],
            Poss = player_stats["Poss"],

            Rim_M =player_shot_distance["0-6"][0],
            Rim_A =player_shot_distance["0-6"][1],
            Rim_P = fg_percentage(player_shot_distance["0-6"][0],player_shot_distance["0-6"][1]),

            Mid_M =player_shot_distance["7-20"][0],
            Mid_A =player_shot_distance["7-20"][1],
            Mid_P = fg_percentage(player_shot_distance["7-20"][0],player_shot_distance["7-20"][1]),


            DR_M = player_driving[0] if player_driving is not None else None,
            DR_A = player_driving[1] if player_driving is not None else None,
            DR_P = fg_percentage(player_driving[0], player_driving[1]) if player_driving is not None and player_driving[1] > 0 else None,

            O_Rim_M = player_defense_distance["0-6"][0] if player_defense_distance is not None else 0,
            O_Rim_A = player_defense_distance["0-6"][1] if player_defense_distance is not None else 0,
            O_Rim_P = fg_percentage(player_defense_distance["0-6"][0], player_defense_distance["0-6"][1]) if player_defense_distance is not None else None,

            O_Mid_M = player_defense_distance["7-20"][0] if player_defense_distance is not None else 0,
            O_Mid_A = player_defense_distance["7-20"][1] if player_defense_distance is not None else 0,
            O_Mid_P = fg_percentage(player_defense_distance["7-20"][0], player_defense_distance["7-20"][1]) if player_defense_distance is not None else None,
            OBPM = bpm_values[0], 
            DBPM = bpm_values[1], 
            BPM =  bpm_values[2],

            
            AOBPM = round(.25 * bpm_values[0] + APM_scaler(team_sos), 1) if bpm_values and game_type == "College" else None, 
            ADBPM = round(.25 * bpm_values[1] + APM_scaler(team_sos), 1) if bpm_values and game_type == "College" else None, 
            ABPM =  round(.25 * bpm_values[0] + APM_scaler(team_sos), 1)  + round(.25 * bpm_values[1] + APM_scaler(team_sos), 1) if bpm_values and game_type == "College" else None,  

            OEPM = epm_values[0],
            DEPM = epm_values[1],
            EPM = epm_values[2] ,   

            AOEPM = round(.25 * epm_values[0] + APM_scaler(team_sos), 1) if epm_values and game_type == "College" else None, 
            ADEPM = round(.25 * epm_values[1] + APM_scaler(team_sos), 1) if epm_values and game_type == "College" else None, 
            AEPM =  round(.25 * epm_values[0] + APM_scaler(team_sos), 1)  + round(.25 * epm_values[1] + APM_scaler(team_sos), 1) if epm_values and game_type == "College" else None,       

            #Advanced Statistics
            TS = round((player_stats["PTS"]) / (2 * (player_stats["FG"][1] + 0.48 * player_stats["FT"][1])), 3) \
                if (player_stats["FG"][1] + 0.48 * player_stats["FT"][1]) != 0 else 0,

            _3PAr = round(player_shots["3-Pointer"][1] / player_stats["FG"][1], 3) if player_stats["FG"][1] != 0 else 0,

            FTr = round(player_stats["FT"][1] / player_stats["FG"][1], 3) if player_stats["FG"][1] != 0 else 0,

            # Calculations without using 'denom' as a variable
            ORB_P = round(100 * (player_stats["Off"] * (team_game_stats.Min / 5)) / 
                        (player_stats["Min"] * (team_game_stats.Off + (opp_team_game_stats.Def))), 1) \
                if (player_stats["Min"] * (team_game_stats.Off + (opp_team_game_stats.Def))) != 0 else 0,

            DRB_P = round(100 * ((player_stats["Reb"] - player_stats["Off"])* (team_game_stats.Min / 5)) / 
                        (player_stats["Min"] * (team_game_stats.Def + (opp_team_game_stats.Off))), 1) \
                if (player_stats["Min"] * (team_game_stats.Def + (opp_team_game_stats.Off))) != 0 else 0,

            TRB_P = round(100 * (player_stats["Reb"] * (team_game_stats.Min / 5)) / 
                        (player_stats["Min"] * (team_game_stats.Rebs + opp_team_game_stats.Rebs)), 1) \
                if (player_stats["Min"] * (team_game_stats.Rebs + opp_team_game_stats.Rebs)) != 0 else 0,

            AST_P = round(100 * player_stats["AST"] / 
                        (((player_stats["Min"] / (team_game_stats.Min / 5)) * team_game_stats.FG_M) - player_stats["FG"][0]), 1) \
                if (((player_stats["Min"] / (team_game_stats.Min / 5)) * team_game_stats.FG_M) - player_stats["FG"][0]) != 0 else 0,

            STL_P = round(100 * (player_stats["STL"] * (team_game_stats.Min / 5)) / 
                        (player_stats["Min"] * opp_team_game_stats.Poss), 1) \
                if (player_stats["Min"] * opp_team_game_stats.Poss) != 0 else 0,

            BLK_P = round(100 * (player_stats["BLK"] * (team_game_stats.Min / 5)) / 
                        (player_stats["Min"] * (opp_team_game_stats.FG_A - opp_team_game_stats._3P_A)), 1) \
                if (player_stats["Min"] * (opp_team_game_stats.FG_A - opp_team_game_stats._3P_A)) != 0 else 0,

            TO_P = round(100 * player_stats["TO"] / 
                        (player_stats["FG"][1] + 0.48 * player_stats["FT"][1] + player_stats["TO"]), 1) \
                if (player_stats["FG"][1] + 0.48 * player_stats["FT"][1] + player_stats["TO"]) != 0 else 0,

            USG_P = round(100 * ((player_stats["FG"][1] + 0.48 * player_stats["FT"][1] + player_stats["TO"]) * 
                                (team_game_stats.Min / 5)) / 
                        (player_stats["Min"] * (team_game_stats.FG_A + 0.48 * team_game_stats.FT_A + team_game_stats.TO)), 1) \
                if (player_stats["Min"] * (team_game_stats.FG_A + 0.48 * team_game_stats.FT_A + team_game_stats.TO)) != 0 else 0


        )
        db.session.add(player_avg)
    db.session.flush()










def add_game_helper(game_id):
    

    '''
    #Adds game to DB (Games Table and Offensive and Defense Stats Table)
    #use multiple helper functions 
    '''

    
    with current_app.app_context():
        _ensure_games_cache()
        game_id_int = int(game_id)
        if game_id_int in EXISTING_GAME_IDS:
            return True

        # If game is not in DB Add it 
        gameURL = "http://onlinecollegebasketball.org/game/" + str(game_id)
        
        game_data = gameAnalyzer(gameURL)
        game_data["homeTeam"]["defense"] = transform_defense_names(game_data["homeTeam"]["defense"])
        game_data["awayTeam"]["defense"] = transform_defense_names(game_data["awayTeam"]["defense"])
        
        homeTeamID = game_data["homeTeam"]["teamCode"]
        awayTeamID = game_data["awayTeam"]["teamCode"]

        season_id = game_data["seasonYear"]
        game_type = game_data["gameType"]

        home_team_outcome = game_data["homeTeam"]["outcome"]
        away_team_outcome = game_data["awayTeam"]["outcome"]

        new_game = Game(game_id=game_data["gameCode"], game_type=game_type, season_id=season_id, game_date=game_data["game_date"], 
                        home_team_id=homeTeamID, away_team_id=awayTeamID)
        db.session.add(new_game)
        db.session.flush()

        # Adds both home and away teams to the DB if needed
        get_or_add_team(homeTeamID)
        get_or_add_team(awayTeamID)

        if season_id == current_season:
            if (int(homeTeamID), season_id) not in ROSTER_LOADED_TEAMS:
                homeTeamURL = id_to_url(homeTeamID)
                homeTeamRoster = team_roster_info(homeTeamURL, season_id)
                team_data_to_playerDB(homeTeamRoster)
                ROSTER_LOADED_TEAMS.add((int(homeTeamID), season_id))

            if (int(awayTeamID), season_id) not in ROSTER_LOADED_TEAMS:
                awayTeamURL = id_to_url(awayTeamID)
                awayTeamRoster = team_roster_info(awayTeamURL, season_id)
                team_data_to_playerDB(awayTeamRoster)
                ROSTER_LOADED_TEAMS.add((int(awayTeamID), season_id))
        
        # Add Game Data to Team_stats/offensive_stats/defensive_stats/player_stats
        game_data_to_team_stats(game_data)
        game_data_to_team_off_deff_stats(game_data)

        # Adds Game Data to playerStats
        add_player_stats(game_data)

        home_team_conference_id = get_team_conference(homeTeamID, season_id)
        away_team_conference_id = get_team_conference(awayTeamID, season_id)

        all_players = game_data["homeTeam"]["players"] + game_data["awayTeam"]["players"]

        EXCLUDED_AVG_GAME_TYPES = {"Non-Conference", "Exhibition", "Invitational"}
        if game_type not in EXCLUDED_AVG_GAME_TYPES:
            update_team_avg(homeTeamID, season_id, game_data["gameType"], "opponent", away_team_outcome, game_data["awayTeam"]["totalShots"], game_data["awayTeam"]["shot_distance"], game_data["awayTeam"]["stats"], game_data["homeTeam"]["stats"], home_team_conference_id, team_driving=game_data["awayTeam"].get("driving"))
            update_team_avg(awayTeamID, season_id, game_data["gameType"], "opponent", home_team_outcome, game_data["homeTeam"]["totalShots"], game_data["homeTeam"]["shot_distance"], game_data["homeTeam"]["stats"], game_data["awayTeam"]["stats"], away_team_conference_id, team_driving=game_data["homeTeam"].get("driving"))
            
            update_team_avg(homeTeamID, season_id, game_data["gameType"], "team", home_team_outcome, game_data["homeTeam"]["totalShots"], game_data["homeTeam"]["shot_distance"], game_data["homeTeam"]["stats"], game_data["awayTeam"]["stats"], home_team_conference_id, team_driving=game_data["homeTeam"].get("driving"))
            update_team_avg(awayTeamID, season_id, game_data["gameType"], "team", away_team_outcome, game_data["awayTeam"]["totalShots"], game_data["awayTeam"]["shot_distance"], game_data["awayTeam"]["stats"], game_data["homeTeam"]["stats"], away_team_conference_id, team_driving=game_data["awayTeam"].get("driving"))

            for player in all_players:
                update_player_avg(player["playerCode"], season_id, game_type, player["position"], player["shots"], player["shot_distance"], player["defense"], player["stats"], player["pos_min"], player_driving=player.get("driving"), player_defense_distance=player.get("defense_distance"))

        EXCLUDED_GAME_TYPES = {"Exhibition", "Invitational"}
        if game_type not in EXCLUDED_GAME_TYPES:
            update_team_avg(homeTeamID, season_id, "College", "opponent", away_team_outcome, game_data["awayTeam"]["totalShots"], game_data["awayTeam"]["shot_distance"], game_data["awayTeam"]["stats"], game_data["homeTeam"]["stats"], home_team_conference_id, team_driving=game_data["awayTeam"].get("driving"))
            update_team_avg(awayTeamID, season_id, "College", "opponent", home_team_outcome, game_data["homeTeam"]["totalShots"], game_data["homeTeam"]["shot_distance"], game_data["homeTeam"]["stats"], game_data["awayTeam"]["stats"], away_team_conference_id, team_driving=game_data["homeTeam"].get("driving"))

            update_team_avg(homeTeamID, season_id, "College", "team", home_team_outcome, game_data["homeTeam"]["totalShots"], game_data["homeTeam"]["shot_distance"], game_data["homeTeam"]["stats"], game_data["awayTeam"]["stats"], home_team_conference_id, team_driving=game_data["homeTeam"].get("driving"))
            update_team_avg(awayTeamID, season_id, "College", "team", away_team_outcome, game_data["awayTeam"]["totalShots"], game_data["awayTeam"]["shot_distance"], game_data["awayTeam"]["stats"], game_data["homeTeam"]["stats"], away_team_conference_id, team_driving=game_data["awayTeam"].get("driving"))

            for player in all_players:
                update_player_avg(player["playerCode"], season_id, "College", player["position"], player["shots"], player["shot_distance"], player["defense"], player["stats"], player["pos_min"], player_driving=player.get("driving"), player_defense_distance=player.get("defense_distance"))

        db.session.commit()
        EXISTING_GAME_IDS.add(game_id_int)
        return new_game



#Updates Team Roster for current Season 
def update_team_roster_db(teamID):
    """
    Adds new players to the Player and PlayerSkills tables.
    Updates existing players' team and name.
    Updates existing player skills for the current season.
    """

    with current_app.app_context():

        
        teamURL = id_to_url(teamID)

        '''
        teamRosterFolder = "backend/TeamRosterPage"
        #team_file = os.path.join(teamRosterFolder, f"{teamID}-{current_season}.html")
        team_file = f"{teamRosterFolder}/{teamID}-{current_season}.html"
        
        delete_file(team_file)
        print(f"{team_file}")
        '''
        team_data = team_roster_info(teamURL,current_season)
        

        teamID = team_data["teamID"]

        for player in team_data["players"]:
            player_id = player["playerID"]
            player_name = player["name"]

            # Check if player already exists
            existing_player = Player.query.filter_by(player_id=player_id).first()

            if existing_player:
                # Update player information if needed
                existing_player.team_id = teamID
                existing_player.name = player_name
            else:
                # Add new player
                new_player = Player(player_id=player_id, team_id=teamID, name=player_name)
                db.session.add(new_player)

            # Check if player skills exist for the current season
            existing_skills = PlayerSkills.query.filter_by(player_id=player_id, season_id=current_season).first()
            skill_data = {
                "Pos": player.get("Pos"),
                "Class": player.get("Class"),
                "height":player.get("height"),
                "weight":player.get("weight"),
                "wingspan":player.get("wingspan"),
                "vertical":player.get("vertical"),
                "IS": player.get("IS"),
                "IQ": player.get("IQ"),
                "OS": player.get("OS"),
                "Pass": player.get("Pass"),
                "Rng": player.get("Rng"),
                "Hnd": player.get("Hnd"),
                "Fin": player.get("Fin"),
                "Drv": player.get("Drv"),
                "Reb": player.get("Reb"),
                "Str": player.get("Str"),
                "IDef": player.get("IDef"),
                "Spd": player.get("Spd"),
                "PDef": player.get("PDef"),
                "Sta": player.get("Sta"),
                "SI": player.get("SI"),
                "POT": player.get("POT"),
                "Stars": player.get("Stars")
            }

            if existing_skills:
                # Update existing skills
                for key, value in skill_data.items():
                    #print(existing_skills, key,value)
                    setattr(existing_skills, key, value)
            else:
                # Add new player skills
                new_player_skills = PlayerSkills(player_id=player_id, season_id=current_season, **skill_data)
                db.session.add(new_player_skills)

        try:
            # Commit all changes in one transaction
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

