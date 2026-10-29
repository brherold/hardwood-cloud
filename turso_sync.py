import os
import sys
import sqlite3
import logging
from typing import List, Set, Optional

# Load .env automatically if present
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except Exception:
    pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("turso_sync")

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
INSTANCE_DIR = os.path.join(PROJECT_ROOT, "instance")
DB_PATH = os.path.join(INSTANCE_DIR, "basketball.db")

def get_turso_client():
    """Returns a connected libsql_client.ClientSync if env vars are configured."""
    url = os.environ.get("TURSO_DATABASE_URL")
    token = os.environ.get("TURSO_AUTH_TOKEN")
    if not url:
        return None
    if url.startswith("libsql://"):
        url = "https://" + url[len("libsql://"):]
    try:
        import libsql_client
        return libsql_client.create_client_sync(url=url, auth_token=token)
    except Exception as e:
        logger.error(f"Failed to create Turso client: {e}")
        return None

def get_local_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_schema(client):
    """Creates all tables and indexes from local SQLite in Turso Cloud."""
    local_conn = get_local_connection()
    local_cur = local_conn.cursor()
    local_cur.execute("SELECT type, name, sql FROM sqlite_master WHERE type IN ('table', 'index') AND name NOT LIKE 'sqlite_%'")
    items = local_cur.fetchall()

    logger.info(f"Initializing schema ({len(items)} tables/indexes) in Turso...")
    for obj_type, name, sql in items:
        if not sql:
            continue
        try:
            logger.info(f"Creating {obj_type} '{name}'...")
            client.execute(sql)
        except Exception as e:
            logger.warning(f"Note on {obj_type} '{name}': {e}")
    local_conn.close()
    logger.info("✅ Schema initialization complete!")

def sync_games(client, season_id: int, game_ids: Optional[List[int]] = None, batch_size: int = 100):
    """
    Syncs games and related game stats from local SQLite to Turso.
    If game_ids is None, finds all games in local DB for season_id not yet in Turso.
    """
    import libsql_client

    local_conn = get_local_connection()
    local_cur = local_conn.cursor()

    if game_ids is None:
        logger.info(f"Checking for unsynced games in season {season_id}...")
        # Get Turso game IDs for this season
        try:
            res = client.execute("SELECT game_id FROM games WHERE season_id = ?", [season_id])
            turso_game_ids = set(r[0] for r in res.rows)
        except Exception as e:
            logger.error(f"Error querying Turso games: {e}")
            turso_game_ids = set()

        local_cur.execute("SELECT game_id FROM games WHERE season_id = ?", (season_id,))
        local_game_ids = [r[0] for r in local_cur.fetchall()]
        to_sync = [gid for gid in local_game_ids if gid not in turso_game_ids]
    else:
        to_sync = list(game_ids)

    if not to_sync:
        logger.info("✅ All games are already synchronized with Turso.")
        local_conn.close()
        return 0

    logger.info(f"Syncing {len(to_sync)} games to Turso...")
    tables_to_sync = ["games", "team_stats", "player_stats", "offense_stats", "defense_stats"]

    total_synced = 0
    # Process in chunks of games
    chunk_size = 50
    batch_size = 500
    for i in range(0, len(to_sync), chunk_size):
        chunk_gids = to_sync[i:i + chunk_size]
        placeholders = ",".join("?" for _ in chunk_gids)

        for table in tables_to_sync:
            local_cur.execute(f"SELECT * FROM \"{table}\" WHERE game_id IN ({placeholders})", chunk_gids)
            rows = local_cur.fetchall()
            if not rows:
                continue

            col_names = [col[0] for col in local_cur.description]
            cols_str = ",".join(f'"{c}"' for c in col_names)
            val_placeholders = ",".join("?" for _ in col_names)
            sql = f'INSERT OR REPLACE INTO "{table}" ({cols_str}) VALUES ({val_placeholders})'
            statements = [libsql_client.Statement(sql, list(r)) for r in rows]

            for b in range(0, len(statements), batch_size):
                client.batch(statements[b:b + batch_size])

        total_synced += len(chunk_gids)
        logger.info(f"Synced {total_synced}/{len(to_sync)} games...")

    local_conn.close()
    return total_synced

def sync_averages(client, season_id: int, batch_size: int = 200):
    """Syncs team_avg and player_avg for the given season to Turso."""
    import libsql_client
    local_conn = get_local_connection()
    local_cur = local_conn.cursor()

    logger.info(f"Syncing team_avg and player_avg for season {season_id}...")
    for table in ["team_avg", "player_avg"]:
        local_cur.execute(f"SELECT * FROM \"{table}\" WHERE season_id = ?", (season_id,))
        rows = local_cur.fetchall()
        if not rows:
            continue
        col_names = [c[0] for c in local_cur.description]
        cols_str = ",".join(f'"{c}"' for c in col_names)
        val_placeholders = ",".join("?" for _ in col_names)
        sql = f'INSERT OR REPLACE INTO "{table}" ({cols_str}) VALUES ({val_placeholders})'

        stmts = [libsql_client.Statement(sql, list(r)) for r in rows]
        for b in range(0, len(stmts), batch_size):
            client.batch(stmts[b:b + batch_size])
        logger.info(f"Synced {len(rows)} rows for {table}.")

    local_conn.close()

