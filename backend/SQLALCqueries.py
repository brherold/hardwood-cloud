import os
import sys

# Ensure backend directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from models import *
from server import app  # Import the app object from app.py
from sqlalchemy.inspection import inspect
from sqlalchemy import func
#from scripts.pygameAnalyzerAPI import *



#Can use this to query get request and combine data instead of regular sql 

# Use the app context to allow the query to work


#Gets Game Logs of  Player in a given Season
def game_log_finder(player_id, season_id):
    gameCount = 1
    gameLogDic = {}
    with app.app_context():
        player = Player.query.get(player_id)
        for stat in player.player_stats:
            gameInfo = stat.game
            if gameInfo.season_id == 2044:
                gameLogDic[gameCount] = {column.name: getattr(stat, column.name) for column in PlayerStats.__table__.columns}
                gameCount += 1
        return gameLogDic

print(game_log_finder(205173,2044))
    