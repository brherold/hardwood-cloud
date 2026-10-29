SELECT g.game_type, tst.*
From games g 
JOIN team_stats tst on tst.game_id = g.game_id
WHERE tst.team_id = 533 and g.season_id = 2045
ORDER BY g.game_date