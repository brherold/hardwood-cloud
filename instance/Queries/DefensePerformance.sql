SELECT 
    defense_type, 
    
    -- Turnover Percentage
    ROUND(1.0 * SUM(TOV) / NULLIF(SUM(plays), 0), 2) AS TOV_P,

    -- Finishing Percentage
    ROUND(1.0 * SUM(F_M) / NULLIF(SUM(F_A), 0), 2) AS FIN_P,

    -- Inside Shot Percentage
    ROUND(1.0 * SUM(IS_M) / NULLIF(SUM(IS_A), 0), 2) AS IS_P,

    -- Mid-Range Shot Percentage
    ROUND(1.0 * SUM(MR_M) / NULLIF(SUM(MR_A), 0), 2) AS MR_P,

    -- 3-Point Shot Percentage
    ROUND(1.0 * SUM(_3P_M) / NULLIF(SUM(_3P_A), 0), 2) AS _3P_P,

    -- Effective Field Goal Percentage
    ROUND(
        1.0 * (
            SUM(F_M) + 
            SUM(IS_M) + 
            SUM(MR_M) + 
            1.5 * SUM(_3P_M)
        ) / NULLIF(
            SUM(F_A) + 
            SUM(IS_A) + 
            SUM(MR_A) + 
            SUM(_3P_A), 0
        ), 
    2) AS eFG,

    -- Points Per Possession Allowed (including Free Throws)
    ROUND(
        1.0 * (
            SUM(F_M) * 2 + 
            SUM(IS_M) * 2 + 
            SUM(MR_M) * 2 + 
            SUM(_3P_M) * 3 +
            SUM(FT_M)
        ) / NULLIF(SUM(plays), 0), 
    2) AS PPP

FROM defense_stats
GROUP BY defense_type;
