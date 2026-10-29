"""
Attempt Rates vs. Offensive Rating (ORtg) Graph Generator for Hardwood Analytics.

Generates a 4-panel high-resolution PNG chart (RimAr, MidAr, 3PAr, FTr vs. ORtg)
with customizable season, game_type, and conference_id filters.

Usage:
  python plot_attempt_rates.py --season 2054 --game_type College --max_conf 100
  python plot_attempt_rates.py -s 2054 -g Conference -c 63 -o my_graph.png
"""

import os
import sys
import sqlite3
import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Default database path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "instance", "basketball.db")


def pearson_r(x, y):
    """Calculates Pearson correlation coefficient between two lists."""
    n = len(x)
    if n < 3:
        return 0.0
    mx = sum(x) / n
    my = sum(y) / n
    cov = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    var_x = sum((xi - mx) ** 2 for xi, yi in zip(x, y))
    var_y = sum((yi - mean_y) ** 2 for yi in y) if 'mean_y' in locals() else sum((yi - my) ** 2 for yi in y)
    if var_x == 0 or var_y == 0:
        return 0.0
    return cov / ((var_x * var_y) ** 0.5)


def get_trendline(x, y):
    """Calculates linear regression trendline coordinates."""
    n = len(x)
    mx = sum(x) / n
    my = sum(y) / n
    var_x = sum((xi - mx) ** 2 for xi in x)
    if var_x == 0:
        return [min(x), max(x)], [my, my]
    slope = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / var_x
    intercept = my - slope * mx
    min_x, max_x = min(x), max(x)
    return [min_x, max_x], [slope * min_x + intercept, slope * max_x + intercept]


