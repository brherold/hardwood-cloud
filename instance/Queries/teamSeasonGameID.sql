select g.season_id, ts.game_id, g.game_type
from team_stats ts 
join games g on ts.game_id = g.game_id 
and g.game_type NOT IN ("Exhibition", "Invitational")
WHERE ts.team_id = 817 and g.season_id = 2051
ORDER BY g.game_date asc