SELECT t.team_name, t.team_id, p.name, pst.*
from players p 
JOIN player_stats pst on pst.player_id = p.player_id
JOIN teams t on t.team_id = p.team_id
WHERE game_id = ?
ORDER BY p.team_id 