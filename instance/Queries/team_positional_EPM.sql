WITH PositionDistribution AS (
    SELECT 
        p.player_id,
        p.name,
        p.team_id,
        pavg.EPM,
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

PositionalEPM AS (
    SELECT 
        team_id,
        position,
        weighted_epm,
        position_minutes,
        total_weight,
        contributors
    FROM (
        -- PG
        SELECT 
            team_id,
            'PG' AS position,
            SUM(EPM * pg_weight) / NULLIF(SUM(pg_weight), 0) AS weighted_epm,
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
            SUM(EPM * sg_weight) / NULLIF(SUM(sg_weight), 0) AS weighted_epm,
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
            SUM(EPM * sf_weight) / NULLIF(SUM(sf_weight), 0) AS weighted_epm,
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
            SUM(EPM * pf_weight) / NULLIF(SUM(pf_weight), 0) AS weighted_epm,
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
            SUM(EPM * c_weight) / NULLIF(SUM(c_weight), 0) AS weighted_epm,
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
    FROM PositionalEPM
    GROUP BY team_id
)

SELECT 
	season_id,
    t.team_id,
    
    -- PG metrics
    MAX(CASE WHEN pe.position = 'PG' THEN pe.weighted_epm END) AS pg_epm,
    MAX(CASE WHEN pe.position = 'PG' THEN ROUND(pe.position_minutes * 100.0 / NULLIF(tt.total_minutes, 0), 1) END) AS pg_min_pct,
    
    -- SG metrics
    MAX(CASE WHEN pe.position = 'SG' THEN pe.weighted_epm END) AS sg_epm,
    MAX(CASE WHEN pe.position = 'SG' THEN ROUND(pe.position_minutes * 100.0 / NULLIF(tt.total_minutes, 0), 1) END) AS sg_min_pct,
    
    -- SF metrics
    MAX(CASE WHEN pe.position = 'SF' THEN pe.weighted_epm END) AS sf_epm,
    MAX(CASE WHEN pe.position = 'SF' THEN ROUND(pe.position_minutes * 100.0 / NULLIF(tt.total_minutes, 0), 1) END) AS sf_min_pct,
    
    -- PF metrics
    MAX(CASE WHEN pe.position = 'PF' THEN pe.weighted_epm END) AS pf_epm,
    MAX(CASE WHEN pe.position = 'PF' THEN ROUND(pe.position_minutes * 100.0 / NULLIF(tt.total_minutes, 0), 1) END) AS pf_min_pct,
    
    -- C metrics
    MAX(CASE WHEN pe.position = 'C' THEN pe.weighted_epm END) AS c_epm,
    MAX(CASE WHEN pe.position = 'C' THEN ROUND(pe.position_minutes * 100.0 / NULLIF(tt.total_minutes, 0), 1) END) AS c_min_pct,
    
    -- Overall team metrics
    SUM(pe.weighted_epm * pe.position_minutes) / NULLIF(SUM(pe.position_minutes), 0) AS overall_weighted_epm,
	
    1.0 * t.GW / t.GP AS WP,
    t.NetRtg,
	t.BPM
    
FROM team_avg t
LEFT JOIN PositionalEPM pe ON pe.team_id = t.team_id
LEFT JOIN TeamTotals tt ON tt.team_id = t.team_id
WHERE t.game_type = 'College'
  AND t.stat_type = "team"
  AND t.season_id = 2046
GROUP BY t.team_id, t.GW, t.GP, t.NetRtg
ORDER BY t.team_id ;