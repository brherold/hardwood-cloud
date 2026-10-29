WITH position_labeled AS (
    SELECT
        pavg.*,
        CASE
            WHEN PG_Min >= SG_Min AND PG_Min >= SF_Min AND PG_Min >= PF_Min AND PG_Min >= C_Min THEN 'PG'
            WHEN SG_Min >= PG_Min AND SG_Min >= SF_Min AND SG_Min >= PF_Min AND SG_Min >= C_Min THEN 'SG'
            WHEN SF_Min >= PG_Min AND SF_Min >= SG_Min AND SF_Min >= PF_Min AND SF_Min >= C_Min THEN 'SF'
            WHEN PF_Min >= PG_Min AND PF_Min >= SG_Min AND PF_Min >= SF_Min AND PF_Min >= C_Min THEN 'PF'
            ELSE 'C'
        END AS Position
    FROM player_avg pavg
    WHERE game_type = 'College'
      AND season_id = 2046
      AND GP >= 20
      AND Min >= 15
)
SELECT DISTINCT 
    posl.Position,
    psk.*,
    posl.*
FROM position_labeled posl
LEFT JOIN players_skills psk 
  ON psk.player_id = posl.player_id 
  AND psk.season_id = posl.season_id
WHERE
    (
        (Position = 'PG' AND PG_Min >= 0.75 * Min) OR
        (Position = 'SG' AND SG_Min >= 0.75 * Min) OR
        (Position = 'SF' AND SF_Min >= 0.75 * Min) OR
        (Position = 'PF' AND PF_Min >= 0.75 * Min) OR
        (Position = 'C'  AND C_Min  >= 0.75 * Min)
    );
