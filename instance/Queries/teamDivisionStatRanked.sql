WITH context AS (
    SELECT DISTINCT season_id, game_type, stat_type, conference_id,
        CASE 
            WHEN conference_id <= 15 THEN 'low'
            WHEN conference_id <= 31 THEN 'mid'
            ELSE 'high'
        END AS conf_group
    FROM team_avg
    WHERE team_id = 533
      AND season_id = 2045
      AND game_type = 'College'
      AND stat_type = 'team'
),
ranked AS (
    SELECT 
        t.team_id,

        -- Playing time
        RANK() OVER (PARTITION BY conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.GW DESC) AS GW_rank,
        RANK() OVER (PARTITION BY conf_group, t.season_id, t.game_type, t.stat_type ORDER BY (t.GP - t.GW) ASC) AS GL_rank,
        RANK() OVER (PARTITION BY conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.Min DESC) AS Min_rank,

        -- Scoring
        RANK() OVER (PARTITION BY conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.PTS DESC) AS PTS_rank,
        RANK() OVER (PARTITION BY conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.FG_M DESC) AS FG_M_rank,
        RANK() OVER (PARTITION BY conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.eFG_P DESC) AS eFG_P_rank,
        RANK() OVER (PARTITION BY conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t._3P_M DESC) AS _3P_M_rank,
        RANK() OVER (PARTITION BY conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t._3P_P DESC) AS _3P_P_rank,
        RANK() OVER (PARTITION BY conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t._2P_M DESC) AS _2P_M_rank,
        RANK() OVER (PARTITION BY conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t._2P_P DESC) AS _2P_P_rank,
        RANK() OVER (PARTITION BY conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.FT_M DESC) AS FT_M_rank,
        RANK() OVER (PARTITION BY conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.FT_P DESC) AS FT_P_rank,

        -- Efficiency
        RANK() OVER (PARTITION BY conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.PLUS DESC) AS PLUS_rank,
        RANK() OVER (PARTITION BY conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.PITP DESC) AS PITP_rank,
        RANK() OVER (PARTITION BY conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.FBP DESC) AS FBP_rank,

        -- Rebounding
        RANK() OVER (PARTITION BY conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.Off DESC) AS Off_rank,
        RANK() OVER (PARTITION BY conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.Def DESC) AS Def_rank,
        RANK() OVER (PARTITION BY conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.Rebs DESC) AS Rebs_rank,

        -- Playmaking
        RANK() OVER (PARTITION BY conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.AST DESC) AS AST_rank,
        RANK() OVER (PARTITION BY conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.STL DESC) AS STL_rank,

        -- Defense
        RANK() OVER (PARTITION BY conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.BLK DESC) AS BLK_rank,
        RANK() OVER (PARTITION BY conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.FD DESC) AS FD_rank,

        -- Attempts
        RANK() OVER (PARTITION BY conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.FG_A DESC) AS FG_A_rank,
        RANK() OVER (PARTITION BY conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t._3P_A DESC) AS _3P_A_rank,
        RANK() OVER (PARTITION BY conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t._2P_A DESC) AS _2P_A_rank,
        RANK() OVER (PARTITION BY conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.FT_A DESC) AS FT_A_rank,

        -- Negative stats (lower is better)
        RANK() OVER (PARTITION BY conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t."TO" ASC) AS TO_rank,
        RANK() OVER (PARTITION BY conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.PF ASC) AS PF_rank,

        -- Neutral stats
        RANK() OVER (PARTITION BY conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.DIST DESC) AS DIST_rank,
        RANK() OVER (PARTITION BY conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.Poss DESC) AS Poss_rank,
        RANK() OVER (PARTITION BY conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t._3PAr DESC) AS _3PAr_rank,
        RANK() OVER (PARTITION BY conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.FTr DESC) AS FTr_rank

    FROM team_avg t
    JOIN context c
      ON t.season_id = c.season_id
     AND t.game_type = c.game_type
     AND t.stat_type = c.stat_type
     AND (
        (c.conf_group = 'low' AND t.conference_id <= 15) OR
        (c.conf_group = 'mid' AND t.conference_id BETWEEN 16 AND 31) OR
        (c.conf_group = 'high' AND t.conference_id >= 32)
     )
)
SELECT *
FROM ranked
WHERE team_id = 533;
