select season_id, game_id, game_type
from games
where game_type NOT IN ("Exhibition", "Invitational")
and season_id = 2053
ORDER BY game_date asc