SELECT 
	DISTINCT
    p.name, 
    p.player_id,
	t.team_name,
    CASE 
        WHEN pavg.PG_Min >= pavg.SG_Min AND pavg.PG_Min >= pavg.SF_Min AND pavg.PG_Min >= pavg.PF_Min AND pavg.PG_Min >= pavg.C_Min THEN 'PG'
        WHEN pavg.SG_Min >= pavg.PG_Min AND pavg.SG_Min >= pavg.SF_Min AND pavg.SG_Min >= pavg.PF_Min AND pavg.SG_Min >= pavg.C_Min THEN 'SG'
        WHEN pavg.SF_Min >= pavg.PG_Min AND pavg.SF_Min >= pavg.SG_Min AND pavg.SF_Min >= pavg.PF_Min AND pavg.SF_Min >= pavg.C_Min THEN 'SF'
        WHEN pavg.PF_Min >= pavg.PG_Min AND pavg.PF_Min >= pavg.SG_Min AND pavg.PF_Min >= pavg.SF_Min AND pavg.PF_Min >= pavg.C_Min THEN 'PF'
        ELSE 'C'
    END AS Primary_Position,
	pavg.GP,
    pavg.Min,
    pavg.OEPM, 
    pavg.DEPM, 
    pavg.EPM,
	ROUND(1.0*(pavg.EPM + 3)*(1.0*pavg.Min/40)*(1.0*pavg.GP/tavg.GP),1) AS VORP
FROM players p
JOIN player_avg pavg ON pavg.player_id = p.player_id
JOIN teams t on t.team_id = p.team_id
JOIN team_avg tavg on tavg.team_id = t.team_id
WHERE pavg.game_type = "Conference"
  AND pavg.season_id = 2050
  AND pavg.GP >= (tavg.GP * .75)
  AND pavg.Min >= 10
  and tavg.conference_id = 1
  and tavg.season_id = pavg.season_id
  and tavg.game_type = pavg.game_type
  and tavg.stat_type = "team"
 
ORDER BY EPM DESC;
