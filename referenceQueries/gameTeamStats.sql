SELECT DISTINCT t.team_name, tst.*
FROM team_stats tst
JOIN teams t ON t.team_id = tst.team_id
WHERE tst.game_id = ?;