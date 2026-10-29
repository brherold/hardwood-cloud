# Hardwood Cloud (Option B Architecture)

This version of the project decouples the **24/7 web application** from the **local scraping engine**:
1. **Frontend (`webapp.py`)**: Hosted in the cloud on **Render** (free tier), accessible anywhere, 24/7.
2. **Database (`basketball.db`)**: Hosted on **Turso Cloud** (free tier: 9 GB storage, easily holds the 1.2 GB database).
3. **Automated Scraper (`dataAdder.py`)**: Runs locally on your PC via **Windows Task Scheduler** using your residential IP (preventing Cloudflare blocks), and pushes updates to Turso.

---

## Architecture Flow

```
[ Public Users Anywhere (24/7) ]
               │
               ▼ (HTTPS)
┌───────────────────────────────────────┐
│     Render Free Web Service           │
│   (Gunicorn / Flask / webapp.py)      │
└──────────────────┬────────────────────┘
                   │
                   ▼ (libSQL over HTTP)
┌───────────────────────────────────────┐
│          Turso Cloud Database         │
│     (1.2 GB basketball.db in Cloud)   │
└──────────────────▲────────────────────┘
                   │ (Pushes daily/weekly updates)
┌──────────────────┴────────────────────┐
│      Your Local PC (Scheduled)        │
│  - Daily: add_games for all teams     │
│  - Thu/Fri: update_roster for teams   │
│  - Residential IP bypasses Cloudflare │
└───────────────────────────────────────┘
```

---

## Step 1: Set Up Free Cloud Database (Turso)

1. **Install Turso CLI**:
   Open PowerShell and run:
   ```powershell
   irm https://get.turso.tech | iex
   ```
2. **Sign up / Log in** (Free tier gives 9 GB storage and 500 databases):
   ```bash
   turso auth signup
   # or
   turso auth login
   ```
3. **Import your 1.2 GB database to Turso Cloud**:
   Navigate to this project folder and run:
   ```bash
   turso db import instance/basketball.db
   ```
   *(Turso will create a database named `basketball` and seed all tables and records).*

4. **Get your Turso Database URL and Auth Token**:
   ```bash
   turso db show basketball --url
   # Example output: libsql://basketball-yourusername.turso.io

   turso db tokens create basketball
   # Outputs your long auth token string
   ```

5. **Save credentials locally**:
   Create a `.env` file in this folder (copy from `.env.example`):
   ```env
   TURSO_DATABASE_URL=libsql://basketball-yourusername.turso.io
   TURSO_AUTH_TOKEN=your_token_here
   ```

---

## Step 2: Deploy the Web App on Render (Free 24/7)

1. **Push this project (`Hardwood-Cloud`) to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Hardwood Cloud setup"
   git remote add origin https://github.com/<your-username>/hardwood-cloud.git
   git push -u origin main
   ```
   *(Note: The `.gitignore` automatically excludes the 1.2 GB local `.db` file, keeping the Git repository small and fast for Render).*

2. **Create Web Service on Render**:
   - Go to [dashboard.render.com](https://dashboard.render.com) and click **New + > Web Service**.
   - Connect your GitHub repository.
   - Settings:
     - **Name**: `hardwood-stats`
     - **Runtime**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120`
     - **Instance Type**: `Free`
   - Under **Environment Variables**, add:
     - `TURSO_DATABASE_URL` = (your Turso database URL)
     - `TURSO_AUTH_TOKEN` = (your Turso token)

3. **Prevent Free Tier Sleeping (Optional but Recommended)**:
   - Render's free tier spins down after 15 minutes of inactivity.
   - Set up a free monitor at [UptimeRobot.com](https://uptimerobot.com) to ping your Render URL (`https://hardwood-stats.onrender.com/`) every 10 minutes. This keeps the web service warm and always online.

---

## Step 3: Automate Daily Scrapes on Windows Task Scheduler

This project includes two ready-to-run batch files:
- `run_daily_games.bat`: Runs `python run_scraper.py --action games` and syncs to Turso.
- `run_weekly_rosters.bat`: Runs `python run_scraper.py --action rosters` and syncs to Turso.

### Setup in Windows Task Scheduler:

1. Press `Win + R`, type `taskschd.msc`, and press **Enter**.
2. Click **Create Basic Task...** on the right panel.

#### Task A: Daily Games Update
- **Name**: `Hardwood - Daily Games Scrape`
- **Trigger**: **Daily** at your preferred time (e.g. 3:00 AM).
- **Action**: **Start a program**.
- **Program/script**: Click Browse and select `D:\Hardwood\Hardwood-Cloud\run_daily_games.bat`.
- **Start in (optional)**: `D:\Hardwood\Hardwood-Cloud`.

#### Task B: Thursday & Friday Roster Update
- **Name**: `Hardwood - Thu Fri Rosters Update`
- **Trigger**: **Weekly** -> check **Thursday** and **Friday** at your preferred time (e.g. 11:30 PM).
- **Action**: **Start a program**.
- **Program/script**: Click Browse and select `D:\Hardwood\Hardwood-Cloud\run_weekly_rosters.bat`.
- **Start in (optional)**: `D:\Hardwood\Hardwood-Cloud`.

Logs are automatically written to `scraper.log` in this directory so you can review runs anytime.

---

## Manual Execution & Testing

- **Run web app locally**:
  ```bash
  python wsgi.py
  ```
  *(Works with or without Turso credentials. Without credentials, it falls back to local `instance/basketball.db`).*

- **Test scraping games for a single team**:
  ```bash
  python run_scraper.py --action games --team 1 --num-games 10
  ```

- **Test updating rosters for a single team**:
  ```bash
  python run_scraper.py --action rosters --team 1
  ```

- **Check sync status between Local and Turso**:
  ```bash
  python turso_sync.py --status
  ```
