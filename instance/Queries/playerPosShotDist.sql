select player_id, season_id, FG_A, round(1.0 * Rim_A / FG_A,3) as RimAr, round(1.0 * Mid_A / FG_A,3) as MidAr, _3PAr, FTr
from player_avg 
where GP >= 30
and PG_Min >= .9 * Min 
and FG_A >= 10
and game_type = "College" 
and season_id <= 2053
ORDER BY RimAr desc