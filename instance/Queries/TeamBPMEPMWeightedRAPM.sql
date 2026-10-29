
-- REMOVE TEAMS WHO HAVE SAME LAST NAME PLAYERS
WITH excluded_teams AS (
    WITH player_lastnames AS (
        SELECT
            t.team_id,
            SUBSTR(p.name, INSTR(p.name, ' ') + 1) AS last_name
        FROM players p
        JOIN teams t ON t.team_id = p.team_id
        JOIN player_avg pavg ON pavg.player_id = p.player_id
        WHERE pavg.game_type = 'College' AND pavg.season_id = 2046
    )
    SELECT DISTINCT team_id
    FROM player_lastnames
    GROUP BY team_id, last_name
    HAVING COUNT(*) > 1
)
SELECT 
    p.team_id,
    pavg.season_id,
	
	SUM(pavg.RAPM * pavg.GP * pavg.Min) / SUM(pavg.GP * pavg.Min) AS RAPM,
    SUM(pavg.OEPM * pavg.GP * pavg.Min) / SUM(pavg.GP * pavg.Min) AS OEPM,
    SUM(pavg.DEPM * pavg.GP * pavg.Min) / SUM(pavg.GP * pavg.Min) AS DEPM,
    SUM(pavg.EPM  * pavg.GP * pavg.Min) / SUM(pavg.GP * pavg.Min) AS EPM,
    SUM(pavg.OBPM * pavg.GP * pavg.Min) / SUM(pavg.GP * pavg.Min) AS OBPM,
    SUM(pavg.DBPM * pavg.GP * pavg.Min) / SUM(pavg.GP * pavg.Min) AS DBPM,
    SUM(pavg.BPM  * pavg.GP * pavg.Min) / SUM(pavg.GP * pavg.Min) AS BPM,
	SUM(pavg.PLUS  * pavg.GP * pavg.Min) / SUM(pavg.GP * pavg.Min) AS PLUS,
    
    (1.0 * tavg.GW / tavg.GP) AS WP,
    tavg.NetRtg

FROM players p
JOIN player_avg pavg 
    ON pavg.player_id = p.player_id
JOIN team_avg tavg 
    ON tavg.team_id = p.team_id
   AND tavg.game_type = pavg.game_type
   AND tavg.stat_type = "team"
   AND tavg.season_id = pavg.season_id

WHERE pavg.game_type = 'College'
  AND pavg.season_id = 2046
  AND p.team_id NOT IN (SELECT team_id FROM excluded_teams)

GROUP BY p.team_id, pavg.season_id, tavg.GW, tavg.GP, tavg.NetRtg
HAVING RAPM IS NOT NULL
ORDER BY RAPM DESC;