SELECT team_id, season_id, round((F_A / FG_A),3) AS FAr, round((IS_A / FG_A),3) AS ISAr, round((IS_A + F_A) / (FG_A),3) AS PaintAr, round((MR_A / FG_A),3) AS MRAr, _3PAr, F_P, IS_P, round((IS_M + F_M) / (IS_A + F_A),3) AS Paint_P, MR_P, _3P_P
from team_avg
where conference_id <= 15
and game_type = "College"
and stat_type = "team"
and season_id = 2051