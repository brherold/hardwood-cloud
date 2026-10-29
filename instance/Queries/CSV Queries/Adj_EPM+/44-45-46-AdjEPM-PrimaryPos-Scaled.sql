-- Calculate team-level OEPM/DEPM/EPM using all players
WITH team_avg AS (
    SELECT 
        p.team_id,
        pavg.season_id,
        SUM(pavg.OEPM * pavg.GP * pavg.Min) / SUM(pavg.GP * pavg.Min) AS team_OEPM,
        SUM(pavg.DEPM * pavg.GP * pavg.Min) / SUM(pavg.GP * pavg.Min) AS team_DEPM,
        SUM(pavg.EPM * pavg.GP * pavg.Min)  / SUM(pavg.GP * pavg.Min) AS team_EPM
    FROM players p
    JOIN player_avg pavg ON pavg.player_id = p.player_id
    WHERE pavg.game_type = 'College'
      AND pavg.season_id IN (2044,2045, 2046)
    GROUP BY p.team_id, pavg.season_id
)
SELECT
    p.name,
    p.player_id,
    p.team_id,
    pavg.season_id,
    psk.*,
    -- Determine primary position
    CASE 
        WHEN pavg.PG_Min >= pavg.SG_Min AND pavg.PG_Min >= pavg.SF_Min AND pavg.PG_Min >= pavg.PF_Min AND pavg.PG_Min >= pavg.C_Min THEN 'PG'
        WHEN pavg.SG_Min >= pavg.PG_Min AND pavg.SG_Min >= pavg.SF_Min AND pavg.SG_Min >= pavg.PF_Min AND pavg.SG_Min >= pavg.C_Min THEN 'SG'
        WHEN pavg.SF_Min >= pavg.PG_Min AND pavg.SF_Min >= pavg.SG_Min AND pavg.SF_Min >= pavg.PF_Min AND pavg.SF_Min >= pavg.C_Min THEN 'SF'
        WHEN pavg.PF_Min >= pavg.PG_Min AND pavg.PF_Min >= pavg.SG_Min AND pavg.PF_Min >= pavg.SF_Min AND pavg.PF_Min >= pavg.C_Min THEN 'PF'
        ELSE 'C'
    END AS Primary_Position,
    -- Adjusted EPM components
    pavg.OEPM - (team_OEPM - (-0.6976 /6.5851))  AS adj_OEPM,
    pavg.DEPM - (team_DEPM - (-1.4334 /8.2345)) AS adj_DEPM,
    (pavg.OEPM - (team_OEPM - (-0.6976 /6.5851))) + (pavg.DEPM - (team_DEPM - (-1.4334 /8.2345))) AS adj_EPM,
    -- Rescaled to match raw OPM+/DPM+ std
    ((pavg.OEPM - (team_OEPM - (-0.6976 /6.5851))) - 0.067497) * 1.667 + 0.067497 + (0.062680 - (-0.074685)) AS adj_OEPM_scaled,
    ((pavg.DEPM - (team_DEPM - (-1.4334 /8.2345))) + 0.022269) * 1.312 - 0.022269 + (-0.057236 - (-0.131476)) AS adj_DEPM_scaled,
    -- Combined scaled EPM
    ((pavg.OEPM - (team_OEPM - (-0.6976 /6.5851))) - 0.067497) * 1.667 + 0.067497 + (0.062680 - (-0.074685))
    + ((pavg.DEPM - (team_DEPM - (-1.4334 /8.2345))) + 0.022269) * 1.312 - 0.022269 + (-0.057236 - (-0.131476)) AS adj_EPM_scaled
FROM players p
JOIN player_avg pavg ON pavg.player_id = p.player_id
JOIN team_avg tavg ON tavg.team_id = p.team_id AND tavg.season_id = pavg.season_id
JOIN players_skills psk ON psk.player_id = p.player_id AND psk.season_id = pavg.season_id
WHERE pavg.game_type = 'College'
  AND pavg.GP >= 20
  AND pavg.Min >= 15
  AND (
        (pavg.PG_Min >= pavg.SG_Min AND pavg.PG_Min >= pavg.SF_Min AND pavg.PG_Min >= pavg.PF_Min AND pavg.PG_Min >= pavg.C_Min AND pavg.PG_Min >= 0.75 * pavg.Min)
     OR (pavg.SG_Min >= pavg.PG_Min AND pavg.SG_Min >= pavg.SF_Min AND pavg.SG_Min >= pavg.PF_Min AND pavg.SG_Min >= pavg.C_Min AND pavg.SG_Min >= 0.75 * pavg.Min)
     OR (pavg.SF_Min >= pavg.PG_Min AND pavg.SF_Min >= pavg.SG_Min AND pavg.SF_Min >= pavg.PF_Min AND pavg.SF_Min >= pavg.C_Min AND pavg.SF_Min >= 0.75 * pavg.Min)
     OR (pavg.PF_Min >= pavg.PG_Min AND pavg.PF_Min >= pavg.SG_Min AND pavg.PF_Min >= pavg.SF_Min AND pavg.PF_Min >= pavg.C_Min AND pavg.PF_Min >= 0.75 * pavg.Min)
     OR (pavg.C_Min >= pavg.PG_Min AND pavg.C_Min >= pavg.SG_Min AND pavg.C_Min >= pavg.SF_Min AND pavg.C_Min >= pavg.PF_Min AND pavg.C_Min >= 0.75 * pavg.Min)
      )
ORDER BY  adj_EPM_scaled DESC;
