WITH rates AS (
    SELECT
        F_A  * 1.0 / NULLIF(FG_A, 0)  AS FAr,
        IS_A * 1.0 / NULLIF(FG_A, 0)  AS ISAr,
        MR_A * 1.0 / NULLIF(FG_A, 0)  AS MRAr,
        _3PAr,
        FTr
    FROM player_avg
    WHERE 
        game_type = "Conference"
        AND GP >= 20
        AND Min >= 20
        AND SF_Min = Min
        AND FG_A >= 5
)

SELECT 'MIN' AS stat,
       ROUND(MIN(FAr), 3)  AS FAr,
       ROUND(MIN(ISAr), 3) AS ISAr,
       ROUND(MIN(MRAr), 3) AS MRAr,
       ROUND(MIN(_3PAr), 3) AS _3PAr,
       ROUND(MIN(FTr), 3)  AS FTr
FROM rates

UNION ALL

SELECT 'AVG',
       ROUND(AVG(FAr), 3),
       ROUND(AVG(ISAr), 3),
       ROUND(AVG(MRAr), 3),
       ROUND(AVG(_3PAr), 3),
       ROUND(AVG(FTr), 3)
FROM rates

UNION ALL

SELECT 'MAX',
       ROUND(MAX(FAr), 3),
       ROUND(MAX(ISAr), 3),
       ROUND(MAX(MRAr), 3),
       ROUND(MAX(_3PAr), 3),
       ROUND(MAX(FTr), 3)
FROM rates;
