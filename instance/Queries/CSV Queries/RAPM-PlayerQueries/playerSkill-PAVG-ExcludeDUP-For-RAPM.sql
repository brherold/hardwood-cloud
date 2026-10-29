-- First, get the teams with duplicate last names
WITH duplicate_lastname_teams AS (
    WITH player_lastnames AS (
        SELECT
            t.team_id,
            SUBSTR(p.name, INSTR(p.name, ' ') + 1) AS last_name
        FROM players p
        JOIN teams t ON t.team_id = p.team_id
        JOIN player_avg pavg ON pavg.player_id = p.player_id
        WHERE pavg.game_type = 'College'
          AND pavg.season_id = 2046
    )
    SELECT team_id
    FROM player_lastnames
    GROUP BY team_id, last_name
    HAVING COUNT(*) > 1
)

-- Now select all players EXCLUDING those teams
SELECT p.name, p.team_id, psk.*, pavg.*, prapm.*
FROM players p
JOIN player_avg pavg 
    ON pavg.player_id = p.player_id
JOIN players_skills psk 
    ON psk.player_id = pavg.player_id
   AND psk.season_id = pavg.season_id
JOIN player_RAPM prapm ON
	prapm.player_id = pavg.player_id 
AND prapm.season_id = pavg.season_id
AND prapm.game_type = pavg.game_type
WHERE pavg.season_id = 2046
  AND pavg.game_type = 'College'
  AND (
       pavg.PG_Min >= 10 OR
       pavg.SG_Min >= 10 OR
       pavg.SF_Min >= 10 OR
       pavg.PF_Min >= 10 OR
       pavg.C_Min  >= 10
  )
  and pavg.GP >= 20
  AND p.team_id NOT IN (SELECT team_id FROM duplicate_lastname_teams)
