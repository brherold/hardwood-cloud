SELECT psk.player_id, psk.height,psk.weight,psk.wingspan,psk.vertical, psk."IS", pavg.IS_A, pavg.IS_P
From players_skills psk
JOIN player_avg pavg on pavg.player_id = psk.player_id
WHERE pavg.GP > 15 and pavg.IS_A > 5 and pavg.IS_P > .6