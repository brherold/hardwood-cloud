SELECT 
    team_id,
    -- Playing time (neutral ranking)
	RANK() OVER (PARTITION BY conference_id, season_id, game_type, stat_type ORDER BY GW DESC) AS GW_rank,
	RANK() OVER (PARTITION BY conference_id, season_id, game_type, stat_type ORDER BY (GP-GW) ASC) AS GL_rank,
    RANK() OVER (PARTITION BY conference_id, season_id, game_type, stat_type ORDER BY Min DESC) AS Min_rank,
    
    -- Scoring stats (higher is better)
    RANK() OVER (PARTITION BY conference_id, season_id, game_type, stat_type ORDER BY PTS DESC) AS PTS_rank,
    RANK() OVER (PARTITION BY conference_id, season_id, game_type, stat_type ORDER BY FG_M DESC) AS FG_M_rank,
    RANK() OVER (PARTITION BY conference_id, season_id, game_type, stat_type ORDER BY eFG_P DESC) AS eFG_P_rank,
    RANK() OVER (PARTITION BY conference_id, season_id, game_type, stat_type ORDER BY _3P_M DESC) AS _3P_M_rank,
    RANK() OVER (PARTITION BY conference_id, season_id, game_type, stat_type ORDER BY _3P_P DESC) AS _3P_P_rank,
    RANK() OVER (PARTITION BY conference_id, season_id, game_type, stat_type ORDER BY _2P_M DESC) AS _2P_M_rank,
    RANK() OVER (PARTITION BY conference_id, season_id, game_type, stat_type ORDER BY _2P_P DESC) AS _2P_P_rank,
    RANK() OVER (PARTITION BY conference_id, season_id, game_type, stat_type ORDER BY FT_M DESC) AS FT_M_rank,
    RANK() OVER (PARTITION BY conference_id, season_id, game_type, stat_type ORDER BY FT_P DESC) AS FT_P_rank,
    
    -- Efficiency stats (higher is better)
    RANK() OVER (PARTITION BY conference_id, season_id, game_type, stat_type ORDER BY PLUS DESC) AS PLUS_rank,
    RANK() OVER (PARTITION BY conference_id, season_id, game_type, stat_type ORDER BY PITP DESC) AS PITP_rank,
    RANK() OVER (PARTITION BY conference_id, season_id, game_type, stat_type ORDER BY FBP DESC) AS FBP_rank,
    
    -- Rebounding (higher is better)
    RANK() OVER (PARTITION BY conference_id, season_id, game_type, stat_type ORDER BY Off DESC) AS Off_rank,
    RANK() OVER (PARTITION BY conference_id, season_id, game_type, stat_type ORDER BY Def DESC) AS Def_rank,
    RANK() OVER (PARTITION BY conference_id, season_id, game_type, stat_type ORDER BY Rebs DESC) AS Rebs_rank,
    
    -- Playmaking (higher is better)
    RANK() OVER (PARTITION BY conference_id, season_id, game_type, stat_type ORDER BY AST DESC) AS AST_rank,
    RANK() OVER (PARTITION BY conference_id, season_id, game_type, stat_type ORDER BY STL DESC) AS STL_rank,
    
    -- Defense (higher is better except TO/PF)
    RANK() OVER (PARTITION BY conference_id, season_id, game_type, stat_type ORDER BY BLK DESC) AS BLK_rank,
    RANK() OVER (PARTITION BY conference_id, season_id, game_type, stat_type ORDER BY FD DESC) AS FD_rank,
	
	RANK() OVER (PARTITION BY conference_id, season_id, game_type, stat_type ORDER BY FG_A DESC) AS FG_A_rank,
    RANK() OVER (PARTITION BY conference_id, season_id, game_type, stat_type ORDER BY _3P_A DESC) AS _3P_A_rank,
    RANK() OVER (PARTITION BY conference_id, season_id, game_type, stat_type ORDER BY _2P_A DESC) AS _2P_A_rank,
    RANK() OVER (PARTITION BY conference_id, season_id, game_type, stat_type ORDER BY FT_A DESC) AS FT_A_rank,
    
    -- Negative stats (lower is better)

    RANK() OVER (PARTITION BY conference_id, season_id, game_type, stat_type ORDER BY "TO"	ASC) AS TO_rank,
    RANK() OVER (PARTITION BY conference_id, season_id, game_type, stat_type ORDER BY PF ASC) AS PF_rank,
    
    -- Neutral distance stat
    RANK() OVER (PARTITION BY conference_id, season_id, game_type, stat_type ORDER BY DIST DESC) AS DIST_rank,
	RANK() OVER (PARTITION BY conference_id, season_id, game_type, stat_type ORDER BY Poss DESC) AS Poss_rank,
	RANK() OVER (PARTITION BY conference_id, season_id, game_type, stat_type ORDER BY _3PAr DESC) AS _3PAr_rank,
		RANK() OVER (PARTITION BY conference_id, season_id, game_type, stat_type ORDER BY FTr DESC) AS FTr_rank
FROM team_avg t
WHERE conference_id = 4 
  AND season_id = 2045 
  AND game_type = 'Conference' 
  AND stat_type = 'team'
ORDER BY PTS_rank;