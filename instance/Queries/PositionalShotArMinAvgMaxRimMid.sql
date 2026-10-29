WITH rates AS (
    SELECT
        Rim_A  * 1.0 / NULLIF(FG_A, 0)  AS RimAr,
        Rim_P,
        Mid_A * 1.0 / NULLIF(FG_A, 0)  AS MidAr,
        Mid_P,
        _3PAr,
        _3P_P,
        _2P_P,
        eFG_P,
        FTr
    FROM player_avg
    WHERE 
        game_type = "College"
        AND GP >= 20
        AND Min >= 20
        AND (PF_Min + C_Min) >= .9* Min
        AND FG_A >= 5
        AND season_id = 2054
)

SELECT 'MIN' AS stat,
       ROUND(RimAr, 3)   AS Rim_Ar,
       ROUND(Rim_P, 3)   AS Rim_P,
       ROUND(MidAr, 3)   AS Mid_Ar,
       ROUND(Mid_P, 3)   AS Mid_P,
       ROUND(_3PAr, 3)   AS _3P_Ar,
       ROUND(_3P_P, 3)   AS _3P_P,
       ROUND(_2P_P, 3)   AS _2P_P,
       ROUND(eFG_P, 3)   AS eFG_P,
       ROUND(FTr, 3)     AS FTr
FROM (
    SELECT MIN(RimAr) AS RimAr,
           MIN(Rim_P) AS Rim_P,
           MIN(MidAr) AS MidAr,
           MIN(Mid_P) AS Mid_P,
           MIN(_3PAr) AS _3PAr,
           MIN(_3P_P) AS _3P_P,
           MIN(_2P_P) AS _2P_P,
           MIN(eFG_P) AS eFG_P,
           MIN(FTr) AS FTr
    FROM rates
)

UNION ALL

SELECT 'AVG',
       ROUND(RimAr, 3),
       ROUND(Rim_P, 3),
       ROUND(MidAr, 3),
       ROUND(Mid_P, 3),
       ROUND(_3PAr, 3),
       ROUND(_3P_P, 3),
       ROUND(_2P_P, 3),
       ROUND(eFG_P, 3),
       ROUND(FTr, 3)
FROM (
    SELECT AVG(RimAr) AS RimAr,
           AVG(Rim_P) AS Rim_P,
           AVG(MidAr) AS MidAr,
           AVG(Mid_P) AS Mid_P,
           AVG(_3PAr) AS _3PAr,
           AVG(_3P_P) AS _3P_P,
           AVG(_2P_P) AS _2P_P,
           AVG(eFG_P) AS eFG_P,
           AVG(FTr) AS FTr
    FROM rates
)

UNION ALL

SELECT 'MAX',
       ROUND(RimAr, 3),
       ROUND(Rim_P, 3),
       ROUND(MidAr, 3),
       ROUND(Mid_P, 3),
       ROUND(_3PAr, 3),
       ROUND(_3P_P, 3),
       ROUND(_2P_P, 3),
       ROUND(eFG_P, 3),
       ROUND(FTr, 3)
FROM (
    SELECT MAX(RimAr) AS RimAr,
           MAX(Rim_P) AS Rim_P,
           MAX(MidAr) AS MidAr,
           MAX(Mid_P) AS Mid_P,
           MAX(_3PAr) AS _3PAr,
           MAX(_3P_P) AS _3P_P,
           MAX(_2P_P) AS _2P_P,
           MAX(eFG_P) AS eFG_P,
           MAX(FTr) AS FTr
    FROM rates
);