

SELECT
    p.name,
    p.team_id,
    psk.*,
    CASE 
        WHEN pavg.PG_Min >= pavg.SG_Min AND pavg.PG_Min >= pavg.SF_Min AND pavg.PG_Min >= pavg.PF_Min AND pavg.PG_Min >= pavg.C_Min THEN 'PG'
        WHEN pavg.SG_Min >= pavg.PG_Min AND pavg.SG_Min >= pavg.SF_Min AND pavg.SG_Min >= pavg.PF_Min AND pavg.SG_Min >= pavg.C_Min THEN 'SG'
        WHEN pavg.SF_Min >= pavg.PG_Min AND pavg.SF_Min >= pavg.SG_Min AND pavg.SF_Min >= pavg.PF_Min AND pavg.SF_Min >= pavg.C_Min THEN 'SF'
        WHEN pavg.PF_Min >= pavg.PG_Min AND pavg.PF_Min >= pavg.SG_Min AND pavg.PF_Min >= pavg.SF_Min AND pavg.PF_Min >= pavg.C_Min THEN 'PF'
        ELSE 'C'
    END AS Primary_Position,
    pavg.*,
    tavg.NetRtg AS team_NetRtg  -- <-- team's avg PLUS
FROM players p
JOIN player_avg pavg 
    ON pavg.player_id = p.player_id
JOIN players_skills psk 
    ON psk.player_id = p.player_id 
    AND psk.season_id = pavg.season_id
JOIN team_avg tavg                          -- <-- new join
    ON tavg.team_id = p.team_id
    AND tavg.season_id = pavg.season_id
    AND tavg.game_type = pavg.game_type
    AND tavg.stat_type = 'team'             -- exclude opponent rows
WHERE pavg.game_type = 'College'
  AND pavg.season_id IN (2051)
  AND pavg.GP >= 30
  AND pavg.Min >= 10
  AND (
        (pavg.PG_Min >= pavg.SG_Min AND pavg.PG_Min >= pavg.SF_Min AND pavg.PG_Min >= pavg.PF_Min AND pavg.PG_Min >= pavg.C_Min AND pavg.PG_Min >= 0.75 * pavg.Min)
     OR (pavg.SG_Min >= pavg.PG_Min AND pavg.SG_Min >= pavg.SF_Min AND pavg.SG_Min >= pavg.PF_Min AND pavg.SG_Min >= pavg.C_Min AND pavg.SG_Min >= 0.75 * pavg.Min)
     OR (pavg.SF_Min >= pavg.PG_Min AND pavg.SF_Min >= pavg.SG_Min AND pavg.SF_Min >= pavg.PF_Min AND pavg.SF_Min >= pavg.C_Min AND pavg.SF_Min >= 0.75 * pavg.Min)
     OR (pavg.PF_Min >= pavg.PG_Min AND pavg.PF_Min >= pavg.SG_Min AND pavg.PF_Min >= pavg.SF_Min AND pavg.PF_Min >= pavg.C_Min AND pavg.PF_Min >= 0.75 * pavg.Min)
     OR (pavg.C_Min >= pavg.PG_Min AND pavg.C_Min >= pavg.SG_Min AND pavg.C_Min >= pavg.SF_Min AND pavg.C_Min >= pavg.PF_Min AND pavg.C_Min >= 0.75 * pavg.Min)
      )
ORDER BY pavg.season_id, pavg.EPM DESC;