def generate_attempt_rates_graph(
    season=2054,
    game_type="College",
    max_conf=100,
    min_gp=3,
    db_path=DB_PATH,
    output_file="attempt_rates_vs_ortg.png"
):
    """
    Queries database, computes correlations, and generates 4-panel attempt rates vs ORtg PNG.

    Args:
        season (int or str): Season year (e.g. 2054) or 'all'.
        game_type (str): Game type (e.g. 'College', 'Conference', 'Tournament').
        max_conf (int): Maximum conference_id threshold (conference_id <= max_conf).
        min_gp (int): Minimum games played threshold (GP >= min_gp).
        db_path (str): Path to SQLite database.
        output_file (str): Path to output PNG.
    """
    if not os.path.exists(db_path):
        print(f"[ERROR] Database file not found at: {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    where_clauses = [
        "stat_type = 'team'",
        "ORtg IS NOT NULL",
        "FG_A > 0",
        f"conference_id <= {int(max_conf)}",
        f"GP >= {int(min_gp)}"
    ]

    if str(season).lower() != "all" and int(season) > 0:
        where_clauses.append(f"season_id = {int(season)}")

    if game_type and game_type.lower() != "all":
        where_clauses.append(f"game_type = '{game_type}'")

    where_sql = " AND ".join(where_clauses)

    query = f"""
    SELECT 
        team_id, 
        season_id, 
        FTr, 
        round((Rim_A / FG_A), 3) AS RimAr, 
        round((Mid_A / FG_A), 3) AS MidAr, 
        _3PAr, 
        ORtg
    FROM team_avg
    WHERE {where_sql}
    ORDER BY MidAr ASC;
    """

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    n_teams = len(rows)
    if n_teams < 3:
        print(f"[WARN] Not enough data found for filters (Season={season}, GameType={game_type}, MaxConf={max_conf}). Rows found: {n_teams}")
        return False

    ftr = [r[2] for r in rows if r[2] is not None and r[6] is not None]
    rim_ar = [r[3] for r in rows if r[3] is not None and r[6] is not None]
    mid_ar = [r[4] for r in rows if r[4] is not None and r[6] is not None]
    three_ar = [r[5] for r in rows if r[5] is not None and r[6] is not None]
    ortg = [r[6] for r in rows if r[6] is not None]

    # Calculate Pearson correlations
    r_rim = pearson_r(rim_ar, ortg)
    r_mid = pearson_r(mid_ar, ortg)
    r_3p = pearson_r(three_ar, ortg)
    r_ft = pearson_r(ftr, ortg)

    # Plotting
    plt.style.use('dark_background')
    fig, axs = plt.subplots(2, 2, figsize=(14, 10), dpi=300)
    season_label = f"Season {season}" if str(season).lower() != "all" else "All Seasons"
    fig.suptitle(f"Hardwood Analytics: Shot Attempt Rates vs. Offensive Rating\n({season_label}, {game_type}, Conf <= {max_conf}, N={n_teams})", fontsize=15, fontweight='bold', y=0.98, color='#ffffff')

    # 1. Rim Attempt Rate (RimAr)
    x_t, y_t = get_trendline(rim_ar, ortg)
    axs[0, 0].scatter([x * 100 for x in rim_ar], ortg, color='#33cc33', alpha=0.45, s=22)
    axs[0, 0].plot([x * 100 for x in x_t], y_t, color='#00ff00', linewidth=2.5, label=f'Trendline (r = {r_rim:+.3f})')
    axs[0, 0].set_title('Rim Attempt Rate (RimAr) vs. ORtg', fontsize=12, fontweight='bold', color='#66ff66')
    axs[0, 0].set_xlabel('Rim Attempt Rate (% of FGA 0-6 ft)', fontsize=10)
    axs[0, 0].set_ylabel('Offensive Rating (ORtg)', fontsize=10)
    axs[0, 0].grid(True, linestyle='--', alpha=0.25)
    axs[0, 0].legend(loc='lower right')

    # 2. Mid-Range Attempt Rate (MidAr)
    x_t, y_t = get_trendline(mid_ar, ortg)
    axs[0, 1].scatter([x * 100 for x in mid_ar], ortg, color='#ff4d4d', alpha=0.45, s=22)
    axs[0, 1].plot([x * 100 for x in x_t], y_t, color='#ff1a1a', linewidth=2.5, label=f'Trendline (r = {r_mid:+.3f})')
    axs[0, 1].set_title('Mid-Range Attempt Rate (MidAr) vs. ORtg', fontsize=12, fontweight='bold', color='#ff6666')
    axs[0, 1].set_xlabel('Mid-Range Attempt Rate (% of FGA 7-20 ft)', fontsize=10)
    axs[0, 1].set_ylabel('Offensive Rating (ORtg)', fontsize=10)
    axs[0, 1].grid(True, linestyle='--', alpha=0.25)
    axs[0, 1].legend(loc='upper right')

    # 3. 3-Point Attempt Rate (3PAr)
    x_t, y_t = get_trendline(three_ar, ortg)
    axs[1, 0].scatter([x * 100 for x in three_ar], ortg, color='#cc66ff', alpha=0.45, s=22)
    axs[1, 0].plot([x * 100 for x in x_t], y_t, color='#b31aff', linewidth=2.5, label=f'Trendline (r = {r_3p:+.3f})')
    axs[1, 0].set_title('3-Point Attempt Rate (3PAr) vs. ORtg', fontsize=12, fontweight='bold', color='#d98cff')
    axs[1, 0].set_xlabel('3-Point Attempt Rate (% of FGA 21+ ft)', fontsize=10)
    axs[1, 0].set_ylabel('Offensive Rating (ORtg)', fontsize=10)
    axs[1, 0].grid(True, linestyle='--', alpha=0.25)
    axs[1, 0].legend(loc='lower right')

    # 4. Free Throw Rate (FTr)
    x_t, y_t = get_trendline(ftr, ortg)
    axs[1, 1].scatter(ftr, ortg, color='#3399ff', alpha=0.45, s=22)
    axs[1, 1].plot(x_t, y_t, color='#0066ff', linewidth=2.5, label=f'Trendline (r = {r_ft:+.3f})')
    axs[1, 1].set_title('Free Throw Rate (FTr) vs. ORtg', fontsize=12, fontweight='bold', color='#66b2ff')
    axs[1, 1].set_xlabel('Free Throw Rate (FTA / FGA)', fontsize=10)
    axs[1, 1].set_ylabel('Offensive Rating (ORtg)', fontsize=10)
    axs[1, 1].grid(True, linestyle='--', alpha=0.25)
    axs[1, 1].legend(loc='lower right')

    plt.tight_layout()
    output_abs = os.path.abspath(output_file)
    plt.savefig(output_abs, dpi=300)
    plt.close()

    print("==========================================================================")
    print(f"  Hardwood Graph Generated: {output_abs}")
    print(f"  Filters: Season={season}, GameType={game_type}, Conf <= {max_conf}, N={n_teams} Teams")
    print("--------------------------------------------------------------------------")
    print(f"  RimAr  (0-6 ft)  to ORtg: r = {r_rim:+.3f}  (R^2 = {r_rim**2*100:5.1f}%)")
    print(f"  MidAr  (7-20 ft) to ORtg: r = {r_mid:+.3f}  (R^2 = {r_mid**2*100:5.1f}%)")
    print(f"  3PAr   (21+ ft)  to ORtg: r = {r_3p:+.3f}  (R^2 = {r_3p**2*100:5.1f}%)")
    print(f"  FTr    (FTA/FGA) to ORtg: r = {r_ft:+.3f}  (R^2 = {r_ft**2*100:5.1f}%)")
    print("==========================================================================")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Attempt Rates vs. ORtg PNG chart.")
    parser.add_argument("-s", "--season", default="2053", help="Season year (e.g. 2054, or 'all') [default: 2054].")
    parser.add_argument("-g", "--game_type", default="College", help="Game type filter (e.g. 'College', 'Conference', 'all') [default: College].")
    parser.add_argument("-c", "--max_conf", type=int, default=15, help="Maximum conference_id (conference_id <= max_conf) [default: 100].")
    parser.add_argument("-p", "--min_gp", type=int, default=3, help="Minimum games played filter (GP >= min_gp) [default: 3].")
    parser.add_argument("-o", "--output", default="53_D1_attempt_rates_vs_ortg.png", help="Output PNG file path [default: attempt_rates_vs_ortg.png].")
    parser.add_argument("-d", "--db", default=DB_PATH, help=f"Path to basketball.db [default: {DB_PATH}].")

    args = parser.parse_args()

    generate_attempt_rates_graph(
        season=args.season,
        game_type=args.game_type,
        max_conf=args.max_conf,
        min_gp=args.min_gp,
        db_path=args.db,
        output_file=args.output
    )
