WITH total_plays_all AS (
    SELECT SUM(plays) AS grand_total_plays
    FROM defense_stats def
    JOIN games g ON g.game_id = def.game_id
    WHERE def.team_id = ? 
      AND g.season_id = ? 
      AND g.game_type in ("Non-Conference", "Conference", "Playoff","Tournament")
)
SELECT 
    def.defense_type,
    COUNT(CASE WHEN def.plays >= 1 THEN 1 END) AS G_P,
    SUM(def.plays) AS plays,
    
    -- Play percentage as decimal float
    ROUND(CAST(SUM(def.plays) AS FLOAT) / CAST((SELECT grand_total_plays FROM total_plays_all) AS FLOAT), 3) AS plays_pct,
    
    -- Total field goal attempts against
    SUM(def.F_A) + SUM(def.IS_A) + SUM(def.MR_A) + SUM(def._3P_A) AS FG_A,
    SUM(def.F_M) + SUM(def.IS_M) + SUM(def.MR_M) + SUM(def._3P_M) AS FG_M,
    
    -- Effective Field Goal allowed as decimal float
    CASE 
        WHEN (SUM(def.F_A) + SUM(def.IS_A) + SUM(def.MR_A) + SUM(def._3P_A)) > 0 
        THEN ROUND(
            (CAST(SUM(def.F_M) + SUM(def.IS_M) + SUM(def.MR_M) + SUM(def._3P_M) AS FLOAT) + 0.5 * CAST(SUM(def._3P_M) AS FLOAT)) 
            / CAST(SUM(def.F_A) + SUM(def.IS_A) + SUM(def.MR_A) + SUM(def._3P_A) AS FLOAT), 3
        )
        ELSE NULL 
    END AS eFG_P,
    
    -- Points Per Possession allowed (including Free Throws)
    CASE 
        WHEN SUM(def.plays) > 0 
        THEN ROUND(
            (CAST(SUM(def.F_M)*2 + SUM(def.IS_M)*2 + SUM(def.MR_M)*2 + SUM(def._3P_M)*3 + SUM(def.FT_M) AS FLOAT)) 
            / CAST(SUM(def.plays) AS FLOAT), 2
        )
        ELSE NULL 
    END AS PPP,
    
    -- 2-point stats
    SUM(def.F_M) + SUM(def.IS_M) + SUM(def.MR_M) AS _2P_M,
    SUM(def.F_A) + SUM(def.IS_A) + SUM(def.MR_A) AS _2P_A,
    CASE 
        WHEN (SUM(def.F_A) + SUM(def.IS_A) + SUM(def.MR_A)) > 0 
        THEN ROUND(CAST(SUM(def.F_M) + SUM(def.IS_M) + SUM(def.MR_M) AS FLOAT) / CAST(SUM(def.F_A) + SUM(def.IS_A) + SUM(def.MR_A) AS FLOAT), 3)
        ELSE NULL 
    END AS _2P_P,

    -- Rim (0-6) stats
    SUM(def.Rim_M) AS Rim_M,
    SUM(def.Rim_A) AS Rim_A,
    CASE 
        WHEN SUM(def.Rim_A) > 0 
        THEN ROUND(CAST(SUM(def.Rim_M) AS FLOAT) / CAST(SUM(def.Rim_A) AS FLOAT), 3)
        ELSE NULL 
    END AS Rim_P,

    -- Mid (7-20) stats
    SUM(def.Mid_M) AS Mid_M,
    SUM(def.Mid_A) AS Mid_A,
    CASE 
        WHEN SUM(def.Mid_A) > 0 
        THEN ROUND(CAST(SUM(def.Mid_M) AS FLOAT) / CAST(SUM(def.Mid_A) AS FLOAT), 3)
        ELSE NULL 
    END AS Mid_P,

    -- 3-Point stats
    SUM(def._3P_M) AS _3P_M,
    SUM(def._3P_A) AS _3P_A,
    CASE 
        WHEN SUM(def._3P_A) > 0 
        THEN ROUND(CAST(SUM(def._3P_M) AS FLOAT) / CAST(SUM(def._3P_A) AS FLOAT), 3)
        ELSE NULL 
    END AS _3P_P,

    -- Free Throw stats
    SUM(def.FT_M) AS FT_M,
    SUM(def.FT_A) AS FT_A,
    CASE 
        WHEN SUM(def.FT_A) > 0 
        THEN ROUND(CAST(SUM(def.FT_M) AS FLOAT) / CAST(SUM(def.FT_A) AS FLOAT), 3)
        ELSE NULL 
    END AS FT_P,

    -- Driving stats
    SUM(def.DR_M) AS DR_M,
    SUM(def.DR_A) AS DR_A,
    CASE 
        WHEN SUM(def.DR_A) > 0 
        THEN ROUND(CAST(SUM(def.DR_M) AS FLOAT) / CAST(SUM(def.DR_A) AS FLOAT), 3)
        ELSE NULL 
    END AS DR_P,

    -- Raw skill stats (kept for internal compatibility)
    SUM(def.F_M) AS F_M,
    SUM(def.F_A) AS F_A,
    SUM(def.IS_M) AS IS_M,
    SUM(def.IS_A) AS IS_A,
    SUM(def.MR_M) AS MR_M,
    SUM(def.MR_A) AS MR_A,
    SUM(def.TOV) AS TOV,
    
    -- Turnover Percentage forced as decimal float
    CASE 
        WHEN SUM(def.plays) > 0 
        THEN ROUND(CAST(SUM(def.TOV) AS FLOAT) / CAST(SUM(def.plays) AS FLOAT), 3)
        ELSE NULL 
    END AS TOV_P

FROM defense_stats def
JOIN games g ON g.game_id = def.game_id
CROSS JOIN total_plays_all
WHERE def.team_id = ?
  AND g.season_id = ? 
  AND g.game_type in ("Non-Conference", "Conference", "Playoff","Tournament")
GROUP BY def.defense_type, total_plays_all.grand_total_plays;
