SELECT *,  round((IS_M + F_M) / (IS_A + F_A),3) AS Paint_P, round((F_A / FG_A),3) AS FAr, round((IS_A / FG_A),3) AS ISAr,round((MR_A / FG_A),3) AS MRAr, round((IS_A + F_A) / (FG_A),3) AS PaintAr
from team_avg
where conference_id <= 100
and game_type = "College"
and stat_type = "team"