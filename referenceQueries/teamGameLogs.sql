SELECT g.game_type, tst.*
From games g 
JOIN team_stats tst on tst.game_id = g.game_id
WHERE tst.team_id = ? and g.season_id = ?
ORDER BY g.game_date