WITH context AS (
    SELECT DISTINCT season_id, game_type, stat_type, conference_id,
        CASE 
            WHEN conference_id <= 15 THEN 'low'
            WHEN conference_id <= 31 THEN 'mid'
            ELSE 'high'
        END AS conf_group
    FROM team_avg
    WHERE team_id = ?
      AND season_id = ?
      AND game_type = ?
      AND stat_type = 'team'
),
ranked AS (
    SELECT 
        t.team_id,

        -- Playing time
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.GW DESC) AS GW,
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY (t.GP - t.GW) ASC) AS GL,
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.Min DESC) AS Min,
        
        -- Scoring
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.PTS DESC) AS PTS,
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.FG_M DESC) AS FG_M,
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.eFG_P DESC) AS eFG_P,
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t._3P_M DESC) AS _3P_M,
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t._3P_P DESC) AS _3P_P,
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t._2P_M DESC) AS _2P_M,
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t._2P_P DESC) AS _2P_P,
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.FT_M DESC) AS FT_M,
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.FT_P DESC) AS FT_P,
        
        -- Efficiency
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.PLUS DESC) AS PLUS,
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.PITP DESC) AS PITP,
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.FBP DESC) AS FBP,
        
        -- Rebounding
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.Off DESC) AS Off,
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.Def DESC) AS Def,
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.Rebs DESC) AS Rebs,
        
        -- Playmaking
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.AST DESC) AS AST,
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.STL DESC) AS STL,
        
        -- Defense
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.BLK DESC) AS BLK,
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.FD DESC) AS FD,
        
        -- Attempts
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.FG_A DESC) AS FG_A,
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t._3P_A DESC) AS _3P_A,
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t._2P_A DESC) AS _2P_A,
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.FT_A DESC) AS FT_A,
        
        -- Negative stats (lower is better)
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t."TO" ASC) AS "TO",
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.PF ASC) AS PF,
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.TO_P ASC) AS TO_P,
        
        -- Neutral stats
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.DIST DESC) AS DIST,
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.Poss DESC) AS Poss,
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t._3PAr DESC) AS _3PAr,
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.FTr DESC) AS FTr,
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.ORtg DESC) AS ORtg,
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.NetRtg DESC) AS NetRtg,
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.FT_FG_A DESC) AS FT_FG_A,
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.ORB_P DESC) AS ORB_P,
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.DRB_P DESC) AS DRB_P,
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.SOS DESC) AS SOS,
        RANK() OVER (PARTITION BY c.conf_group, t.season_id, t.game_type, t.stat_type ORDER BY t.RPI DESC) AS RPI

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
WHERE team_id = ?;
