SELECT 
    g.game_type,
    g.game_date,

    -- Home team info
    h.team_id AS home_team_id,
    ht.team_name AS home_team_name,
    h.Min AS home_Min,
    h.PTS AS home_PTS,
    h.FG_M AS home_FG_M,
    h.FG_A AS home_FG_A,
    h.eFG_P AS home_eFG_P,
    h._3P_M AS home_3P_M,
    h._3P_A AS home_3P_A,
    h._3P_P AS home_3P_P,
    h._2P_M AS home_2P_M,
    h._2P_A AS home_2P_A,
    h._2P_P AS home_2P_P,
    h.FT_M AS home_FT_M,
    h.FT_A AS home_FT_A,
    h.FT_P AS home_FT_P,
    h.Off AS home_Off,
    h.Def AS home_Def,
    h.Rebs AS home_Rebs,
    h.AST AS home_AST,
    h.STL AS home_STL,
    h.BLK AS home_BLK,
    h."TO" AS home_TO,
    h.PF AS home_PF,
    h.PLUS AS home_PLUS,
    h.DIST AS home_DIST,
    h.PITP AS home_PITP,
    h.FBP AS home_FBP,
    h.FD AS home_FD,
    h.Fat AS home_Fat,
    h.F_M AS home_F_M,
    h.F_A AS home_F_A,
    h.F_P AS home_F_P,
    h.IS_M AS home_IS_M,
    h.IS_A AS home_IS_A,
    h.IS_P AS home_IS_P,
    h.MR_M AS home_MR_M,
    h.MR_A AS home_MR_A,
    h.MR_P AS home_MR_P,
    h.Poss AS home_Poss,

    -- Away team info
    a.team_id AS away_team_id,
    at.team_name AS away_team_name,
    a.Min AS away_Min,
    a.PTS AS away_PTS,
    a.FG_M AS away_FG_M,
    a.FG_A AS away_FG_A,
    a.eFG_P AS away_eFG_P,
    a._3P_M AS away_3P_M,
    a._3P_A AS away_3P_A,
    a._3P_P AS away_3P_P,
    a._2P_M AS away_2P_M,
    a._2P_A AS away_2P_A,
    a._2P_P AS away_2P_P,
    a.FT_M AS away_FT_M,
    a.FT_A AS away_FT_A,
    a.FT_P AS away_FT_P,
    a.Off AS away_Off,
    a.Def AS away_Def,
    a.Rebs AS away_Rebs,
    a.AST AS away_AST,
    a.STL AS away_STL,
    a.BLK AS away_BLK,
    a."TO" AS away_TO,
    a.PF AS away_PF,
    a.PLUS AS away_PLUS,
    a.DIST AS away_DIST,
    a.PITP AS away_PITP,
    a.FBP AS away_FBP,
    a.FD AS away_FD,
    a.Fat AS away_Fat,
    a.F_M AS away_F_M,
    a.F_A AS away_F_A,
    a.F_P AS away_F_P,
    a.IS_M AS away_IS_M,
    a.IS_A AS away_IS_A,
    a.IS_P AS away_IS_P,
    a.MR_M AS away_MR_M,
    a.MR_A AS away_MR_A,
    a.MR_P AS away_MR_P,
    a.Poss AS away_Poss,

    -- Determine the location of the team
    CASE 
        WHEN tst.team_id = g.home_team_id THEN 'Home'
        ELSE 'Away'
    END AS team_location,


    -- Determine the opponent team info
    CASE 
        WHEN tst.team_id = g.home_team_id THEN g.away_team_id
        ELSE g.home_team_id
    END AS opponent_id,

    CASE 
        WHEN tst.team_id = g.home_team_id THEN at.team_name
        ELSE ht.team_name
    END AS opponent_name

FROM games g
JOIN team_stats h ON h.game_id = g.game_id AND h.team_id = g.home_team_id
JOIN team_stats a ON a.game_id = g.game_id AND a.team_id = g.away_team_id
LEFT JOIN teams ht ON ht.team_id = h.team_id
LEFT JOIN teams at ON at.team_id = a.team_id
LEFT JOIN team_stats tst ON tst.game_id = g.game_id AND tst.team_id = 533 -- For the team you're interested in

WHERE g.season_id = 2045 AND tst.team_id = 533
ORDER BY g.game_date;
