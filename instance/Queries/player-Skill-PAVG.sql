SELECT p.name, psk.*, pavg.*
FROM players p 
JOIN players_skills psk on psk.player_id = p.player_id
JOIN player_avg pavg on pavg.player_id = p.player_id
WHERE p.team_id = 1 and pavg.game_type = "College" and pavg.season_id = 2046 and pavg.season_id = psk.season_id
ORDER BY pavg.Min desc