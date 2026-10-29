-- Step 1: Find teams with duplicate last names
WITH teams_with_duplicates AS (
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
),

-- Step 2: Select stat values excluding players from those teams
stats AS (
    SELECT
        "sf_rapm" AS value  -- replace "sf_rapm" with any column you want
    FROM player_avg pavg
    JOIN players p ON p.player_id = pavg.player_id
    JOIN team_avg tavg ON tavg.team_id = p.team_id 
                       AND tavg.season_id = pavg.season_id 
                       AND tavg.game_type = pavg.game_type
    WHERE pavg.season_id = 2046
      AND pavg.game_type = "College"
      AND pavg.GP >= 20
      AND pavg.SF_Min >= 20
      AND "sf_rapm" IS NOT NULL
      AND p.team_id NOT IN (SELECT team_id FROM teams_with_duplicates)
)

-- Step 3: Compute mean and std
SELECT
    AVG(value) AS mean_value,
    SQRT(AVG(value * value) - AVG(value) * AVG(value)) AS std_value
FROM stats;