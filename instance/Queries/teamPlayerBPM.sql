SELECT p.name, p.player_id, psk.Pos,pavg.Min,pavg.OBPM, pavg.DBPM, pavg.BPM, pavg.OEPM, pavg.DEPM, pavg.EPM
FROM players p
JOIN player_avg pavg on pavg.player_id = p.player_id
JOIN players_skills psk on psk.player_id = p.player_id
WHERE team_id = 533 AND pavg.game_type = "College" and pavg.season_id = 2046 and psk.season_id = pavg.season_id and pavg.GP >= 5
ORDER BY pavg.BPM desc