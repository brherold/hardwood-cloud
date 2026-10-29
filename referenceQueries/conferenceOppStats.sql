select t.team_name, tavg.* 
from team_avg tavg
JOIN teams t on t.team_id = tavg.team_id
where tavg.conference_id = ? and tavg.season_id = ? and tavg.game_type = "Conference" and tavg.stat_type = "opponent"
ORDER BY GW desc