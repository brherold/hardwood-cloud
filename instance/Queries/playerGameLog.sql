SELECT p.name, g.game_type, g.season_id, pst.*
FROM player_stats pst
JOIN players p on p.player_id = pst.player_id
JOIN games g on g.game_id = pst.game_id 
WHERE pst.player_id = 202447 and g.season_id = 2045
ORDER BY g.game_date ASC