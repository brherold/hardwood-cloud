SELECT DISTINCT
    p.name,
	    CASE
        WHEN pavg.PG_Min >= pavg.SG_Min AND pavg.PG_Min >= pavg.SF_Min AND pavg.PG_Min >= pavg.PF_Min AND pavg.PG_Min >= pavg.C_Min THEN 'PG'
        WHEN pavg.SG_Min >= pavg.PG_Min AND pavg.SG_Min >= pavg.SF_Min AND pavg.SG_Min >= pavg.PF_Min AND pavg.SG_Min >= pavg.C_Min THEN 'SG'
        WHEN pavg.SF_Min >= pavg.PG_Min AND pavg.SF_Min >= pavg.SG_Min AND pavg.SF_Min >= pavg.PF_Min AND pavg.SF_Min >= pavg.C_Min THEN 'SF'
        WHEN pavg.PF_Min >= pavg.PG_Min AND pavg.PF_Min >= pavg.SG_Min AND pavg.PF_Min >= pavg.SF_Min AND pavg.PF_Min >= pavg.C_Min THEN 'PF'
        ELSE 'C'
    END AS Primary_Position,
    p.team_id,
    tavg.conference_id,
    tavg.SOS,
    psk.*,
    pavg.*
FROM players p
JOIN players_skills psk ON psk.player_id = p.player_id AND psk.season_id = 2045
JOIN (
    SELECT DISTINCT team_id, season_id, conference_id, SOS
    FROM team_avg
    WHERE season_id = 2045
      AND game_type = 'College'
      AND stat_type = 'team'
) tavg ON tavg.team_id = p.team_id
JOIN player_avg pavg ON pavg.player_id = p.player_id
  AND pavg.game_type = 'College'
  AND pavg.season_id = 2045
WHERE pavg.GP >= 20
  AND pavg.Min >= 15
  AND (
    (pavg.PG_Min >= pavg.SG_Min AND pavg.PG_Min >= pavg.SF_Min AND pavg.PG_Min >= pavg.PF_Min AND pavg.PG_Min >= pavg.C_Min AND pavg.PG_Min >= 0.75 * pavg.Min) OR
    (pavg.SG_Min >= pavg.PG_Min AND pavg.SG_Min >= pavg.SF_Min AND pavg.SG_Min >= pavg.PF_Min AND pavg.SG_Min >= pavg.C_Min AND pavg.SG_Min >= 0.75 * pavg.Min) OR
    (pavg.SF_Min >= pavg.PG_Min AND pavg.SF_Min >= pavg.SG_Min AND pavg.SF_Min >= pavg.PF_Min AND pavg.SF_Min >= pavg.C_Min AND pavg.SF_Min >= 0.75 * pavg.Min) OR
    (pavg.PF_Min >= pavg.PG_Min AND pavg.PF_Min >= pavg.SG_Min AND pavg.PF_Min >= pavg.SF_Min AND pavg.PF_Min >= pavg.C_Min AND pavg.PF_Min >= 0.75 * pavg.Min) OR
    (pavg.C_Min >= pavg.PG_Min AND pavg.C_Min >= pavg.SG_Min AND pavg.C_Min >= pavg.SF_Min AND pavg.C_Min >= pavg.PF_Min AND pavg.C_Min >= 0.75 * pavg.Min)
  )
ORDER BY tavg.conference_id;
