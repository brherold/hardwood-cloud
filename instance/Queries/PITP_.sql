select team_id, round((PITP / PTS) * 100,1) AS PITP_P
from team_avg 
where game_type = "College"
and stat_type = "team"
and conference_id <= 15
and season_id = 2046
ORDER BY 2 DESC