WITH total_plays_all AS (
    SELECT SUM(plays) AS grand_total_plays
    FROM offense_stats off
    JOIN games g ON g.game_id = off.game_id
    WHERE off.team_id = ? 
      AND g.season_id = ? 
      AND g.game_type in ('Non-Conference', 'Conference', 'Playoff', 'Tournament')
)
SELECT 
    off.defense_type,
    COUNT(CASE WHEN off.plays >= 1 THEN 1 END) AS G_P,
    SUM(off.plays) AS plays,
    
    -- Play percentage as decimal float
    ROUND(CAST(SUM(off.plays) AS FLOAT) / CAST((SELECT grand_total_plays FROM total_plays_all) AS FLOAT), 3) AS plays_pct,
    
    -- Total field goal attempts
    SUM(off.F_A) + SUM(off.IS_A) + SUM(off.MR_A) + SUM(off._3P_A) AS FG_A,
    SUM(off.F_M) + SUM(off.IS_M) + SUM(off.MR_M) + SUM(off._3P_M) AS FG_M,
    
    -- Effective Field Goal as decimal float
    CASE 
        WHEN (SUM(off.F_A) + SUM(off.IS_A) + SUM(off.MR_A) + SUM(off._3P_A)) > 0 
        THEN ROUND(
            (CAST(SUM(off.F_M) + SUM(off.IS_M) + SUM(off.MR_M) + SUM(off._3P_M) AS FLOAT) + 0.5 * CAST(SUM(off._3P_M) AS FLOAT)) 
            / CAST(SUM(off.F_A) + SUM(off.IS_A) + SUM(off.MR_A) + SUM(off._3P_A) AS FLOAT), 3
        )
        ELSE NULL 
    END AS eFG_P,
    
    -- Points Per Possession as float (including Free Throws)
    CASE 
        WHEN SUM(off.plays) > 0 
        THEN ROUND(
            (CAST(SUM(off.F_M)*2 + SUM(off.IS_M)*2 + SUM(off.MR_M)*2 + SUM(off._3P_M)*3 + SUM(off.FT_M) AS FLOAT)) 
            / CAST(SUM(off.plays) AS FLOAT), 2
        )
        ELSE NULL 
    END AS PPP,
    
    -- 2-point stats
    SUM(off.F_M) + SUM(off.IS_M) + SUM(off.MR_M) AS _2P_M,
    SUM(off.F_A) + SUM(off.IS_A) + SUM(off.MR_A) AS _2P_A,
    CASE 
        WHEN (SUM(off.F_A) + SUM(off.IS_A) + SUM(off.MR_A)) > 0 
        THEN ROUND(CAST(SUM(off.F_M) + SUM(off.IS_M) + SUM(off.MR_M) AS FLOAT) / CAST(SUM(off.F_A) + SUM(off.IS_A) + SUM(off.MR_A) AS FLOAT), 3)
        ELSE NULL 
    END AS _2P_P,

    -- Rim (0-6) stats
    SUM(off.Rim_M) AS Rim_M,
    SUM(off.Rim_A) AS Rim_A,
    CASE 
        WHEN SUM(off.Rim_A) > 0 
        THEN ROUND(CAST(SUM(off.Rim_M) AS FLOAT) / CAST(SUM(off.Rim_A) AS FLOAT), 3)
        ELSE NULL 
    END AS Rim_P,

    -- Mid (7-20) stats
    SUM(off.Mid_M) AS Mid_M,
    SUM(off.Mid_A) AS Mid_A,
    CASE 
        WHEN SUM(off.Mid_A) > 0 
        THEN ROUND(CAST(SUM(off.Mid_M) AS FLOAT) / CAST(SUM(off.Mid_A) AS FLOAT), 3)
        ELSE NULL 
    END AS Mid_P,

    -- 3-Point stats
    SUM(off._3P_M) AS _3P_M,
    SUM(off._3P_A) AS _3P_A,
    CASE 
        WHEN SUM(off._3P_A) > 0 
        THEN ROUND(CAST(SUM(off._3P_M) AS FLOAT) / CAST(SUM(off._3P_A) AS FLOAT), 3)
        ELSE NULL 
    END AS _3P_P,

    -- Free Throw stats
    SUM(off.FT_M) AS FT_M,
    SUM(off.FT_A) AS FT_A,
    CASE 
        WHEN SUM(off.FT_A) > 0 
        THEN ROUND(CAST(SUM(off.FT_M) AS FLOAT) / CAST(SUM(off.FT_A) AS FLOAT), 3)
        ELSE NULL 
    END AS FT_P,

    -- Driving stats
    SUM(off.DR_M) AS DR_M,
    SUM(off.DR_A) AS DR_A,
    CASE 
        WHEN SUM(off.DR_A) > 0 
        THEN ROUND(CAST(SUM(off.DR_M) AS FLOAT) / CAST(SUM(off.DR_A) AS FLOAT), 3)
        ELSE NULL 
    END AS DR_P,

    -- Raw skill stats (kept for internal compatibility)
    SUM(off.F_M) AS F_M,
    SUM(off.F_A) AS F_A,
    SUM(off.IS_M) AS IS_M,
    SUM(off.IS_A) AS IS_A,
    SUM(off.MR_M) AS MR_M,
    SUM(off.MR_A) AS MR_A,
    SUM(off.TOV) AS TOV,
    
    -- Turnover Percentage as decimal float
    CASE 
        WHEN SUM(off.plays) > 0 
        THEN ROUND(CAST(SUM(off.TOV) AS FLOAT) / CAST(SUM(off.plays) AS FLOAT), 3)
        ELSE NULL 
    END AS TOV_P

FROM offense_stats off
JOIN games g ON g.game_id = off.game_id
CROSS JOIN total_plays_all
WHERE off.team_id = ?
  AND g.season_id = ? 
  AND g.game_type in ('Non-Conference', 'Conference', 'Playoff', 'Tournament')
GROUP BY off.defense_type, total_plays_all.grand_total_plays;
