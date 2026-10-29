WITH base AS (
SELECT 
    AVG(FAr) AS FAr,
    AVG(ISAr) AS ISAr,
    AVG(PaintAr) AS PaintAr,
    AVG(MRAr) AS MRAr,
    AVG(_3PAr) AS _3PAr,
    AVG(F_P) AS F_P,
    AVG(IS_P) AS IS_P,
    AVG(Paint_P) AS Paint_P,
    AVG(MR_P) AS MR_P,
    AVG(_3P_P) AS _3P_P
FROM (
    SELECT 
        (F_A * 1.0 / FG_A) AS FAr,
        (IS_A * 1.0 / FG_A) AS ISAr,
        ((IS_A + F_A) * 1.0 / FG_A) AS PaintAr,
        (MR_A * 1.0 / FG_A) AS MRAr,
        _3PAr,
        F_P,
        IS_P,
        ((IS_M + F_M) * 1.0 / (IS_A + F_A)) AS Paint_P,
        MR_P,
        _3P_P
    FROM team_avg
    WHERE conference_id <= 15
      AND game_type = "College"
      AND stat_type = "team"
      AND season_id IN (2051)
) t
),

denom AS (
SELECT
    (FAr * (2 * F_P)) +
    (ISAr * (2 * IS_P)) +
    (MRAr * (2 * MR_P)) +
    (_3PAr * (3 * _3P_P)) AS total_points,
    *
FROM base
)

SELECT 
    'ar_pps' AS row_type,
    ROUND(FAr,3) AS F,
    ROUND(ISAr,3) AS IS_,
    ROUND(PaintAr,3) AS Paint,
    ROUND(MRAr,3) AS MR,
    ROUND(_3PAr,3) AS _3P,
    ROUND(2*F_P,3) AS F_PPS,
    ROUND(2*IS_P,3) AS IS_PPS,
    ROUND(2*Paint_P,3) AS Paint_PPS,
    ROUND(2*MR_P,3) AS MR_PPS,
    ROUND(3*_3P_P,3) AS _3P_PPS
FROM denom

UNION ALL

SELECT
    'contribution_pct',
    ROUND((FAr*(2*F_P))/total_points,3),
    ROUND((ISAr*(2*IS_P))/total_points,3),
    ROUND(((FAr*(2*F_P))+(ISAr*(2*IS_P)))/total_points,3),
    ROUND((MRAr*(2*MR_P))/total_points,3),
    ROUND((_3PAr*(3*_3P_P))/total_points,3),
    NULL,NULL,NULL,NULL,NULL
FROM denom;