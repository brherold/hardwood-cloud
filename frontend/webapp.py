import os
import sys
from flask import Flask, render_template, request, redirect, url_for, jsonify

FRONTEND_DIR = os.path.dirname(os.path.abspath(__file__))
if FRONTEND_DIR not in sys.path:
    sys.path.insert(0, FRONTEND_DIR)

from getData import *

#Keep Note (Website shown EPM is db BPM)

app = Flask(__name__, template_folder=os.path.join(FRONTEND_DIR, 'templates'))

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        code = request.form["code"]

        if len(code) > 4:
            game_code = code
            return redirect(url_for('gameBoxScore', code=game_code))
        else:
                
            team_id = request.form["code"]
            season_id = 2054
            return redirect(url_for('teamStats', code=team_id, season_year=season_id))
    
    return render_template('home.html')

#Route to get to Team Stats for Given year
@app.route("/teams/<code>/<season_year>/<game_type>")
@app.route('/teams/<code>/<season_year>', methods=['GET', 'POST'], defaults={'game_type': 'College'})
def teamStats(code, season_year, game_type):
    team_id = int(code)
    season_id = int(season_year)

    #If Error (no season stats or game_type stats)
    try:
        roster = getRoster(team_id, season_id)
        team_avg = getTeamAvg(team_id, season_id, game_type)
        opp_avg = getOppAvg(team_id, season_id, game_type)
        team_player_avg = getTeamPlayerAvg(team_id, game_type, season_id)
        team_offense = getTeamOffense(team_id,season_id,game_type)
        team_defense = getTeamDefense(team_id,season_id,game_type)
        team_rank = getTeamRank(team_id,season_id,game_type)
        opp_rank = getOppRank(team_id,season_id,game_type)
    except:
        #Error Page
        return render_template('error.html')

    for player in team_player_avg:
        denom = team_avg["GP"] * 40
        player["VORP"] = ((player["EPM"] + 3) * player["Min"] * (player["GP"]))/denom
        #player["WAR"] = player["VORP"] * .1205 * team_avg["GP"] / 5




    return render_template('teamPage.html', team_code= code, season_id = season_id, game_type = game_type, roster=roster, team_stats=team_avg, opp_stats=opp_avg, player_stats=team_player_avg, team_offense = team_offense, team_defense=team_defense, team_rank=team_rank, opp_rank=opp_rank)

#Route to get to Game Log for given year
@app.route('/teams/<code>/<season_year>/gamelog')
def gameLog(code, season_year):
    team_id = int(code)
    season_id = int(season_year)

    game_log = getTeamGameLog(team_id,season_id)

    return render_template('teamGameLog.html', game_log = game_log, season_id = season_id)

#Route to go to Game Box Score Stats
@app.route('/games/<code>')
def gameBoxScore(code):
    game_code = int(code)
    
    game_data = gameInfo(code)

    awayPlayerStats , homePlayerStats = gamePlayerStats(game_data["away_team_id"], game_code)
    
    awayTeamStats , homeTeamStats = gameTeamStats(game_data["away_team_id"],  game_code)

    #Team Defense Stats
    awayTeamDefense= gameTeamDefense(game_data["away_team_id"],game_code)
    homeTeamDefense = gameTeamDefense(game_data["home_team_id"],game_code)

    #print(game_data["away_team_id"], awayPlayerStats)


    return render_template('BoxScore.html', game_data = game_data , awayPlayerStats = awayPlayerStats, homePlayerStats = homePlayerStats, 
                           awayTeamStats = awayTeamStats, homeTeamStats = homeTeamStats, 
                           awayTeamDefense = awayTeamDefense, homeTeamDefense = homeTeamDefense  )

#Route to go to Conference Page
#code -> conference_id
@app.route('/conferences/<code>/<season_year>')
def conferencePage(code,season_year):
    conference_id = int(code)
    season_id = int(season_year)

    team_stats = getConferenceAvg(conference_id,season_id)
    opp_stats = getConferenceOppAvg(conference_id,season_id)



    return render_template('Conference.html', conference_id = conference_id, season_id = season_id, conf_stats = team_stats, conf_opp_stats = opp_stats)
    
    

#Route to go to Player Page
@app.route('/players/<code>')
def playerStats(code):
    pass

if __name__ == '__main__':
    app.run(port=7000, debug=True)
