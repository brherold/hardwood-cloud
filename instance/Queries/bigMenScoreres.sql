SELECT psk.player_id, psk.height, psk.wingspan, psk.vertical, pavg.player_id, psk."IS", pavg.IS_P, psk.IDef, pavg.O_IS_P
FROM players_skills psk
JOIN player_avg pavg on pavg.player_id = psk.player_id
WHERE psk.height <= 81.5 and psk.weight >= 260 and  pavg.IS_A >= 5 and pavg.game_type == "College" and pavg.GP >= 15 and ((pavg.PF_Min + pavg.C_Min) / (pavg.Min)) >= .9
ORDER BY psk.weight desc