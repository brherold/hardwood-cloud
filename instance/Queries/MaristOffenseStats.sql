WITH total_plays_all AS (
    SELECT 
        g.season_id,
        SUM(off.plays) AS grand_total_plays
    FROM offense_stats off
    JOIN games g ON g.game_id = off.game_id
    WHERE off.team_id = 252
      AND g.season_id IN (2044, 2045, 2046, 2047)
      AND g.game_type IN ('Non-Conference','Conference','Playoff','Tournament')
    GROUP BY g.season_id
)
SELECT 
    g.season_id,
    off.defense_type,

    COUNT(CASE WHEN off.plays >= 1 THEN 1 END) AS Games_Used,
    SUM(off.plays) AS plays,

    -- Play percentage (within season)
    ROUND(
        CAST(SUM(off.plays) AS FLOAT) /
        CAST(tpa.grand_total_plays AS FLOAT),
        3
    ) AS plays_pct,

    -- Total FG attempts
    SUM(off.F_A) + SUM(off.IS_A) + SUM(off.MR_A) + SUM(off._3P_A) AS FG_A,

    -- eFG%
    CASE 
        WHEN (SUM(off.F_A) + SUM(off.IS_A) + SUM(off.MR_A) + SUM(off._3P_A)) > 0 
        THEN ROUND(
            CAST(
                SUM(off.F_M) + SUM(off.IS_M) + SUM(off.MR_M) + 1.5 * SUM(off._3P_M)
            AS FLOAT) /
            CAST(
                SUM(off.F_A) + SUM(off.IS_A) + SUM(off.MR_A) + SUM(off._3P_A)
            AS FLOAT),
            3
        )
        ELSE 0.0 
    END AS eFG,

    -- PPP (including Free Throws)
    CASE
        WHEN SUM(off.plays) > 0 THEN 
            ROUND(
                CAST(
                    SUM(off.F_M) * 2 +
                    SUM(off.IS_M) * 2 +
                    SUM(off.MR_M) * 2 +
                    SUM(off._3P_M) * 3 +
                    SUM(off.FT_M)
                AS FLOAT) /
                CAST(SUM(off.plays) AS FLOAT),
                3
            )
        ELSE 0.0
    END AS PPP,

    -- Raw totals
    SUM(off.F_M) AS F_M,
    SUM(off.F_A) AS F_A,
    SUM(off.IS_M) AS IS_M,
    SUM(off.IS_A) AS IS_A,
    SUM(off.MR_M) AS MR_M,
    SUM(off.MR_A) AS MR_A,
    SUM(off._3P_M) AS _3P_M,
    SUM(off._3P_A) AS _3P_A,
    SUM(off.TOV) AS TOV,

    -- Attempt rates
    ROUND(1.0 * SUM(off.F_A) /
        (SUM(off.F_A) + SUM(off.IS_A) + SUM(off.MR_A) + SUM(off._3P_A)), 3) AS FAr,

    ROUND(1.0 * SUM(off.IS_A) /
        (SUM(off.F_A) + SUM(off.IS_A) + SUM(off.MR_A) + SUM(off._3P_A)), 3) AS ISAr,

    ROUND(1.0 * (SUM(off.F_A) + SUM(off.IS_A)) /
        (SUM(off.F_A) + SUM(off.IS_A) + SUM(off.MR_A) + SUM(off._3P_A)), 3) AS PaintAr,

    ROUND(1.0 * SUM(off.MR_A) /
        (SUM(off.F_A) + SUM(off.IS_A) + SUM(off.MR_A) + SUM(off._3P_A)), 3) AS MRAr,

    ROUND(1.0 * SUM(off._3P_A) /
        (SUM(off.F_A) + SUM(off.IS_A) + SUM(off.MR_A) + SUM(off._3P_A)), 3) AS _3PAr,

    -- Percentages
    CASE WHEN SUM(off.F_A) > 0
        THEN ROUND(1.0 * SUM(off.F_M) / SUM(off.F_A), 3)
        ELSE 0.0 END AS F_P,

    CASE WHEN SUM(off.IS_A) > 0
        THEN ROUND(1.0 * SUM(off.IS_M) / SUM(off.IS_A), 3)
        ELSE 0.0 END AS IS_P,

    CASE WHEN SUM(off.F_A) + SUM(off.IS_A) > 0
        THEN ROUND(
            1.0 * (SUM(off.F_M) + SUM(off.IS_M)) /
            (SUM(off.F_A) + SUM(off.IS_A)),
            3
        )
        ELSE 0.0 END AS Paint_P,

    CASE WHEN SUM(off.MR_A) > 0
        THEN ROUND(1.0 * SUM(off.MR_M) / SUM(off.MR_A), 3)
        ELSE 0.0 END AS MR_P,

    CASE WHEN SUM(off._3P_A) > 0
        THEN ROUND(1.0 * SUM(off._3P_M) / SUM(off._3P_A), 3)
        ELSE 0.0 END AS _3P_P,

    CASE WHEN SUM(off.plays) > 0
        THEN ROUND(1.0 * SUM(off.TOV) / SUM(off.plays), 3)
        ELSE 0.0 END AS TOV_P

FROM offense_stats off
JOIN games g 
    ON g.game_id = off.game_id
JOIN total_plays_all tpa
    ON tpa.season_id = g.season_id
WHERE off.team_id = 252
  AND g.season_id IN (2044, 2045, 2046, 2047)
  AND g.game_type IN ('Non-Conference','Conference','Playoff','Tournament')
GROUP BY 
    g.season_id,
    off.defense_type,
    tpa.grand_total_plays
ORDER BY 
    g.season_id,
    plays DESC;
