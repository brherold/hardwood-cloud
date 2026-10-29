select  tavg.season_id, t.team_name, tavg.team_id , tavg.conference_id, p.name as player_name, pavg.player_id, pavg.game_type, pavg.GP, tavg.GP as team_GP,pavg.PG_Min, pavg.SG_Min, pavg.SF_Min, pavg.PF_Min,pavg.C_Min,pavg.Min
from players p 
join player_avg pavg on pavg.player_id = p.player_id and pavg.season_id = 2053 and pavg.game_type = "College"
join team_avg tavg on tavg.team_id = p.team_id and tavg.season_id = pavg.season_id and tavg.game_type = pavg.game_type
and tavg.stat_type = "team"
join teams t on t.team_id = tavg.team_id
WHERE pavg.Min >= 1 and pavg.GP >= 1
ORDER BY tavg.team_id