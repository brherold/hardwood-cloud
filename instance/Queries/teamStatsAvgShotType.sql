select AVG((ts.IS_A + ts.F_A) / (ts.FG_A)) AS Paint_Ar,  MAX((ts.IS_A + ts.F_A) / (ts.FG_A)) AS Max_Paint_Ar, AVG((ts.IS_M + ts.F_M)/(ts.IS_A + ts.F_A)) AS Paint_P,
AVG((ts.MR_A) / (ts.FG_A)) AS MRAr, AVG(MR_P) AS MR_P, AVG(1.00 *ts._3P_A / ts.FG_A) AS _3PAr, AVG(_3P_P) AS _3P_P
from games g
join team_stats ts on ts.game_id = g.game_id 
where g.season_id  IN (2044,2045,2046)