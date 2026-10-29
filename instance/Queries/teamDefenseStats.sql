WITH total_plays_all AS (
    SELECT SUM(plays) AS grand_total_plays
    FROM defense_stats def
    JOIN games g ON g.game_id = def.game_id
    WHERE def.team_id = 533 
      AND g.season_id = 2046 
      AND g.game_type IN ('Non-Conference','Conference','Playoff','Tournament')
)
SELECT 
    def.defense_type,
	COUNT(CASE WHEN def.plays >= 1 THEN 1 END) AS Games_Used,
    SUM(def.plays) AS plays,
    
    -- Play percentage as decimal float
    ROUND(CAST(SUM(def.plays) AS FLOAT) / CAST((SELECT grand_total_plays FROM total_plays_all) AS FLOAT), 3) AS plays_pct,
    
    -- Total field goal attempts against
    SUM(def.F_A) + SUM(def.IS_A) + SUM(def.MR_A) + SUM(def._3P_A) AS FG_A,
    
    -- Effective Field Goal allowed as decimal float
    CASE 
        WHEN (SUM(def.F_A) + SUM(def.IS_A) + SUM(def.MR_A) + SUM(def._3P_A)) > 0 
        THEN ROUND(
            CAST(SUM(def.F_M) + SUM(def.IS_M) + SUM(def.MR_M) + 1.5 * SUM(def._3P_M) AS FLOAT) / 
            CAST(SUM(def.F_A) + SUM(def.IS_A) + SUM(def.MR_A) + SUM(def._3P_A) AS FLOAT), 
            3
        )
        ELSE 0.0 
    END AS eFG,
    
    -- Points Per Possession allowed as float (including Free Throws)
    CASE
        WHEN SUM(def.plays) > 0 THEN 
            ROUND(
                CAST(
                    (SUM(def.F_M) * 2 + 
                     SUM(def.IS_M) * 2 + 
                     SUM(def.MR_M) * 2 + 
                     SUM(def._3P_M) * 3 +
                     SUM(def.FT_M)) AS FLOAT
                ) / 
                CAST(SUM(def.plays) AS FLOAT),
                3
            )
        ELSE 0.0
    END AS PPP,
	
	

    
    -- Raw defensive stats
    SUM(def.F_M) AS F_M,
    SUM(def.F_A) AS F_A,
    SUM(def.IS_M) AS IS_M,
    SUM(def.IS_A) AS IS_A,
    SUM(def.MR_M) AS MR_M,
    SUM(def.MR_A) AS MR_A,
    SUM(def._3P_M) AS _3P_M,
    SUM(def._3P_A) AS _3P_A,
    SUM(def.TOV) AS TOV,
    
    -- Field Goal Percentage allowed as decimal float
    CASE 
        WHEN SUM(def.F_A) > 0 THEN ROUND(CAST(SUM(def.F_M) AS FLOAT) / CAST(SUM(def.F_A) AS FLOAT), 3)
        ELSE 0.0 
    END AS F_P,
    
    -- Inside Shot Percentage allowed as decimal float
    CASE 
        WHEN SUM(def.IS_A) > 0 THEN ROUND(CAST(SUM(def.IS_M) AS FLOAT) / CAST(SUM(def.IS_A) AS FLOAT), 3)
        ELSE 0.0 
    END AS IS_P,
    
    -- Mid-Range Shot Percentage allowed as decimal float
    CASE 
        WHEN SUM(def.MR_A) > 0 THEN ROUND(CAST(SUM(def.MR_M) AS FLOAT) / CAST(SUM(def.MR_A) AS FLOAT), 3)
        ELSE 0.0 
    END AS MR_P,
    
    -- Three-Point Shot Percentage allowed as decimal float
    CASE 
        WHEN SUM(def._3P_A) > 0 THEN ROUND(CAST(SUM(def._3P_M) AS FLOAT) / CAST(SUM(def._3P_A) AS FLOAT), 3)
        ELSE 0.0 
    END AS _3P_P,
    
    -- Turnover Percentage forced as decimal float
    CASE 
        WHEN SUM(def.plays) > 0 THEN ROUND(CAST(SUM(def.TOV) AS FLOAT) / CAST(SUM(def.plays) AS FLOAT), 3)
        ELSE 0.0 
    END AS TOV_P

FROM defense_stats def
JOIN games g ON g.game_id = def.game_id
CROSS JOIN total_plays_all
WHERE def.team_id = 533 
  AND g.season_id = 2046 
  AND g.game_type IN ('Non-Conference','Conference','Playoff','Tournament')
GROUP BY def.defense_type, total_plays_all.grand_total_plays
ORDER BY plays desc