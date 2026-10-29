select pavg.GP, pavg.Min, prapm.*
from player_avg pavg 
join player_RAPM prapm on prapm.player_id = pavg.player_id and prapm.season_id = pavg.season_id and prapm.game_type = pavg.game_type 
where pavg.GP >= 20 
and pavg.Min >= 10
and pavg.PG_Min = pavg.Min