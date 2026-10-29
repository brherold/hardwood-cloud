select t.team_name, t.team_id as teamID, tavg.season_id as year, tavg.conference_id, round(1.0*tavg.GW/tavg.GP,3) as WP, tavg.NetRtg, tavg.SOS
from team_avg tavg 
JOIN teams t on t.team_id = tavg.team_id 
where tavg.stat_type = "team" and tavg.game_type = "College" and tavg.season_id = 2051
ORDER BY tavg.team_id