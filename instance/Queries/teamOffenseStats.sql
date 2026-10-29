WITH total_plays_all AS (
    SELECT SUM(plays) AS grand_total_plays
    FROM offense_stats off
    JOIN games g ON g.game_id = off.game_id
    WHERE off.team_id = 533 
      AND g.season_id = 2046 
      AND g.game_type IN ('Non-Conference','Conference','Playoff','Tournament')
)
SELECT 
    off.defense_type,
	COUNT(CASE WHEN off.plays >= 1 THEN 1 END) AS Games_Used,
    SUM(off.plays) AS plays,
    
    -- Play percentage as decimal float
    ROUND(CAST(SUM(off.plays) AS FLOAT) / CAST((SELECT grand_total_plays FROM total_plays_all) AS FLOAT), 3) AS plays_pct,
    
    -- Total field goal attempts
    SUM(off.F_A) + SUM(off.IS_A) + SUM(off.MR_A) + SUM(off._3P_A) AS FG_A,
    
    -- Effective Field Goal as decimal float
    CASE 
        WHEN (SUM(off.F_A) + SUM(off.IS_A) + SUM(off.MR_A) + SUM(off._3P_A)) > 0 
        THEN ROUND(
            CAST(SUM(off.F_M) + SUM(off.IS_M) + SUM(off.MR_M) + 1.5 * SUM(off._3P_M) AS FLOAT) / 
            CAST(SUM(off.F_A) + SUM(off.IS_A) + SUM(off.MR_A) + SUM(off._3P_A) AS FLOAT), 
            3
        )
        ELSE 0.0 
    END AS eFG,
    
    -- Points Per Possession as float (including Free Throws)
    CASE
        WHEN SUM(off.plays) > 0 THEN 
            ROUND(
                CAST(
                    (SUM(off.F_M) * 2 + 
                     SUM(off.IS_M) * 2 + 
                     SUM(off.MR_M) * 2 + 
                     SUM(off._3P_M) * 3 +
                     SUM(off.FT_M)) AS FLOAT
                ) / 
                CAST(SUM(off.plays) AS FLOAT),
                3
            )
        ELSE 0.0
    END AS PPP,
    
    -- Raw sums
    SUM(off.F_M) AS F_M,
    SUM(off.F_A) AS F_A,
    SUM(off.IS_M) AS IS_M,
    SUM(off.IS_A) AS IS_A,
    SUM(off.MR_M) AS MR_M,
    SUM(off.MR_A) AS MR_A,
    SUM(off._3P_M) AS _3P_M,
    SUM(off._3P_A) AS _3P_A,
    SUM(off.TOV) AS TOV,
    
    -- Field Goal Percentage as decimal float
    CASE 
        WHEN SUM(off.F_A) > 0 THEN ROUND(CAST(SUM(off.F_M) AS FLOAT) / CAST(SUM(off.F_A) AS FLOAT), 3)
        ELSE 0.0 
    END AS F_P,
    
    -- Inside Shot Percentage as decimal float
    CASE 
        WHEN SUM(off.IS_A) > 0 THEN ROUND(CAST(SUM(off.IS_M) AS FLOAT) / CAST(SUM(off.IS_A) AS FLOAT), 3)
        ELSE 0.0 
    END AS IS_P,
    
    -- Mid-Range Shot Percentage as decimal float
    CASE 
        WHEN SUM(off.MR_A) > 0 THEN ROUND(CAST(SUM(off.MR_M) AS FLOAT) / CAST(SUM(off.MR_A) AS FLOAT), 3)
        ELSE 0.0 
    END AS MR_P,
    
    -- Three-Point Shot Percentage as decimal float
    CASE 
        WHEN SUM(off._3P_A) > 0 THEN ROUND(CAST(SUM(off._3P_M) AS FLOAT) / CAST(SUM(off._3P_A) AS FLOAT), 3)
        ELSE 0.0 
    END AS _3P_P,
    
    -- Turnover Percentage as decimal float
    CASE 
        WHEN SUM(off.plays) > 0 THEN ROUND(CAST(SUM(off.TOV) AS FLOAT) / CAST(SUM(off.plays) AS FLOAT), 3)
        ELSE 0.0 
    END AS TOV_P

FROM offense_stats off
JOIN games g ON g.game_id = off.game_id
CROSS JOIN total_plays_all
WHERE off.team_id = 533 
  AND g.season_id = 2046 
  AND g.game_type IN ('Non-Conference','Conference','Playoff','Tournament')
GROUP BY off.defense_type, total_plays_all.grand_total_plays
ORDER BY plays desc