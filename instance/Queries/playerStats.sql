SELECT DISTINCT p.name, psk.Pos,pavg.*
FROM players p
JOIN player_avg pavg on pavg.player_id = p.player_id
JOIN players_skills psk on psk.player_id = p.player_id
WHERE p.team_id = 533 AND pavg.game_type = "College"  and pavg.season_id = 2052 and psk.season_id = pavg.season_id 
ORDER BY pavg.Min desc