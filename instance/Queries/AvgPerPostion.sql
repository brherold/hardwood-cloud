SELECT 'PG' AS Position, AVG(AST_P)
FROM player_avg
WHERE game_type = 'College' AND GP >= 20 AND Min >= 15 
AND PG_Min >= 0 AND SG_Min = 0 AND SF_Min = 0 AND PF_Min = 0 AND C_Min = 0

UNION ALL

SELECT 'SG', AVG(AST_P)
FROM player_avg
WHERE game_type = 'College' AND GP >= 20 AND Min >= 15 
AND PG_Min = 0 AND SG_Min >= 0 AND SF_Min = 0 AND PF_Min = 0 AND C_Min = 0

UNION ALL

SELECT 'SF', AVG(AST_P)
FROM player_avg
WHERE game_type = 'College' AND GP >= 20 AND Min >= 15 
AND PG_Min = 0 AND SG_Min = 0 AND SF_Min >= 0 AND PF_Min = 0 AND C_Min = 0

UNION ALL

SELECT 'PF', AVG(AST_P)
FROM player_avg
WHERE game_type = 'College' AND GP >= 20 AND Min >= 15 
AND PG_Min = 0 AND SG_Min = 0 AND SF_Min = 0 AND PF_Min >= 0 AND C_Min = 0

UNION ALL

SELECT 'C', AVG(AST_P)
FROM player_avg
WHERE game_type = 'College' AND GP >= 20 AND Min >= 15 
AND PG_Min = 0 AND SG_Min = 0 AND SF_Min = 0 AND PF_Min = 0 AND C_Min >= 0;
