WITH base AS (
    SELECT 
        AVG(RimAr) AS RimAr,
        AVG(MidAr) AS MidAr,
        AVG(_3PAr) AS _3PAr,
        AVG(Rim_P) AS Rim_P,
        AVG(Mid_P) AS Mid_P,
        AVG(_3P_P) AS _3P_P
    FROM (
        SELECT 
            (Rim_A * 1.0 / FG_A) AS RimAr,
            (Mid_A * 1.0 / FG_A) AS MidAr,
            _3PAr,
            Rim_P,
            Mid_P,
            _3P_P
        FROM team_avg
        WHERE conference_id <= 15
          AND game_type = "College"
          AND stat_type = "team"
          AND season_id IN (2050)
    ) t
),

denom AS (
    SELECT
        (RimAr * (2 * Rim_P)) +
        (MidAr * (2 * Mid_P)) +
        (_3PAr * (3 * _3P_P)) AS total_points,
        *
    FROM base
)

SELECT 
    'ar_pps' AS row_type,
    ROUND(RimAr,3) AS Rim,
    ROUND(MidAr,3) AS Mid,
    ROUND(_3PAr,3) AS _3P,
    ROUND(2*Rim_P,3) AS Rim_PPS,
    ROUND(2*Mid_P,3) AS Mid_PPS,
    ROUND(3*_3P_P,3) AS _3P_PPS
FROM denom

UNION ALL

SELECT
    'contribution_pct',
    ROUND((RimAr*(2*Rim_P))/total_points,3),
    ROUND((MidAr*(2*Mid_P))/total_points,3),
    ROUND((_3PAr*(3*_3P_P))/total_points,3),
    NULL,NULL,NULL
FROM denom;