select t.team_name, tavg.*
FROM team_avg tavg
JOIN teams t on t.team_id = tavg.team_id
where tavg.team_id = ? and tavg.season_id = ? and tavg.game_type = ? and tavg.stat_type = "team"