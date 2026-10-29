import os
import sys

# Ensure backend directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from extensions import db

# Alias so both 'models' and 'backend.models' resolve to this module instance
if 'backend.models' not in sys.modules:
    sys.modules['backend.models'] = sys.modules[__name__]
if 'models' not in sys.modules:
    sys.modules['models'] = sys.modules[__name__]
# Season Table
class Season(db.Model):
    __tablename__ = "seasons"  # table name

    season_id = db.Column(db.Integer, primary_key=True)  # columns
    year = db.Column(db.Integer)

#Confernece Table
class Conference(db.Model): 
    __tablename__ = "conferences"

    conference_id = db.Column(db.Integer,primary_key=True)
    conference_name = db.Column(db.String)

    division_id = db.Column(db.Integer) #1,2,3


# Game Table
class Game(db.Model):

    __tablename__ = "games"
    
    game_id = db.Column(db.Integer, primary_key=True)
    game_type = db.Column(db.String)
    season_id = db.Column(db.Integer, db.ForeignKey('seasons.season_id'))
    game_date = db.Column(db.Integer)
    home_team_id = db.Column(db.Integer, db.ForeignKey('teams.team_id'))
    away_team_id = db.Column(db.Integer, db.ForeignKey('teams.team_id'))

    home_team = db.relationship('Team', foreign_keys=[home_team_id], backref='home_games')
    away_team = db.relationship('Team', foreign_keys=[away_team_id], backref='away_games')
    '''
    season = db.relationship('Season', backref='games')
    home_team = db.relationship('Team', foreign_keys=[home_team_id], backref='home_games')
    away_team = db.relationship('Team', foreign_keys=[away_team_id], backref='away_games')
    '''

