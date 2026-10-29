import os
import sys
import sqlite3
import time
import logging
from dotenv import load_dotenv

# Setup logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("turso_historical_sync")

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

DB_PATH = os.path.join(PROJECT_ROOT, "instance", "basketball.db")

def get_turso_client():
    url = os.environ.get("TURSO_DATABASE_URL")
    token = os.environ.get("TURSO_AUTH_TOKEN")
    if not url:
        raise ValueError("TURSO_DATABASE_URL not set in .env")
    if url.startswith("libsql://"):
        url = "https://" + url[len("libsql://"):]
    import libsql_client
    return libsql_client.create_client_sync(url=url, auth_token=token)

def sync_table_batch(client, local_cur, table_name, query, params=(), batch_size=500):
    import libsql_client
    local_cur.execute(query, params)
    rows = local_cur.fetchall()
    if not rows:
        return 0

    col_names = [c[0] for c in local_cur.description]
    cols_str = ",".join(f'"{c}"' for c in col_names)
    p_str = ",".join("?" for _ in col_names)
    sql = f'INSERT OR REPLACE INTO "{table_name}" ({cols_str}) VALUES ({p_str})'
    
    statements = [libsql_client.Statement(sql, list(r)) for r in rows]
    total = len(statements)
    for b in range(0, total, batch_size):
        chunk = statements[b:b + batch_size]
        client.batch(chunk)
    return total

def sync_season(client, local_conn, season_id):
    local_cur = local_conn.cursor()
    logger.info(f"========== Syncing Season {season_id} ==========")

    # 1. players_skills
    n = sync_table_batch(client, local_cur, "players_skills",
                         "SELECT * FROM players_skills WHERE season_id = ?", (season_id,))
    logger.info(f"Season {season_id}: Synced {n} players_skills.")

    # 2. team_avg
    n = sync_table_batch(client, local_cur, "team_avg",
                         "SELECT * FROM team_avg WHERE season_id = ?", (season_id,))
    logger.info(f"Season {season_id}: Synced {n} team_avg.")

    # 3. player_avg
    n = sync_table_batch(client, local_cur, "player_avg",
                         "SELECT * FROM player_avg WHERE season_id = ?", (season_id,))
    logger.info(f"Season {season_id}: Synced {n} player_avg.")

    # 4. Games & stats
    local_cur.execute("SELECT game_id FROM games WHERE season_id = ?", (season_id,))
    all_game_ids = [r[0] for r in local_cur.fetchall()]
    
    # Check existing games in Turso
    res = client.execute("SELECT game_id FROM games WHERE season_id = ?", [season_id])
    existing_turso = set(r[0] for r in res.rows)
    to_sync = [gid for gid in all_game_ids if gid not in existing_turso]
    logger.info(f"Season {season_id}: Total games={len(all_game_ids)}, Unsynced={len(to_sync)}.")

    chunk_size = 50
    tables = ["games", "team_stats", "player_stats", "offense_stats", "defense_stats"]
    total_synced = 0
    t0 = time.time()
    
    for i in range(0, len(to_sync), chunk_size):
        chunk_gids = to_sync[i:i + chunk_size]
        placeholders = ",".join("?" for _ in chunk_gids)

        for tbl in tables:
            sync_table_batch(client, local_cur, tbl,
                             f'SELECT * FROM "{tbl}" WHERE game_id IN ({placeholders})', chunk_gids)

        total_synced += len(chunk_gids)
        if total_synced % 200 == 0 or total_synced == len(to_sync):
            elapsed = time.time() - t0
            rate = total_synced / elapsed if elapsed > 0 else 0
            logger.info(f"Season {season_id}: {total_synced}/{len(to_sync)} games synced ({rate:.1f} games/s)...")

    logger.info(f"✅ Season {season_id} fully synchronized!")

def main():
    client = get_turso_client()
    local_conn = sqlite3.connect(DB_PATH)
    local_conn.row_factory = sqlite3.Row

    # Sync seasons 2054 down to 2050
    seasons = [2054, 2053, 2052, 2051, 2050]
    total_start = time.time()
    
    for s in seasons:
        sync_season(client, local_conn, s)

    local_conn.close()
    client.close()
    total_time = (time.time() - total_start) / 60
    logger.info(f"🎉 All historical seasons (2050-2054) synchronized in {total_time:.1f} minutes!")

if __name__ == "__main__":
    main()