def sync_rosters(client, season_id: int, batch_size: int = 200):
    """Syncs players and players_skills for season to Turso."""
    import libsql_client
    local_conn = get_local_connection()
    local_cur = local_conn.cursor()

    logger.info(f"Syncing players and players_skills for season {season_id}...")
    # 1. Sync all players FIRST (so foreign keys are satisfied)
    local_cur.execute(
        "SELECT DISTINCT p.* FROM players p JOIN players_skills ps ON p.player_id = ps.player_id WHERE ps.season_id = ?",
        (season_id,)
    )
    players_rows = local_cur.fetchall()
    if players_rows:
        col_names = [c[0] for c in local_cur.description]
        cols_str = ",".join(f'"{c}"' for c in col_names)
        val_placeholders = ",".join("?" for _ in col_names)
        sql = f'INSERT OR REPLACE INTO players ({cols_str}) VALUES ({val_placeholders})'
        stmts = [libsql_client.Statement(sql, list(r)) for r in players_rows]
        for b in range(0, len(stmts), 500):
            client.batch(stmts[b:b + 500])
        logger.info(f"Synced {len(players_rows)} rows for players.")

    # 2. Sync players_skills SECOND
    local_cur.execute("SELECT * FROM players_skills WHERE season_id = ?", (season_id,))
    skills_rows = local_cur.fetchall()
    if skills_rows:
        col_names = [c[0] for c in local_cur.description]
        cols_str = ",".join(f'"{c}"' for c in col_names)
        val_placeholders = ",".join("?" for _ in col_names)
        sql = f'INSERT OR REPLACE INTO players_skills ({cols_str}) VALUES ({val_placeholders})'
        stmts = [libsql_client.Statement(sql, list(r)) for r in skills_rows]
        for b in range(0, len(stmts), 500):
            client.batch(stmts[b:b + 500])
        logger.info(f"Synced {len(skills_rows)} rows for players_skills.")

    local_conn.close()

def print_status(season_id: int):
    client = get_turso_client()
    if not client:
        print("❌ TURSO_DATABASE_URL is not set.")
        return

    local_conn = get_local_connection()
    local_cur = local_conn.cursor()

    print(f"\n--- Database Sync Status (Season {season_id}) ---")
    local_cur.execute("SELECT COUNT(*) FROM games WHERE season_id = ?", (season_id,))
    local_games = local_cur.fetchone()[0]

    try:
        turso_res = client.execute("SELECT COUNT(*) FROM games WHERE season_id = ?", [season_id])
        turso_games = turso_res.rows[0][0]
    except Exception as e:
        turso_games = f"Error: {e}"

    print(f"Games (Season {season_id}): Local={local_games} | Turso={turso_games}")

    local_cur.execute("SELECT COUNT(*) FROM players_skills WHERE season_id = ?", (season_id,))
    local_skills = local_cur.fetchone()[0]
    try:
        turso_res = client.execute("SELECT COUNT(*) FROM players_skills WHERE season_id = ?", [season_id])
        turso_skills = turso_res.rows[0][0]
    except Exception as e:
        turso_skills = f"Error: {e}"

    print(f"Player Skills (Season {season_id}): Local={local_skills} | Turso={turso_skills}")
    local_conn.close()
    client.close()

def run_sync(season_id: int = 2055, sync_type: str = "all", game_ids: Optional[List[int]] = None):
    client = get_turso_client()
    if not client:
        logger.info("Turso credentials not set. Skipping cloud sync (saved locally).")
        return False

    try:
        if sync_type in ("games", "all"):
            sync_games(client, season_id, game_ids=game_ids)
            sync_averages(client, season_id)
        if sync_type in ("rosters", "all"):
            sync_rosters(client, season_id)
        logger.info("🎉 Sync to Turso completed successfully!")
        return True
    finally:
        client.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Turso Database Synchronization Tool")
    parser.add_argument("--season", type=int, default=2055, help="Season ID (default: 2055)")
    parser.add_argument("--sync", choices=["games", "rosters", "all"], default="all")
    parser.add_argument("--status", action="store_true", help="Check sync status between Local and Turso")
    parser.add_argument("--init-schema", action="store_true", help="Initialize all database tables in Turso Cloud")
    args = parser.parse_args()

    if args.init_schema:
        client = get_turso_client()
        if client:
            init_schema(client)
            client.close()
        else:
            print("❌ Cannot connect to Turso. Check TURSO_DATABASE_URL and TURSO_AUTH_TOKEN in .env.")
    elif args.status:
        print_status(args.season)
    else:
        run_sync(season_id=args.season, sync_type=args.sync)
