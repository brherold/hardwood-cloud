import os
import sys
import threading
import time
import urllib.request
from flask import Flask, render_template, request, redirect, url_for, jsonify

FRONTEND_DIR = os.path.dirname(os.path.abspath(__file__))
if FRONTEND_DIR not in sys.path:
    sys.path.insert(0, FRONTEND_DIR)

from getData import *

#Keep Note (Website shown EPM is db BPM)

app = Flask(__name__, template_folder=os.path.join(FRONTEND_DIR, 'templates'))

def start_keep_alive():
    """Background keep-alive thread that pings the app's public URL every 10 minutes on Render."""
    if not (os.environ.get("RENDER") or os.environ.get("RENDER_EXTERNAL_URL") or os.environ.get("PING_URL")):
        return

    url = os.environ.get("RENDER_EXTERNAL_URL") or os.environ.get("PING_URL") or "https://hardwood-cloud.onrender.com"
    if not url.startswith("http"):
        url = "https://" + url
    ping_target = url.rstrip("/") + "/health"

    def ping_worker():
        time.sleep(120)  # Wait 2 minutes after startup before first ping
        while True:
            try:
                req = urllib.request.Request(ping_target, headers={"User-Agent": "HardwoodKeepAlive/1.0"})
                with urllib.request.urlopen(req, timeout=15):
                    pass
            except Exception:
                pass
            time.sleep(600)  # 10 minutes

    t = threading.Thread(target=ping_worker, daemon=True)
    t.start()

start_keep_alive()

ALL_CONFERENCES = [{"id": cid, "name": get_conference_name(cid)} for cid in range(1, 64)]
app.jinja_env.globals['ALL_CONFERENCES'] = ALL_CONFERENCES
app.jinja_env.globals['get_conference_name'] = get_conference_name
@app.route("/health")
def health():
    db_url = os.environ.get("TURSO_DATABASE_URL")
    auth_token = os.environ.get("TURSO_AUTH_TOKEN")
    info = {
        "TURSO_DATABASE_URL_set": bool(db_url),
        "TURSO_DATABASE_URL_masked": (db_url[:25] + "...") if db_url else None,
        "TURSO_AUTH_TOKEN_set": bool(auth_token),
        "error": None,
        "teams_count": None
    }
    try:
        conn, cur = get_connection()
        cur.execute("SELECT COUNT(*) FROM teams")
        row = cur.fetchone()
        info["teams_count"] = row[0] if row else None
        conn.close()
        info["status"] = "ok"
    except Exception as e:
        info["status"] = "error"
        info["error"] = str(e)
    return jsonify(info)
TEAMS_CACHE = None

def get_all_teams():
    global TEAMS_CACHE
    if TEAMS_CACHE is not None:
        return TEAMS_CACHE
    try:
        conn, cur = get_connection()
        cur.execute("SELECT team_id, team_name FROM teams ORDER BY team_name ASC")
        rows = cur.fetchall()
        TEAMS_CACHE = [{"id": int(r["team_id"]), "name": str(r["team_name"])} for r in rows]
        conn.close()
    except Exception as e:
        print(f"Error fetching teams: {e}")
        TEAMS_CACHE = []
    return TEAMS_CACHE

@app.route("/api/teams")
def api_teams():
    return jsonify(get_all_teams())

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        raw_code = request.form.get("code", "").strip()

        if not raw_code:
            return redirect(url_for('home'))

        # Numeric input
        if raw_code.isdigit():
            val = int(raw_code)
            if len(raw_code) > 4:
                return redirect(url_for('gameBoxScore', code=val))
            else:
                return redirect(url_for('teamStats', code=val, season_year=2055))

        # Team name search fallback
        teams = get_all_teams()
        lower_q = raw_code.lower()
        match = next((t for t in teams if t["name"].lower() == lower_q), None)
        if not match:
            match = next((t for t in teams if t["name"].lower().startswith(lower_q)), None)
        if not match:
            match = next((t for t in teams if lower_q in t["name"].lower()), None)

        if match:
            return redirect(url_for('teamStats', code=match["id"], season_year=2055))

        return render_template('home.html', error=f"Team '{raw_code}' not found.")

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

    # Map player GP and Primary Position from team_player_avg
    player_gp_map = {p["player_id"]: p.get("GP", 0) for p in team_player_avg}
    player_pos_map = {p["player_id"]: p.get("Primary_Position", "-") for p in team_player_avg}
    team_gp = team_avg.get("GP", 0) or 0
    gp_threshold = team_gp * 0.5

    for player in roster:
        pid = player.get("player_id")
        p_gp = player_gp_map.get(pid, 0)
        player["GP"] = p_gp
        player["Primary_Position"] = player_pos_map.get(pid, "-")
        player["highlight"] = (p_gp >= gp_threshold and team_gp > 0)
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

    conf_name = get_conference_name(conference_id)
    team_stats = getConferenceAvg(conference_id,season_id)
    opp_stats = getConferenceOppAvg(conference_id,season_id)

    return render_template('Conference.html', conference_id = conference_id, conf_name = conf_name, season_id = season_id, conf_stats = team_stats, conf_opp_stats = opp_stats)
    

#Route to go to Player Page
@app.route('/players/<code>')
def playerStats(code):
    pass

if __name__ == '__main__':
    app.run(port=7000, debug=True)
