SELECT 
    def.defense_type, 
    
    -- Turnover Percentage
    ROUND(1.0 * SUM(def.TOV) / NULLIF(SUM(def.plays), 0), 2) AS TOV_P,

    -- Attempt Rates (% of FGA by Distance)
    ROUND(
        1.0 * SUM(def.Rim_A) /
        NULLIF(SUM(def.Rim_A) + SUM(def.Mid_A) + SUM(def._3P_A), 0),
    2) AS RIM_AR,

    ROUND(
        1.0 * SUM(def.Mid_A) /
        NULLIF(SUM(def.Rim_A) + SUM(def.Mid_A) + SUM(def._3P_A), 0),
    2) AS MID_AR,

    ROUND(
        1.0 * SUM(def._3P_A) /
        NULLIF(SUM(def.Rim_A) + SUM(def.Mid_A) + SUM(def._3P_A), 0),
    2) AS _3P_AR,

    -- Points Per Shot (PPS) by Distance
    ROUND(
        2.0 * SUM(def.Rim_M) / NULLIF(SUM(def.Rim_A), 0), 
    2) AS RIM_PPS,

    ROUND(
        2.0 * SUM(def.Mid_M) / NULLIF(SUM(def.Mid_A), 0), 
    2) AS MID_PPS,

    ROUND(
        3.0 * SUM(def._3P_M) / NULLIF(SUM(def._3P_A), 0), 
    2) AS _3P_PPS,

    -- Driving Metrics
    ROUND(
        1.0 * SUM(def.DR_A) / NULLIF(SUM(def.plays), 0),
    2) AS DRV_RATE,

    ROUND(
        1.0 * SUM(def.DR_M) / NULLIF(SUM(def.DR_A), 0), 
    2) AS DRV_SUCC_P,

    -- Free Throw Rate (FTA / FGA)
    ROUND(
        1.0 * SUM(def.FT_A) /
        NULLIF(SUM(def.Rim_A) + SUM(def.Mid_A) + SUM(def._3P_A), 0),
    2) AS FTR,

    -- Effective Field Goal Percentage Allowed
    ROUND(
        1.0 * (
            SUM(def.Rim_M) + 
            SUM(def.Mid_M) + 
            1.5 * SUM(def._3P_M)
        ) / NULLIF(
            SUM(def.Rim_A) + 
            SUM(def.Mid_A) + 
            SUM(def._3P_A), 0
        ), 
    2) AS eFG,

    -- Points Per Possession Allowed (including Free Throws)
    ROUND(
        1.0 * (
            SUM(def.Rim_M) * 2 + 
            SUM(def.Mid_M) * 2 + 
            SUM(def._3P_M) * 3 + 
            SUM(def.FT_M)
        ) / NULLIF(SUM(def.plays), 0), 
    2) AS PPP

FROM defense_stats def
JOIN games g 
    ON g.game_id = def.game_id

-- Join offensive teams whose PG played >= 25 mins and has Pass < 10
JOIN (
    SELECT DISTINCT 
        ps.game_id, 
        p.team_id
    FROM player_stats ps
    JOIN players p 
        ON p.player_id = ps.player_id
    JOIN games g_sub 
        ON g_sub.game_id = ps.game_id
    JOIN players_skills psk 
        ON psk.player_id = ps.player_id 
        AND psk.season_id = g_sub.season_id
    WHERE ps.SF_Min >= 25
      AND psk.Pass <= 5
) off_pg
    ON off_pg.game_id = def.game_id
    AND off_pg.team_id = (CASE WHEN g.home_team_id = def.team_id THEN g.away_team_id ELSE g.home_team_id END)

GROUP BY def.defense_type;