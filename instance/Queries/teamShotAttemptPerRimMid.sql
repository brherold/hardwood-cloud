SELECT team_id, season_id, FTr, round((Rim_A / FG_A),3) AS RimAr, round((Mid_A / FG_A),3) AS MidAr, _3PAr, Rim_P * 2 as Rim_PPP, Mid_P * 2 as Mid_PPP, _3P_P * 3 as _3P_PPP, ORtg
from team_avg
where conference_id <= 100
and game_type = "College"
and stat_type = "team"
and season_id = 2054
