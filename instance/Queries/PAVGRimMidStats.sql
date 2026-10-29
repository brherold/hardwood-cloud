SELECT DISTINCT p.name, psk.Pos,pavg.season_id, pavg.game_type, pavg.GS, pavg.GP, pavg.FG_A, pavg.Min, round(pavg.Rim_A / pavg.FG_A,3) AS RimAr, round(pavg.Mid_A / pavg.FG_A,3) AS MidAr,  pavg._3PAr,pavg.Rim_P ,  pavg.Mid_P, pavg._3P_P
FROM players p
JOIN player_avg pavg on pavg.player_id = p.player_id
JOIN players_skills psk on psk.player_id = p.player_id
WHERE p.team_id = 533 AND pavg.game_type = "Conference"  and pavg.season_id = 2051 and psk.season_id = pavg.season_id and pavg.GP >=5
ORDER BY pavg.Min desc