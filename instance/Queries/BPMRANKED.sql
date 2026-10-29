SELECT t.team_name, t.team_id, tavg.conference_id, round(1.0*tavg.GW/tavg.GP,3) AS WP,tavg.SOS, tavg.OBPM, tavg.DBPM, tavg.BPM, tavg.AOBPM, tavg.ADBPM, tavg.ABPM
FROM teams t
JOIN team_avg tavg on tavg.team_id = t.team_id
WHERE tavg.stat_type = "team" and tavg.game_type = "College" and tavg.season_id = 2050 and tavg.conference_id <= 15
ORDER BY tavg.ABPM DESC

