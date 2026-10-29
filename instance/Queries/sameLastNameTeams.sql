WITH player_lastnames AS (
  SELECT
    t.team_id,
    SUBSTR(p.name, INSTR(p.name, ' ') + 1) AS last_name
  FROM players p
  JOIN teams t ON t.team_id = p.team_id
  JOIN player_avg pavg ON pavg.player_id = p.player_id
  WHERE pavg.game_type = 'College' AND pavg.season_id = 2048
)
SELECT DISTINCT team_id
FROM player_lastnames
GROUP BY team_id, last_name
HAVING COUNT(*) > 1;
