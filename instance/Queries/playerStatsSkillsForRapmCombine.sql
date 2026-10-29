select p.name, psk.*, pavg.*
from players  p
join players_skills psk on  p.player_id = psk.player_id 
join player_avg pavg on pavg.player_id = psk.player_id and pavg.season_id = psk.season_id 
where psk.season_id = 2050
and pavg.game_type = "College" 
  AND pavg.GP >= 15
  AND pavg.Min >= 10