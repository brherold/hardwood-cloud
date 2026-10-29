#Holds  getRequest Functions
import os
import sys

# Ensure backend directory is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from models import *
from server import app  # Import the app object from app.py
from sqlalchemy.inspection import inspect
from sqlalchemy import func
from .pygameAnalyzerAPI import *

######################################################################  Player ########################################################################################

#Gets Game Logs of  Player in a given Season
def game_log_finder(player_id, season_id):
    gameCount = 1
    gameLogDic = {}
    with app.app_context():
        player = Player.query.get(player_id)
        for stat in player.player_stats:
            gameInfo = stat.game
            if gameInfo.season_id == season_id:
                gameLogDic[gameCount] = {column.name: getattr(stat, column.name) for column in PlayerStats.__table__.columns}
                gameCount += 1
        return gameLogDic
    
#Gets the Player's avgs from a certain season and game_type
def avg_stats_finder(player_id, season_id, game_type):
    averages = {}
    if game_type not in ["Exhibition","College","Non-Conference","Conference","Playoff","Tournament", "Invitational"]:
        return None
    with app.app_context(): # Ensure the app context is active
        stats = [
    "Min", "PTS", "FG_M","FG_A", "_3P_M", "_3P_A", "FT_M", "FT_A", "Off" ,"Rebs", "AST", "STL", "BLK", "TO", "PF", "FD",
    "F_M", "F_A", "IS_M", "IS_A", "MR_M", "MR_A", 
    "O_F_M", "O_F_A", "O_IS_M", "O_IS_A", "O_MR_M", "O_MR_A", "O_3P_M", "O_3P_A"
]  # List of columns you want the average for
        for stat in stats:
            if game_type == "College":
                avg =  (
                db.session.query(func.avg(getattr(PlayerStats, stat)))
                .join(Game, PlayerStats.game_id == Game.game_id)
                .filter(PlayerStats.player_id == player_id, Game.season_id == season_id, (~Game.game_type.in_(["Exhibition", "Invitational"]) # does not include "Exhbiiton or Invitational"
))
                .scalar()
                )
            else:    
                avg =  (
                    db.session.query(func.avg(getattr(PlayerStats, stat)))
                    .join(Game, PlayerStats.game_id == Game.game_id)
                    .filter(PlayerStats.player_id == player_id, Game.season_id == season_id, Game.game_type == game_type)
                    .scalar()
                )
                
            averages[stat] = round(avg,1) if avg is not None else None
    return averages



######################################################################  Team ########################################################################################

#Gets Avgs of All players in a Team in a given season and game_Type
def avg_player_stats_from_Team(team_id,season_id,game_type):
    stats = []
    with app.app_context():
        team = Team.query.get(team_id)
        players = team.players
        for player in players:
            player_skills = player.player_skills
            for player_skill in player_skills:
                if player_skill.season_id == season_id:
                    stats.append((player.name,avg_stats_finder(player.player_id,season_id,game_type)))
        
    return stats



######################################################################  Game ########################################################################################
#Get All information for Game Box Score (use pygameAnalyzerAPI)
def box_score(game_id):
    with app.app_context():  # Ensure the app context is active
        game = Game.query.get(game_id)
        if game:
            return (gameAnalyzer("http://onlinecollegebasketball.org/game/" + str(game_id)))
        else:
            return None