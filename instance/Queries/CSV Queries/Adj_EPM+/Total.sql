-- Calculate team-level OEPM/DEPM/EPM using all players
WITH team_stats AS (
    SELECT 
        p.team_id,
        SUM(pavg.OEPM * pavg.GP * pavg.Min) / SUM(pavg.GP * pavg.Min) AS team_OEPM,
        SUM(pavg.DEPM * pavg.GP * pavg.Min) / SUM(pavg.GP * pavg.Min) AS team_DEPM,
        SUM(pavg.EPM * pavg.GP * pavg.Min)  / SUM(pavg.GP * pavg.Min) AS team_EPM
    FROM players p
    JOIN player_avg pavg ON pavg.player_id = p.player_id
    WHERE pavg.game_type = 'College'
      AND pavg.season_id = 2046
    GROUP BY p.team_id
)

-- Select individual players with GP/Min filters
SELECT
    p.name,
	p.player_id,
    p.team_id,
	psk.*,
    pavg.GP,
    pavg.Min,
	team_OEPM,
	team_DEPM,
    pavg.OEPM,
    pavg.DEPM,
    pavg.EPM,
    -- Adjusted EPM components using team-level values
    pavg.OEPM - (team_OEPM - (-0.6976 /6.5851))  AS adj_OEPM,
    pavg.DEPM - (team_DEPM - (-1.4334 /8.2345)) AS adj_DEPM,
    (pavg.OEPM - (team_OEPM - (-0.6976 /6.5851))) + (pavg.DEPM - (team_DEPM - (-1.4334 /8.2345))) AS adj_EPM
FROM players p
JOIN player_avg pavg ON pavg.player_id = p.player_id
JOIN team_stats ts ON ts.team_id = p.team_id
JOIN players_skills psk ON psk.player_id = p.player_id
WHERE pavg.game_type = 'College'
  AND pavg.season_id = 2046
  AND psk.season_id = pavg.season_id
  AND pavg.GP >= 20
  AND pavg.Min >= 15
ORDER BY adj_EPM DESC;
