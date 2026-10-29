SELECT tavg.conference_id, AVG(tavg.AOBPM) AS avg_OPM, AVG(tavg.ADBPM) AS avg_DPM, AVG(tavg.ABPM) AS avg_ABPM
FROM team_avg tavg 
WHERE tavg.stat_type = "team" and tavg.game_type = "College" and tavg.season_id = 2050 and tavg.conference_id <= 15
GROUP BY tavg.conference_id 
ORDER BY avg_ABPM DESC


