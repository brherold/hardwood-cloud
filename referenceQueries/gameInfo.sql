SELECT 
    ht.team_name AS home_team_name,
    at.team_name AS away_team_name,
	g.*
FROM games g
JOIN teams ht ON ht.team_id = g.home_team_id
JOIN teams at ON at.team_id = g.away_team_id
WHERE g.game_id = ?;
