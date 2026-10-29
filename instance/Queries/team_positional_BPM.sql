WITH PositionDistribution AS (
    SELECT 
        p.player_id,
        p.name,
        p.team_id,
        pavg.BPM,
        pavg.Min AS total_minutes,
        pavg.GP,
        pavg.PG_Min,
        pavg.SG_Min,
        pavg.SF_Min,
        pavg.PF_Min,
        pavg.C_Min,
        pavg.PG_Min * pavg.GP AS pg_weight,
        pavg.SG_Min * pavg.GP AS sg_weight,
        pavg.SF_Min * pavg.GP AS sf_weight,
        pavg.PF_Min * pavg.GP AS pf_weight,
        pavg.C_Min * pavg.GP AS c_weight
    FROM players p
    JOIN player_avg pavg ON pavg.player_id = p.player_id
    WHERE pavg.game_type = 'College'  
      AND pavg.season_id = 2046
      AND pavg.Min > 0
),

PositionalBPM AS (
    SELECT 
        team_id,
        position,
        weighted_bpm,
        position_minutes,
        total_weight,
        contributors
    FROM (
        -- PG
        SELECT 
            team_id,
            'PG' AS position,
            SUM(BPM * pg_weight) / NULLIF(SUM(pg_weight), 0) AS weighted_bpm,
            SUM(PG_Min) AS position_minutes,
            SUM(pg_weight) AS total_weight,
            GROUP_CONCAT(name || ' (' || PG_Min || ' min)', ', ') AS contributors
        FROM PositionDistribution
        WHERE pg_weight > 0
        GROUP BY team_id
        
        UNION ALL
        
        -- SG
        SELECT 
            team_id,
            'SG' AS position,
            SUM(BPM * sg_weight) / NULLIF(SUM(sg_weight), 0) AS weighted_bpm,
            SUM(SG_Min) AS position_minutes,
            SUM(sg_weight) AS total_weight,
            GROUP_CONCAT(name || ' (' || SG_Min || ' min)', ', ') AS contributors
        FROM PositionDistribution
        WHERE sg_weight > 0
        GROUP BY team_id
        
        UNION ALL
        
        -- SF
        SELECT 
            team_id,
            'SF' AS position,
            SUM(BPM * sf_weight) / NULLIF(SUM(sf_weight), 0) AS weighted_bpm,
            SUM(SF_Min) AS position_minutes,
            SUM(sf_weight) AS total_weight,
            GROUP_CONCAT(name || ' (' || SF_Min || ' min)', ', ') AS contributors
        FROM PositionDistribution
        WHERE sf_weight > 0
        GROUP BY team_id
        
        UNION ALL
        
        -- PF
        SELECT 
            team_id,
            'PF' AS position,
            SUM(BPM * pf_weight) / NULLIF(SUM(pf_weight), 0) AS weighted_bpm,
            SUM(PF_Min) AS position_minutes,
            SUM(pf_weight) AS total_weight,
            GROUP_CONCAT(name || ' (' || PF_Min || ' min)', ', ') AS contributors
        FROM PositionDistribution
        WHERE pf_weight > 0
        GROUP BY team_id
        
        UNION ALL
        
        -- C
        SELECT 
            team_id,
            'C' AS position,
            SUM(BPM * c_weight) / NULLIF(SUM(c_weight), 0) AS weighted_bpm,
            SUM(C_Min) AS position_minutes,
            SUM(c_weight) AS total_weight,
            GROUP_CONCAT(name || ' (' || C_Min || ' min)', ', ') AS contributors
        FROM PositionDistribution
        WHERE c_weight > 0
        GROUP BY team_id
    ) pos
),

TeamTotals AS (
    SELECT 
        team_id,
        SUM(position_minutes) AS total_minutes
    FROM PositionalBPM
    GROUP BY team_id
)

SELECT 
    season_id,
    t.team_id,
    
    -- PG metrics
    MAX(CASE WHEN pb.position = 'PG' THEN pb.weighted_bpm END) AS pg_bpm,
    MAX(CASE WHEN pb.position = 'PG' THEN ROUND(pb.position_minutes * 100.0 / NULLIF(tt.total_minutes, 0), 1) END) AS pg_min_pct,
    
    -- SG metrics
    MAX(CASE WHEN pb.position = 'SG' THEN pb.weighted_bpm END) AS sg_bpm,
    MAX(CASE WHEN pb.position = 'SG' THEN ROUND(pb.position_minutes * 100.0 / NULLIF(tt.total_minutes, 0), 1) END) AS sg_min_pct,
    
    -- SF metrics
    MAX(CASE WHEN pb.position = 'SF' THEN pb.weighted_bpm END) AS sf_bpm,
    MAX(CASE WHEN pb.position = 'SF' THEN ROUND(pb.position_minutes * 100.0 / NULLIF(tt.total_minutes, 0), 1) END) AS sf_min_pct,
    
    -- PF metrics
    MAX(CASE WHEN pb.position = 'PF' THEN pb.weighted_bpm END) AS pf_bpm,
    MAX(CASE WHEN pb.position = 'PF' THEN ROUND(pb.position_minutes * 100.0 / NULLIF(tt.total_minutes, 0), 1) END) AS pf_min_pct,
    
    -- C metrics
    MAX(CASE WHEN pb.position = 'C' THEN pb.weighted_bpm END) AS c_bpm,
    MAX(CASE WHEN pb.position = 'C' THEN ROUND(pb.position_minutes * 100.0 / NULLIF(tt.total_minutes, 0), 1) END) AS c_min_pct,
    
    -- Overall team metrics
    SUM(pb.weighted_bpm * pb.position_minutes) / NULLIF(SUM(pb.position_minutes), 0) AS overall_weighted_bpm,
    
    1.0 * t.GW / t.GP AS WP,
    t.NetRtg,
    t.BPM
    
FROM team_avg t
LEFT JOIN PositionalBPM pb ON pb.team_id = t.team_id
LEFT JOIN TeamTotals tt ON tt.team_id = t.team_id
WHERE t.game_type = 'College'
  AND t.stat_type = "team"
  AND t.season_id = 2046
GROUP BY t.team_id, t.GW, t.GP, t.NetRtg
ORDER BY t.team_id;