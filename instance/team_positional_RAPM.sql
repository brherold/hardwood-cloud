WITH TeamsWithDuplicateLastNames AS (
    SELECT team_id
    FROM (
        SELECT
            p.team_id,
            SUBSTR(p.name, INSTR(p.name, ' ') + 1) AS last_name
        FROM players p
        JOIN player_avg pavg 
            ON pavg.player_id = p.player_id
        WHERE pavg.game_type = 'College'
          AND pavg.season_id = 2046
    ) names
    GROUP BY team_id, last_name
    HAVING COUNT(*) > 1
),

PositionDistribution AS (
    SELECT 
        p.player_id,
        p.name,
        p.team_id,
        pavg.GP,

        pavg.PG_Min,
        pavg.SG_Min,
        pavg.SF_Min,
        pavg.PF_Min,
        pavg.C_Min,

        pavg.pg_rapm,
        pavg.sg_rapm,
        pavg.sf_rapm,
        pavg.pf_rapm,
        pavg.c_rapm,

        pavg.PG_Min * pavg.GP AS pg_weight,
        pavg.SG_Min * pavg.GP AS sg_weight,
        pavg.SF_Min * pavg.GP AS sf_weight,
        pavg.PF_Min * pavg.GP AS pf_weight,
        pavg.C_Min * pavg.GP AS c_weight

    FROM players p
    JOIN player_avg pavg 
        ON pavg.player_id = p.player_id
    WHERE pavg.game_type = 'College'
      AND pavg.season_id = 2046
      AND pavg.Min > 0
      AND NOT EXISTS (
            SELECT 1
            FROM TeamsWithDuplicateLastNames d
            WHERE d.team_id = p.team_id
      )
),

TeamPositionalRAPM AS (
    SELECT
        team_id,

        SUM(pg_rapm * pg_weight) / NULLIF(SUM(pg_weight), 0) AS pg_rapm,
        SUM(sg_rapm * sg_weight) / NULLIF(SUM(sg_weight), 0) AS sg_rapm,
        SUM(sf_rapm * sf_weight) / NULLIF(SUM(sf_weight), 0) AS sf_rapm,
        SUM(pf_rapm * pf_weight) / NULLIF(SUM(pf_weight), 0) AS pf_rapm,
        SUM(c_rapm * c_weight)  / NULLIF(SUM(c_weight), 0)  AS c_rapm,

        SUM(PG_Min) AS pg_minutes,
        SUM(SG_Min) AS sg_minutes,
        SUM(SF_Min) AS sf_minutes,
        SUM(PF_Min) AS pf_minutes,
        SUM(C_Min)  AS c_minutes,

        SUM(PG_Min + SG_Min + SF_Min + PF_Min + C_Min) AS total_minutes

    FROM PositionDistribution
    GROUP BY team_id
)

SELECT 
    t.season_id,
    t.team_id,

    tr.pg_rapm,
    ROUND(tr.pg_minutes * 100.0 / NULLIF(tr.total_minutes, 0), 1) AS pg_min_pct,

    tr.sg_rapm,
    ROUND(tr.sg_minutes * 100.0 / NULLIF(tr.total_minutes, 0), 1) AS sg_min_pct,

    tr.sf_rapm,
    ROUND(tr.sf_minutes * 100.0 / NULLIF(tr.total_minutes, 0), 1) AS sf_min_pct,

    tr.pf_rapm,
    ROUND(tr.pf_minutes * 100.0 / NULLIF(tr.total_minutes, 0), 1) AS pf_min_pct,

    tr.c_rapm,
    ROUND(tr.c_minutes * 100.0 / NULLIF(tr.total_minutes, 0), 1) AS c_min_pct,

    (
        tr.pg_rapm * tr.pg_minutes +
        tr.sg_rapm * tr.sg_minutes +
        tr.sf_rapm * tr.sf_minutes +
        tr.pf_rapm * tr.pf_minutes +
        tr.c_rapm  * tr.c_minutes
    ) / NULLIF(tr.total_minutes, 0) AS overall_weighted_rapm,

    1.0 * t.GW / t.GP AS WP,
    t.NetRtg

FROM team_avg t
LEFT JOIN TeamPositionalRAPM tr
    ON tr.team_id = t.team_id

WHERE t.game_type = 'College'
  AND t.stat_type = 'team'
  AND t.season_id = 2046
  AND NOT EXISTS (
        SELECT 1
        FROM TeamsWithDuplicateLastNames d
        WHERE d.team_id = t.team_id
  )

ORDER BY t.team_id;