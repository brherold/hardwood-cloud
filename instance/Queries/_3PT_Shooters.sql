SELECT COUNT(psk.player_id), AVG(pavg._3P_P)
From players_skills psk
JOIN player_avg pavg on pavg.player_id = psk.player_id
WHERE pavg.GP >= 20  and psk.season_id = pavg.season_id
and pavg._3P_A >= 5
and .4 * psk.OS + .4 * psk.Rng + .2 * Spd = (40 - 22.8)