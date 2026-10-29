SELECT 
    g.game_type,
    g.game_date,

    -- Team info (original column names)
    CASE 
        WHEN tst.team_id = g.home_team_id THEN g.home_team_id
        ELSE g.away_team_id
    END AS team_id,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN ht.team_name
        ELSE at.team_name
    END AS team_name,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN 'Home'
        ELSE 'Away'
    END AS team_location,
	
    CASE 
        WHEN tst.team_id = g.home_team_id THEN h.outcome
        ELSE a.outcome
    END AS outcome,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN h.Min
        ELSE a.Min
    END AS Min,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN h.PTS
        ELSE a.PTS
    END AS PTS,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN h.FG_M
        ELSE a.FG_M
    END AS FG_M,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN h.FG_A
        ELSE a.FG_A
    END AS FG_A,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN h.eFG_P
        ELSE a.eFG_P
    END AS eFG_P,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN h._3P_M
        ELSE a._3P_M
    END AS _3P_M,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN h._3P_A
        ELSE a._3P_A
    END AS _3P_A,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN h._3P_P
        ELSE a._3P_P
    END AS _3P_P,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN h._2P_M
        ELSE a._2P_M
    END AS _2P_M,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN h._2P_A
        ELSE a._2P_A
    END AS _2P_A,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN h._2P_P
        ELSE a._2P_P
    END AS _2P_P,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN h.FT_M
        ELSE a.FT_M
    END AS FT_M,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN h.FT_A
        ELSE a.FT_A
    END AS FT_A,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN h.FT_P
        ELSE a.FT_P
    END AS FT_P,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN h.Off
        ELSE a.Off
    END AS Off,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN h.Def
        ELSE a.Def
    END AS Def,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN h.Rebs
        ELSE a.Rebs
    END AS Rebs,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN h.AST
        ELSE a.AST
    END AS AST,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN h.STL
        ELSE a.STL
    END AS STL,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN h.BLK
        ELSE a.BLK
    END AS BLK,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN h."TO"
        ELSE a."TO"
    END AS "TO",
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN h.PF
        ELSE a.PF
    END AS PF,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN h.PLUS
        ELSE a.PLUS
    END AS PLUS,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN h.DIST
        ELSE a.DIST
    END AS DIST,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN h.PITP
        ELSE a.PITP
    END AS PITP,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN h.FBP
        ELSE a.FBP
    END AS FBP,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN h.FD
        ELSE a.FD
    END AS FD,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN h.Poss
        ELSE a.Poss
    END AS Poss,

    -- Opponent info (with O_ prefix)
    CASE 
        WHEN tst.team_id = g.home_team_id THEN g.away_team_id
        ELSE g.home_team_id
    END AS opp_id,
    
    CASE
        WHEN tst.team_id = g.home_team_id THEN at.team_name
        ELSE ht.team_name
    END AS opp_name,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN a.Min
        ELSE h.Min
    END AS O_Min,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN a.PTS
        ELSE h.PTS
    END AS O_PTS,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN a.FG_M
        ELSE h.FG_M
    END AS O_FG_M,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN a.FG_A
        ELSE h.FG_A
    END AS O_FG_A,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN a.eFG_P
        ELSE h.eFG_P
    END AS O_eFG_P,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN a._3P_M
        ELSE h._3P_M
    END AS O_3P_M,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN a._3P_A
        ELSE h._3P_A
    END AS O_3P_A,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN a._3P_P
        ELSE h._3P_P
    END AS O_3P_P,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN a._2P_M
        ELSE h._2P_M
    END AS O_2P_M,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN a._2P_A
        ELSE h._2P_A
    END AS O_2P_A,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN a._2P_P
        ELSE h._2P_P
    END AS O_2P_P,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN a.FT_M
        ELSE h.FT_M
    END AS O_FT_M,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN a.FT_A
        ELSE h.FT_A
    END AS O_FT_A,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN a.FT_P
        ELSE h.FT_P
    END AS O_FT_P,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN a.Off
        ELSE h.Off
    END AS O_Off,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN a.Def
        ELSE h.Def
    END AS O_Def,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN a.Rebs
        ELSE h.Rebs
    END AS O_Rebs,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN a.AST
        ELSE h.AST
    END AS O_AST,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN a.STL
        ELSE h.STL
    END AS O_STL,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN a.BLK
        ELSE h.BLK
    END AS O_BLK,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN a."TO"
        ELSE h."TO"
    END AS O_TO,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN a.PF
        ELSE h.PF
    END AS O_PF,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN a.PLUS
        ELSE h.PLUS
    END AS O_PLUS,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN a.DIST
        ELSE h.DIST
    END AS O_DIST,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN a.PITP
        ELSE h.PITP
    END AS O_PITP,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN a.FBP
        ELSE h.FBP
    END AS O_FBP,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN a.FD
        ELSE h.FD
    END AS O_FD,
    
    CASE 
        WHEN tst.team_id = g.home_team_id THEN a.Poss
        ELSE h.Poss
    END AS O_Poss

FROM games g
JOIN team_stats h ON h.game_id = g.game_id AND h.team_id = g.home_team_id
JOIN team_stats a ON a.game_id = g.game_id AND a.team_id = g.away_team_id
LEFT JOIN teams ht ON ht.team_id = h.team_id
LEFT JOIN teams at ON at.team_id = a.team_id
LEFT JOIN team_stats tst ON tst.game_id = g.game_id AND tst.team_id = 533

WHERE g.season_id = 2045 AND tst.team_id = tst.team_id
ORDER BY g.game_date;