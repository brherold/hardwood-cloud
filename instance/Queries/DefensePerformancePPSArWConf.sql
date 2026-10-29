SELECT 
    def.defense_type, 
    
    -- Turnover Percentage
    ROUND(1.0 * SUM(def.TOV) / NULLIF(SUM(def.plays), 0), 2) AS TOV_P,

    -- Attempt Rates
    ROUND(
        1.0 * (SUM(def.F_A) + SUM(def.IS_A)) /
        NULLIF(SUM(def.F_A) + SUM(def.IS_A) + SUM(def.MR_A) + SUM(def._3P_A), 0),
    2) AS PAINT_AR,

    ROUND(
        1.0 * SUM(def.MR_A) /
        NULLIF(SUM(def.F_A) + SUM(def.IS_A) + SUM(def.MR_A) + SUM(def._3P_A), 0),
    2) AS MR_AR,

    ROUND(
        1.0 * SUM(def._3P_A) /
        NULLIF(SUM(def.F_A) + SUM(def.IS_A) + SUM(def.MR_A) + SUM(def._3P_A), 0),
    2) AS _3P_AR,

    -- Paint PPS
    2 * ROUND(
        1.0 * (SUM(def.F_M) + SUM(def.IS_M)) 
        / NULLIF(SUM(def.F_A) + SUM(def.IS_A), 0), 
    2) AS PAINT_PPS,

    -- Mid-Range PPS
    2 * ROUND(
        1.0 * SUM(def.MR_M) / NULLIF(SUM(def.MR_A), 0), 
    2) AS MR_PPS,

    -- 3-Point PPS
    3 * ROUND(
        1.0 * SUM(def._3P_M) / NULLIF(SUM(def._3P_A), 0), 
    2) AS _3P_PPS,

    -- Effective Field Goal Percentage
    ROUND(
        1.0 * (
            SUM(def.F_M) + 
            SUM(def.IS_M) + 
            SUM(def.MR_M) + 
            1.5 * SUM(def._3P_M)
        ) / NULLIF(
            SUM(def.F_A) + 
            SUM(def.IS_A) + 
            SUM(def.MR_A) + 
            SUM(def._3P_A), 0
        ), 
    2) AS eFG,

    -- Points Per Possession Allowed (including Free Throws)
    ROUND(
        1.0 * (
            SUM(def.F_M) * 2 + 
            SUM(def.IS_M) * 2 + 
            SUM(def.MR_M) * 2 + 
            SUM(def._3P_M) * 3 +
            SUM(def.FT_M)
        ) / NULLIF(SUM(def.plays), 0), 
    2) AS PPP

FROM defense_stats def
JOIN games g 
    ON g.game_id = def.game_id
JOIN team_avg tavg 
	ON tavg.team_id = def.team_id and g.season_id = tavg.season_id and tavg.stat_type = "team" and tavg.game_type = "Conference" and tavg.conference_id = 1
WHERE g.season_id = 2051

GROUP BY def.defense_type;