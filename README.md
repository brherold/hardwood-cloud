# 🏀 Hardwood Basketball Analytics Platform

[![Live Application](https://img.shields.io/badge/Live_Demo-hardwood--cloud.onrender.com-0055aa?style=for-the-badge&logo=render&logoColor=white)](https://hardwood-cloud.onrender.com/)
[![Database](https://img.shields.io/badge/Turso_libSQL-7.6M+_Rows-00E599?style=for-the-badge&logo=sqlite&logoColor=black)](https://turso.tech/)
[![Python](https://img.shields.io/badge/Python_3.11+-Flask_Web_Framework-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)

An end-to-end basketball analytics and scouting platform tracking **1,008 teams**, **125,000+ games**, and over **7.6 million statistical records** from the [Hardwood College Basketball](https://onlinecollegebasketball.org/) simulation universe. Built with a decoupled cloud-edge architecture, the platform features advanced metrics (VORP, BPM, EPM, Dean Oliver's Four Factors), instant client-side autocomplete search across all 1,008 teams, and an automated data ingestion pipeline.

👉 **Live Demo:** [https://hardwood-cloud.onrender.com/](https://hardwood-cloud.onrender.com/)

---

## 🏛️ System Architecture

The platform decouples the **24/7 web application** from the **data extraction pipeline**, ensuring continuous availability:

```
                          [ Public Visitors Worldwide ]
                                        │
                                        ▼ HTTPS (TLS 1.3)
                  ┌───────────────────────────────────────────┐
                  │          Render Web Service (24/7)        │
                  │    • Flask / Gunicorn WSGI (2w / 4th)     │
                  │    • In-Memory Template & Query Cache     │
                  │    • Persistent HTTP Connection Pooling   │
                  └─────────────────────┬─────────────────────┘
                                        │
                                        ▼ libSQL over HTTP (Sub-150ms)
                  ┌───────────────────────────────────────────┐
                  │         Turso Cloud Edge Database         │
                  │    • 125,000+ Games | 7.6M+ Records       │
                  │    • 9 Composite B-Tree Indexes           │
                  │    • WAL Journal Mode Storage             │
                  └─────────────────────▲─────────────────────┘
                                        │
                                        │ Batch Upserts (libsql-client)
                                        │
                  ┌─────────────────────┴─────────────────────┐
                  │      Automated Ingestion Pipeline (PC)    │
                  │    • Windows Task Scheduler (Daily ETL)   │
                  │    • Headless Browser Boxscore Parsing    │
                  │    • Idempotent Game Processing           │
                  │    • Self-Healing Resilient Catch-Up      │
                  └───────────────────────────────────────────┘
```

---

## 🚀 Engineering Highlights & Technical Challenges

### 1. 33x Query Optimization on Multi-Million Row Tables
* **The Challenge:** Initial queries across 2.26M rows (`offense_stats`), 2.26M rows (`defense_stats`), and 2.35M rows (`player_stats`) resulted in full table scans, taking ~24 seconds to assemble an individual team dashboard.
* **The Solution:** Engineered 9 composite B-tree indexes covering multi-column lookup patterns (`team_id`, `game_id`, `season_id`, `game_type`, `stat_type`), built in-memory SQL query caching, and implemented client-side connection pooling.
* **Result:** Reduced full page assembly from **23.9 seconds down to 0.7 seconds** (**~33x speedup**), with individual analytical queries executing in **under 170ms**.

### 2. Resilient Scheduled ETL & Data Pipeline
* **The Challenge:** Continuously ingesting daily boxscores and roster updates across 1,008 teams and 63 conferences without creating duplicates, losing historical state, or stalling on network drops.
* **The Solution:** Designed a scheduled, idempotent ingestion pipeline that parses box score tables, extracts play-by-play events and shot distance coordinates, and dynamically computes the target game count (`previous_day_gp + 1 + 3_exhibitions`).
* **Fault Tolerance & Catch-Up:** The pipeline tracks processed games and automatically identifies missing matches. If the host machine is asleep or offline, Task Scheduler detects missed runs and triggers a self-healing catch-up run upon boot.

### 3. Serverless Edge Database (libSQL)
* **Zero Cold-Starts:** Powered by Turso (distributed libSQL), avoiding heavy relational database maintenance costs while providing serverless scale across 125k historical games.
* **Transactional Sync Engine:** Includes `turso_sync.py`, a batch synchronization engine pushing 500-statement batches using HTTP pipelines with automated foreign-key validation.

---

## 📊 Analytics & Advanced Metrics

| Metric | Category | Description |
| :--- | :--- | :--- |
| **BPM / EPM** | Player Impact | Box Plus/Minus and Estimated Plus/Minus measuring per-possession player quality relative to league average. |
| **VORP** | Value Above Replacement | Value Over Replacement Player normalized to 40-minute college team games: `[ (EPM + 3) * Min * GP ] / (Team_GP * 40)`. |
| **Four Factors** | Team Efficiency | Dean Oliver's foundational Four Factors of Basketball Success: Effective FG% (`eFG%`), Turnover Rate (`TOV%`), Offensive/Defensive Rebound Rate (`ORB%` / `DRB%`), and Free Throw Factor (`FT/FGA`). |
| **Shooting Distributions** | Shot Quality | Granular breakdown of field goal attempts by distance: Rim (`0-6 ft`), Mid-Range (`7-20 ft`), and 3-Point (`21+ ft`), with separate tracking for Driving Success (`DRV` / `DRVA` / `DRV%`). |
| **Historical Depth Chart** | Team Structure | Automatically computes a 3-tier positional depth chart (`Starter`, `Backup`, `Reserve`) across `PG`, `SG`, `SF`, `PF`, and `C` based on positional minutes, starts (`GS`), and games played (`GP`). |

---

## 💻 Tech Stack

- **Backend:** Python 3.11+, Flask, Gunicorn, SQLAlchemy, Requests, Beautiful Soup 4
- **Database & Storage:** Turso (libSQL/SQLite at the edge), SQLite3 WAL Mode
- **Automation & Ingestion:** Selenium WebDriver, Windows Task Scheduler
- **Frontend:** Responsive HTML5, CSS3, Jinja2 Templates, Vanilla JavaScript (0 external UI dependencies)
- **Deployment & Hosting:** Render (Web Service), GitHub Actions

---

## 🛠️ Local Development & Preview

The repository includes a dedicated local development server with live auto-reloading:

### 1. Clone & Install
```bash
git clone https://github.com/brherold/hardwood-cloud.git
cd hardwood-cloud
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file in the project root (see `.env.example`):
```env
TURSO_DATABASE_URL=https://your-database-name.turso.io
TURSO_AUTH_TOKEN=your_auth_token_here
```
*(Note: If credentials are not supplied, the application automatically falls back to the local `instance/basketball.db` SQLite database).*

### 3. Run Development Server
```bash
# Windows: Double-click run_dev.bat or execute:
python run_dev.py
```
* The development server starts at `http://127.0.0.1:5000/` and automatically opens in your browser.
* Any edits to HTML templates or Python routes will live-reload instantly.

---

## 🗄️ Database Schema Overview

```
teams (team_id, team_name)
seasons (season_id, year)
conferences (conference_id, conference_name, division_id)
games (game_id, game_type, season_id, game_date, home_team_id, away_team_id)
players (player_id, team_id, name)
players_skills (player_id, season_id, Pos, Class, Ht, Wt, Wingspan, Vertical, IS, OS, Rng, Fin, Reb, IDef, PDef, IQ, Pass, Hnd, Drv, Str, Spd, Sta, SI, POT, Stars)
team_avg (team_id, season_id, game_type, stat_type, conference_id, GW, GP, Min, PTS, eFG%, Poss, ORtg, DRtg, NetRtg, Four_Factors...)
player_avg (player_id, season_id, game_type, GP, GS, Min, Pos_Min[PG,SG,SF,PF,C], PTS, Shooting_Splits, BPM, EPM, VORP...)
team_stats (game_id, team_id, PTS, Possession_Metrics, Shot_Splits...)
player_stats (player_id, game_id, Pos, GS, Min, Stats, Advanced_Ratings...)
offense_stats (team_id, game_id, defense_type, plays, shot_splits...)
defense_stats (team_id, game_id, defense_type, plays, allowed_splits...)
```

---

## 👤 Author
**Brandon Herold**  
- GitHub: [@brherold](https://github.com/brherold)
- Live App: [https://hardwood-cloud.onrender.com/](https://hardwood-cloud.onrender.com/)
