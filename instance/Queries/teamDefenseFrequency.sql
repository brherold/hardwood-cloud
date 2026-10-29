WITH total_plays_all AS (
    SELECT SUM(plays) AS grand_total_plays
    FROM defense_stats def
    JOIN games g ON g.game_id = def.game_id
    WHERE def.team_id = 1 
      AND g.season_id = 2046 
      AND g.game_type IN ('Non-Conference','Conference','Playoff','Tournament')
)
SELECT 
    combined_defense AS defense_type,
    ROUND(SUM(plays) * 1.0 / (SELECT grand_total_plays FROM total_plays_all), 3) AS plays_pct
FROM (
    SELECT 
        CASE 
            WHEN defense_type LIKE 'z_%' THEN 'zone'
            WHEN defense_type LIKE 'm_%' THEN 'man'
            ELSE defense_type
        END AS combined_defense,
        plays
    FROM defense_stats def
    JOIN games g ON g.game_id = def.game_id
    WHERE def.team_id = 1 
      AND g.season_id = 2046 
      AND g.game_type IN ('Non-Conference','Conference','Playoff','Tournament')
) sub
GROUP BY combined_defense
ORDER BY SUM(plays) DESC;
