SELECT
(
    COUNT(*) * SUM(x * y) - SUM(x) * SUM(y)
) /
(
    SQRT(
        (COUNT(*) * SUM(x * x) - SUM(x) * SUM(x)) *
        (COUNT(*) * SUM(y * y) - SUM(y) * SUM(y))
    )
) AS correlation
FROM (
    SELECT
        EPM AS x,
        PLUS AS y
    FROM player_avg
    WHERE season_id = 2046
      AND game_type = 'College'
	  AND GP >= 15
	  AND Min >= 20
	  AND C_Min = Min
);