class OffenseStats(db.Model):
    __tablename__ = "offense_stats"

    game_id = db.Column(db.Integer, db.ForeignKey("games.game_id"), primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.team_id"), primary_key=True)
    defense_type = db.Column(db.String, primary_key=True)  # e.g., "man-to-man", "zone"

    plays = db.Column(db.Integer, default = 0)
    F_M = db.Column(db.Integer, default=0)
    F_A = db.Column(db.Integer, default=0)
    IS_M = db.Column(db.Integer, default=0)
    IS_A = db.Column(db.Integer, default=0)
    MR_M = db.Column(db.Integer, default=0)
    MR_A = db.Column(db.Integer, default=0)
    _3P_M = db.Column(db.Integer, default=0)
    _3P_A = db.Column(db.Integer, default=0)
    Rim_M = db.Column(db.Integer, default=0)
    Rim_A = db.Column(db.Integer, default=0)
    Mid_M = db.Column(db.Integer, default=0)
    Mid_A = db.Column(db.Integer, default=0)
    FT_M = db.Column(db.Integer, default=0)
    FT_A = db.Column(db.Integer, default=0)
    DR_M = db.Column(db.Integer, default=0)
    DR_A = db.Column(db.Integer, default=0)
    TOV = db.Column(db.Integer, default=0)

    game = db.relationship('Game', backref='off_game_info') #Allows to get seasonID and game_type

    # Relationships
    '''
    game = db.relationship("Game", backref="total_shots")
    team = db.relationship("Team", backref="total_shots")
    '''

class DefenseStats(db.Model):
    __tablename__ = "defense_stats"

    game_id = db.Column(db.Integer, db.ForeignKey("games.game_id"), primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.team_id"), primary_key=True)
    defense_type = db.Column(db.String, primary_key= True)  # Different defense strategies

    plays = db.Column(db.Integer, default = 0)
    F_M = db.Column(db.Integer, default=0)
    F_A = db.Column(db.Integer, default=0)
    IS_M = db.Column(db.Integer, default=0)
    IS_A = db.Column(db.Integer, default=0)
    MR_M = db.Column(db.Integer, default=0)
    MR_A = db.Column(db.Integer, default=0)
    _3P_M = db.Column(db.Integer, default=0)
    _3P_A = db.Column(db.Integer, default=0)
    Rim_M = db.Column(db.Integer, default=0)
    Rim_A = db.Column(db.Integer, default=0)
    Mid_M = db.Column(db.Integer, default=0)
    Mid_A = db.Column(db.Integer, default=0)
    FT_M = db.Column(db.Integer, default=0)
    FT_A = db.Column(db.Integer, default=0)
    DR_M = db.Column(db.Integer, default=0)
    DR_A = db.Column(db.Integer, default=0)
    TOV = db.Column(db.Integer, default=0)

    game = db.relationship('Game', backref='def_game_info') #Allows to get seasonID and game_type
    # Relationships
    '''
    game = db.relationship("Game", backref="defense_stats")
    team = db.relationship("Team", backref="defense_stats")
    '''


    

# Team Table
class Team(db.Model):
    __tablename__ = "teams"

    team_id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String)

    team_stats = db.relationship("TeamStats",backref="team")
    offense_stats = db.relationship("OffenseStats", backref="team")
    offense_stats = db.relationship("DefenseStats", backref="team")
    players = db.relationship("Player", backref = "team")

# Team Stats Table
class TeamStats(db.Model):
    __tablename__ = "team_stats"

    game_id = db.Column(db.Integer, db.ForeignKey("games.game_id"), primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.team_id"), primary_key=True)
    
    outcome = db.Column(db.Integer)
    

    Min = db.Column(db.Integer)
    PTS = db.Column(db.Integer)
    FG_M = db.Column(db.Integer, default=0)
    FG_A = db.Column(db.Integer, default=0)
    eFG_P = db.Column(db.Float)
    _3P_M = db.Column(db.Integer, default=0)
    _3P_A = db.Column(db.Integer, default=0)
    _3P_P = db.Column(db.Float)
    _2P_M= db.Column(db.Integer, default=0)
    _2P_A = db.Column(db.Integer, default=0)
    _2P_P = db.Column(db.Float)
    FT_M = db.Column(db.Integer)
    FT_A = db.Column(db.Integer)
    FT_P = db.Column(db.Float)
    Off = db.Column(db.Integer)
    Def = db.Column(db.Integer)
    Rebs = db.Column(db.Integer)
    AST = db.Column(db.Integer)
    STL = db.Column(db.Integer)
    BLK = db.Column(db.Integer)
    TO = db.Column(db.Integer)
    PF = db.Column(db.Integer)
    PLUS = db.Column(db.Integer)
    DIST = db.Column(db.Float)
    PITP = db.Column(db.Integer)
    FBP = db.Column(db.Integer)
    FD = db.Column(db.Integer)
    Fat = db.Column(db.String)
    
    F_M = db.Column(db.Float, default=0)
    F_A = db.Column(db.Float, default=0)
    F_P = db.Column(db.Float)
    IS_M = db.Column(db.Float, default=0)
    IS_A = db.Column(db.Float, default=0)
    IS_P = db.Column(db.Float)
    MR_M = db.Column(db.Float, default=0)
    MR_A = db.Column(db.Float, default=0)
    MR_P = db.Column(db.Float)
    Rim_M = db.Column(db.Float, default=0)
    Rim_A = db.Column(db.Float, default=0)
    Rim_P = db.Column(db.Float)
    Mid_M = db.Column(db.Float, default=0)
    Mid_A = db.Column(db.Float, default=0)
    Mid_P =  db.Column(db.Float)
    DR_M = db.Column(db.Float, default=0)
    DR_A = db.Column(db.Float, default=0)
    DR_P = db.Column(db.Float)
    Poss = db.Column(db.Float)

    O_Poss = db.Column(db.Float)
    O_PTS = db.Column(db.Float)
    O_FG_M = db.Column(db.Float, default=0)
    O_FG_A = db.Column(db.Float, default=0)
    O_eFG_P = db.Column(db.Float)
    O_3P_M = db.Column(db.Float)
    O_3P_A = db.Column(db.Float)
    O_3P_P = db.Column(db.Float)
    O_2P_M = db.Column(db.Float, default=0)
    O_2P_A = db.Column(db.Float, default=0)
    O_2P_P = db.Column(db.Float)
    
    
    O_F_M = db.Column(db.Float)
    O_F_A = db.Column(db.Float)
    O_F_P = db.Column(db.Float)
    O_IS_M = db.Column(db.Float)
    O_IS_A = db.Column(db.Float)
    O_IS_P = db.Column(db.Float)
    O_MR_M = db.Column(db.Float)
    O_MR_A = db.Column(db.Float)
    O_MR_P = db.Column(db.Float)
    O_Rim_M = db.Column(db.Float, default=0)
    O_Rim_A = db.Column(db.Float, default=0)
    O_Rim_P = db.Column(db.Float)
    O_Mid_M = db.Column(db.Float, default=0)
    O_Mid_A = db.Column(db.Float, default=0)
    O_Mid_P = db.Column(db.Float)
    O_DR_M = db.Column(db.Float, default=0)
    O_DR_A = db.Column(db.Float, default=0)
    O_DR_P = db.Column(db.Float)
    OBPM = db.Column(db.Float)
    DBPM = db.Column(db.Float)
    BPM = db.Column(db.Float)



    game = db.relationship('Game', backref='team_game_info') #Allows to get seasonID and game_type from teamStats
    '''
    game = db.relationship('Game', backref='team_stats')
    team = db.relationship('Team', backref='team_stats')
    season = db.relationship('Season', backref='team_stats')
    '''

# Team Avg Stats Table
class TeamAvg(db.Model):
    __tablename__ = "team_avg"

    team_id = db.Column(db.Integer, db.ForeignKey("teams.team_id"), primary_key=True)
    season_id = db.Column(db.Integer, db.ForeignKey("seasons.season_id"), primary_key=True)
    game_type = db.Column(db.String, primary_key=True)
    stat_type = db.Column(db.String,primary_key=True) #Holds stat type (team or opponent)
    conference_id = db.Column(db.Integer,db.ForeignKey("conferences.conference_id"))
    

    GW = db.Column(db.Integer) #Games Won
    GP = db.Column(db.Integer) #Games Played
    Min = db.Column(db.Float)
    PTS = db.Column(db.Float)
    FG_M = db.Column(db.Float, default=0)
    FG_A = db.Column(db.Float, default=0)
    eFG_P = db.Column(db.Float)
    _3P_M = db.Column(db.Float, default=0)
    _3P_A = db.Column(db.Float, default=0)
    _3P_P = db.Column(db.Float)
    _2P_M = db.Column(db.Float, default=0)
    _2P_A = db.Column(db.Float, default=0)
    _2P_P = db.Column(db.Float)
    
    FT_M = db.Column(db.Float)
    FT_A = db.Column(db.Float)
    FT_P = db.Column(db.Float)
    Off = db.Column(db.Float)
    Def = db.Column(db.Float)
    Rebs = db.Column(db.Float)
    AST = db.Column(db.Float)
    STL = db.Column(db.Float)
    BLK = db.Column(db.Float)
    TO = db.Column(db.Float)
    PF = db.Column(db.Float)
    PLUS = db.Column(db.Float)
    DIST = db.Column(db.Float)
    PITP = db.Column(db.Float)
    FBP = db.Column(db.Float)
    FD = db.Column(db.Float)

    
    F_M = db.Column(db.Float, default=0)
    F_A = db.Column(db.Float, default=0)
    F_P = db.Column(db.Float)
    IS_M = db.Column(db.Float, default=0)
    IS_A = db.Column(db.Float, default=0)
    IS_P = db.Column(db.Float)
    MR_M = db.Column(db.Float, default=0)
    MR_A = db.Column(db.Float, default=0)
    MR_P = db.Column(db.Float)
    Rim_M = db.Column(db.Float, default=0)
    Rim_A = db.Column(db.Float, default=0)
    Rim_P = db.Column(db.Float)
    Mid_M = db.Column(db.Float, default=0)
    Mid_A = db.Column(db.Float, default=0)
    Mid_P =  db.Column(db.Float)
    DR_M = db.Column(db.Float, default=0)
    DR_A = db.Column(db.Float, default=0)
    DR_P = db.Column(db.Float)
    Poss = db.Column(db.Float)
    
    OBPM = db.Column(db.Float)
    DBPM = db.Column(db.Float)
    BPM = db.Column(db.Float)

    #Adjusted BPM scores (uses SOS)
    AOBPM = db.Column(db.Float)
    ADBPM = db.Column(db.Float)
    ABPM = db.Column(db.Float)

    TS = db.Column(db.Float)
    _3PAr = db.Column(db.Float)
    FTr = db.Column(db.Float)

    ORtg = db.Column(db.Float)
    NetRtg = db.Column(db.Float)
    TO_P = db.Column(db.Float)
    FT_FG_A = db.Column(db.Float)
    ORB_P = db.Column(db.Float)
    DRB_P = db.Column(db.Float)

    SOS = db.Column(db.Float)
    RPI = db.Column(db.Float)





    #game = db.relationship('Game', backref='team_game_info') #Allows to get seasonID and game_type from teamStats
    '''
    game = db.relationship('Game', backref='team_stats')
    team = db.relationship('Team', backref='team_stats')
    season = db.relationship('Season', backref='team_stats')
    '''






# Player Stats Table
class PlayerStats(db.Model):
    __tablename__ = "player_stats"

    player_id = db.Column(db.Integer, db.ForeignKey("players.player_id"), primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("games.game_id"), primary_key=True)
    #season_id = db.Column(db.Integer, db.ForeignKey("seasons.season_id"))
    
    Pos = db.Column(db.String)
    GS = db.Column(db.Integer)
    PG_Min = db.Column(db.Integer, default=0)
    SG_Min = db.Column(db.Integer, default=0)
    SF_Min = db.Column(db.Integer, default=0)
    PF_Min = db.Column(db.Integer, default=0)
    C_Min = db.Column(db.Integer, default=0)
    Min = db.Column(db.Integer)
    PTS = db.Column(db.Integer)
    FG_M = db.Column(db.Integer, default=0)
    FG_A = db.Column(db.Integer, default=0)
    eFG_P = db.Column(db.Float)
    _3P_M = db.Column(db.Integer, default=0)
    _3P_A = db.Column(db.Integer, default=0)
    _3P_P = db.Column(db.Float)
    _2P_M= db.Column(db.Integer, default=0)
    _2P_A = db.Column(db.Integer, default=0)
    _2P_P = db.Column(db.Float)
    FT_M = db.Column(db.Integer)
    FT_A = db.Column(db.Integer)
    FT_P = db.Column(db.Float)
    Off = db.Column(db.Integer)
    Def = db.Column(db.Integer)
    Rebs = db.Column(db.Integer)
    AST = db.Column(db.Integer)
    STL = db.Column(db.Integer)
    BLK = db.Column(db.Integer)
    TO = db.Column(db.Integer)
    PF = db.Column(db.Integer)
    PLUS = db.Column(db.Integer)
    DIST = db.Column(db.Float)
    PITP = db.Column(db.Integer)
    FBP = db.Column(db.Integer)
    FD = db.Column(db.Integer)
    Fat = db.Column(db.String)
    F_M = db.Column(db.Float, default=0)
    F_A = db.Column(db.Float, default=0)
    F_P = db.Column(db.Float)
    IS_M = db.Column(db.Float, default=0)
    IS_A = db.Column(db.Float, default=0)
    IS_P = db.Column(db.Float)
    MR_M = db.Column(db.Float, default=0)
    MR_A = db.Column(db.Float, default=0)
    MR_P = db.Column(db.Float)
    Rim_M = db.Column(db.Float, default=0)
    Rim_A = db.Column(db.Float, default=0)
    Rim_P = db.Column(db.Float)
    Mid_M = db.Column(db.Float, default=0)
    Mid_A = db.Column(db.Float, default=0)
    Mid_P =  db.Column(db.Float)
    DR_M = db.Column(db.Float)
    DR_A = db.Column(db.Float)
    DR_P = db.Column(db.Float)
    Poss = db.Column(db.Float)

    O_Poss = db.Column(db.Float)
    O_PTS = db.Column(db.Float)
    O_FG_M = db.Column(db.Float, default=0)
    O_FG_A = db.Column(db.Float, default=0)
    O_eFG_P = db.Column(db.Float)
    O_3P_M = db.Column(db.Float)
    O_3P_A = db.Column(db.Float)
    O_3P_P = db.Column(db.Float)
    O_2P_M = db.Column(db.Float, default=0)
    O_2P_A = db.Column(db.Float, default=0)
    O_2P_P = db.Column(db.Float)
    
    O_F_M = db.Column(db.Float)
    O_F_A = db.Column(db.Float)
    O_F_P = db.Column(db.Float)
    O_IS_M = db.Column(db.Float)
    O_IS_A = db.Column(db.Float)
    O_IS_P = db.Column(db.Float)
    O_MR_M = db.Column(db.Float)
    O_MR_A = db.Column(db.Float)
    O_MR_P = db.Column(db.Float)
    O_Rim_M = db.Column(db.Float, default=0)
    O_Rim_A = db.Column(db.Float, default=0)
    O_Rim_P = db.Column(db.Float)
    O_Mid_M = db.Column(db.Float, default=0)
    O_Mid_A = db.Column(db.Float, default=0)
    O_Mid_P = db.Column(db.Float)
    O_DR_M = db.Column(db.Float)
    O_DR_A = db.Column(db.Float)
    O_DR_P = db.Column(db.Float)

    OBPM = db.Column(db.Float)
    DBPM = db.Column(db.Float)
    BPM = db.Column(db.Float)

    #Real BPM (testing)
    OEPM = db.Column(db.Float)
    DEPM = db.Column(db.Float)
    EPM = db.Column(db.Float)
    game = db.relationship('Game', backref='player_game_info') #Allows to get seasonID and game_type from playerStats
    '''
    game = db.relationship('Game', backref='player_stats')
    season = db.relationship('Season', backref='player_stats')
    team = db.relationship('Team', backref='player_stats')
    '''

# Player Avg Stats Table
class PlayerAvg(db.Model):
    __tablename__ = "player_avg"

    player_id = db.Column(db.Integer, db.ForeignKey("players.player_id"), primary_key=True)
    season_id = db.Column(db.Integer, db.ForeignKey("seasons.season_id"), primary_key=True)
    game_type = db.Column(db.String, primary_key=True)
    GS = db.Column(db.Integer)
    GP = db.Column(db.Integer) #Games Played
    #Minutes for Each Position
    PG_Min = db.Column(db.Float)
    SG_Min = db.Column(db.Float)
    SF_Min = db.Column(db.Float)
    PF_Min = db.Column(db.Float)
    C_Min = db.Column(db.Float)
    #
    Min = db.Column(db.Float)
    PTS = db.Column(db.Float)
    FG_M = db.Column(db.Float, default=0)
    FG_A = db.Column(db.Float, default=0)
    eFG_P = db.Column(db.Float)
    _3P_M = db.Column(db.Float, default=0)
    _3P_A = db.Column(db.Float, default=0)
    _3P_P = db.Column(db.Float)
    _2P_M = db.Column(db.Float, default=0)
    _2P_A = db.Column(db.Float, default=0)
    _2P_P = db.Column(db.Float)
    
    FT_M = db.Column(db.Float)
    FT_A = db.Column(db.Float)
    FT_P = db.Column(db.Float)
    Off = db.Column(db.Float)
    Def = db.Column(db.Float)
    Rebs = db.Column(db.Float)
    AST = db.Column(db.Float)
    STL = db.Column(db.Float)
    BLK = db.Column(db.Float)
    TO = db.Column(db.Float)
    PF = db.Column(db.Float)
    PLUS = db.Column(db.Float)
    DIST = db.Column(db.Float)
    PITP = db.Column(db.Float)
    FBP = db.Column(db.Float)
    FD = db.Column(db.Float)


    F_M = db.Column(db.Float, default=0)
    F_A = db.Column(db.Float, default=0)
    F_P = db.Column(db.Float)
    IS_M = db.Column(db.Float, default=0)
    IS_A = db.Column(db.Float, default=0)
    IS_P = db.Column(db.Float)
    MR_M = db.Column(db.Float, default=0)
    MR_A = db.Column(db.Float, default=0)
    MR_P = db.Column(db.Float)
    Rim_M = db.Column(db.Float, default=0)
    Rim_A = db.Column(db.Float, default=0)
    Rim_P = db.Column(db.Float)
    Mid_M = db.Column(db.Float, default=0)
    Mid_A = db.Column(db.Float, default=0)
    Mid_P =  db.Column(db.Float)
    Poss = db.Column(db.Float)
    
    O_Poss = db.Column(db.Float)
    O_PTS = db.Column(db.Float)
    O_FG_M = db.Column(db.Float, default=0)
    O_FG_A = db.Column(db.Float, default=0)
    O_eFG_P = db.Column(db.Float)
    O_3P_M = db.Column(db.Float)
    O_3P_A = db.Column(db.Float)
    O_3P_P = db.Column(db.Float)
    O_2P_M = db.Column(db.Float, default=0)
    O_2P_A = db.Column(db.Float, default=0)
    O_2P_P = db.Column(db.Float)
    
    
    O_F_M = db.Column(db.Float)
    O_F_A = db.Column(db.Float)
    O_F_P = db.Column(db.Float)
    O_IS_M = db.Column(db.Float)
    O_IS_A = db.Column(db.Float)
    O_IS_P = db.Column(db.Float)
    O_MR_M = db.Column(db.Float)
    O_MR_A = db.Column(db.Float)
    O_MR_P = db.Column(db.Float)
    O_Rim_M = db.Column(db.Float, default=0)
    O_Rim_A = db.Column(db.Float, default=0)
    O_Rim_P = db.Column(db.Float)
    O_Mid_M = db.Column(db.Float, default=0)
    O_Mid_A = db.Column(db.Float, default=0)
    O_Mid_P = db.Column(db.Float)
    DR_M = db.Column(db.Float)
    DR_A = db.Column(db.Float)
    DR_P = db.Column(db.Float)
    OBPM = db.Column(db.Float)
    DBPM = db.Column(db.Float)
    BPM = db.Column(db.Float)

    #Adjusted BPM scores (uses SOS)
    AOBPM = db.Column(db.Float)
    ADBPM = db.Column(db.Float)
    ABPM = db.Column(db.Float)

    #Real BPM (testing)
    OEPM = db.Column(db.Float)
    DEPM = db.Column(db.Float)
    EPM = db.Column(db.Float)

    AOEPM = db.Column(db.Float)
    ADEPM = db.Column(db.Float)
    AEPM = db.Column(db.Float)

    
    TS = db.Column(db.Float)
    _3PAr = db.Column(db.Float)
    FTr = db.Column(db.Float)
    ORB_P = db.Column(db.Float)
    DRB_P = db.Column(db.Float)
    TRB_P = db.Column(db.Float)
    AST_P = db.Column(db.Float)
    STL_P = db.Column(db.Float)
    BLK_P = db.Column(db.Float)
    TO_P = db.Column(db.Float)
    USG_P = db.Column(db.Float)

    #game = db.relationship('Game', backref='player_game_info') #Allows to get seasonID and game_type from playerStats
    '''
    game = db.relationship('Game', backref='player_stats')
    season = db.relationship('Season', backref='player_stats')
    team = db.relationship('Team', backref='player_stats')
    '''
    
    
# Player Table
class Player(db.Model):
    __tablename__ = "players"

    player_id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.team_id"))
    name = db.Column(db.String)


    player_stats = db.relationship('PlayerStats',backref="player") #able to get player_stats from player table 
    player_skills = db.relationship("PlayerSkills",backref="player") #able to get player_skills from player table

    '''
    team = db.relationship('Team', backref='players')
    player_stats = db.relationship('PlayerStats', backref='player')
    player_totals = db.relationship('PlayerTotals', backref='player')
    '''

# Player Skills Table
class PlayerSkills(db.Model):
    __tablename__ = "players_skills"

    player_id = db.Column(db.Integer, db.ForeignKey("players.player_id"), primary_key=True)
    season_id = db.Column(db.Integer, db.ForeignKey("seasons.season_id"), primary_key=True)
    Pos = db.Column(db.String)
    Class = db.Column(db.String)
    height = db.Column(db.Float)
    weight = db.Column(db.Integer)
    wingspan = db.Column(db.Float)
    vertical = db.Column(db.Float)
    IS = db.Column(db.Integer)
    OS = db.Column(db.Integer)
    Rng = db.Column(db.Integer)
    Fin = db.Column(db.Integer)
    Reb = db.Column(db.Integer)
    IDef = db.Column(db.Integer)
    PDef = db.Column(db.Integer)
    IQ = db.Column(db.Integer)
    Pass = db.Column(db.Integer)
    Hnd = db.Column(db.Integer)
    Drv = db.Column(db.Integer)
    Str = db.Column(db.Integer)
    Spd = db.Column(db.Integer)
    Sta = db.Column(db.Integer)
    SI = db.Column(db.Integer)
    POT = db.Column(db.Integer)
    Stars = db.Column(db.Integer)




