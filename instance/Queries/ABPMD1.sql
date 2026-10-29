SELECT t.team_name, tavg.*
FROM team_avg tavg 
JOIN teams t on t.team_id = tavg.team_id
WHERE tavg.season_id = 2050 and tavg.conference_id <= 15 and stat_type = "team" and game_type = "College"
ORDER BY tavg.ABPM DESC
