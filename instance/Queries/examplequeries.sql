-- Gets the player names and heights 
SELECT p.name, psk.height
FROM players p
JOIN players_skills psk on p.player_id = psk.player_id

-- Gets player names from team code 533 (that are in the DB)
SELECT p.name
FROM players p 
JOIN teams t on p.team_id = t.team_id
WHERE t.team_id = 533

-- Gets player names from team code 533 from season_id 2
SELECT p.name
FROM players p 
JOIN teams t on p.team_id = t.team_id 
JOIN games g on (g.home_team_id = t.team_id OR g.away_team_id = t.team_id)
WHERE t.team_id = 533 and g.season_id = 2

-- Gets 3p% from team_id 533 and game_id 1027313 
SELECT _3P_M * 1.0 / _3P_A  -- Multiplying by 1.0 forces floating-point division
FROM team_stats ts
WHERE game_id = 1027313 AND team_id = 533;

-- Gets IS% for player_id 205173 in season_id 2 for each game
-- Prompt: Find JJ Schwarz Inside Shooting % in 2044 (season_id = 2) for each game
SELECT ps.IS_M * 1.0 / ps.IS_A
FROM player_stats ps
JOIN games g on g.game_id = ps.game_id
WHERE g.season_id = 2 AND ps.player_id = 205173

-- Gets IS% for total season ^
SELECT SUM(ps.IS_M) * 1.0 / SUM(ps.IS_A) AS total_IS_percentage
FROM player_stats ps
JOIN games g ON g.game_id = ps.game_id
WHERE g.season_id = 2 AND ps.player_id = 205173;

--Gets Box score of all player w/ >0 minutes played w/ their height
select p.player_id, p.name, psk.height, ps.*
From players p
JOIN players_skills psk on psk.player_id = p.player_id
JOIN player_stats ps on ps.player_id = psk.player_id 
JOIN games g on g.game_id = ps.game_id
WHERE p.team_id = 533 and g.game_type = "Non-Conference" and ps.Min > 0

-- Gets 3P% of all defense types
SELECT 
    -- Zone Defense
    SUM(CASE WHEN defense_type = 'zone' THEN _3p_M ELSE 0 END) * 1.0 / 
    NULLIF(SUM(CASE WHEN defense_type = 'zone' THEN _3P_A ELSE 0 END), 0) AS zone_defense_3p_percentage,
    
    SUM(CASE WHEN defense_type = 'zone' THEN IS_M ELSE 0 END) * 1.0 / 
    NULLIF(SUM(CASE WHEN defense_type = 'zone' THEN IS_A ELSE 0 END), 0) AS zone_defense_is_percentage,

    -- Extended Zone Defense
    SUM(CASE WHEN defense_type = 'z_ext' THEN _3p_M ELSE 0 END) * 1.0 / 
    NULLIF(SUM(CASE WHEN defense_type = 'z_ext' THEN _3P_A ELSE 0 END), 0) AS z_ext_defense_3p_percentage,
    
    SUM(CASE WHEN defense_type = 'z_ext' THEN IS_M ELSE 0 END) * 1.0 / 
    NULLIF(SUM(CASE WHEN defense_type = 'z_ext' THEN IS_A ELSE 0 END), 0) AS z_ext_defense_is_percentage,

    -- Pack Line Zone Defense
    SUM(CASE WHEN defense_type = 'z_pck' THEN _3p_M ELSE 0 END) * 1.0 / 
    NULLIF(SUM(CASE WHEN defense_type = 'z_pck' THEN _3P_A ELSE 0 END), 0) AS z_pck_defense_3p_percentage,
    
    SUM(CASE WHEN defense_type = 'z_pck' THEN IS_M ELSE 0 END) * 1.0 / 
    NULLIF(SUM(CASE WHEN defense_type = 'z_pck' THEN IS_A ELSE 0 END), 0) AS z_pck_defense_is_percentage,  

    -- Man Defense
    SUM(CASE WHEN defense_type = 'man' THEN _3p_M ELSE 0 END) * 1.0 / 
    NULLIF(SUM(CASE WHEN defense_type = 'man' THEN _3P_A ELSE 0 END), 0) AS man_defense_3p_percentage,
    
    SUM(CASE WHEN defense_type = 'man' THEN IS_M ELSE 0 END) * 1.0 / 
    NULLIF(SUM(CASE WHEN defense_type = 'man' THEN IS_A ELSE 0 END), 0) AS man_defense_is_percentage,

    -- Extended Man Defense
    SUM(CASE WHEN defense_type = 'm_ext' THEN _3p_M ELSE 0 END) * 1.0 / 
    NULLIF(SUM(CASE WHEN defense_type = 'm_ext' THEN _3P_A ELSE 0 END), 0) AS m_ext_defense_3p_percentage,
    
    SUM(CASE WHEN defense_type = 'm_ext' THEN IS_M ELSE 0 END) * 1.0 / 
    NULLIF(SUM(CASE WHEN defense_type = 'm_ext' THEN IS_A ELSE 0 END), 0) AS m_ext_defense_is_percentage,

    -- Pack Line Man Defense
    SUM(CASE WHEN defense_type = 'm_pck' THEN _3p_M ELSE 0 END) * 1.0 / 
    NULLIF(SUM(CASE WHEN defense_type = 'm_pck' THEN _3P_A ELSE 0 END), 0) AS m_pck_defense_3p_percentage,
    
    SUM(CASE WHEN defense_type = 'm_pck' THEN IS_M ELSE 0 END) * 1.0 / 
    NULLIF(SUM(CASE WHEN defense_type = 'm_pck' THEN IS_A ELSE 0 END), 0) AS m_pck_defense_is_percentage,  

    -- Half-Court Defense
    SUM(CASE WHEN defense_type = 'half' THEN _3p_M ELSE 0 END) * 1.0 / 
    NULLIF(SUM(CASE WHEN defense_type = 'half' THEN _3P_A ELSE 0 END), 0) AS half_defense_3p_percentage,
    
    SUM(CASE WHEN defense_type = 'half' THEN IS_M ELSE 0 END) * 1.0 / 
    NULLIF(SUM(CASE WHEN defense_type = 'half' THEN IS_A ELSE 0 END), 0) AS half_defense_is_percentage,

    -- Transition Defense
    SUM(CASE WHEN defense_type = 'trans' THEN _3p_M ELSE 0 END) * 1.0 / 
    NULLIF(SUM(CASE WHEN defense_type = 'trans' THEN _3P_A ELSE 0 END), 0) AS trans_defense_3p_percentage,
    
    SUM(CASE WHEN defense_type = 'trans' THEN IS_M ELSE 0 END) * 1.0 / 
    NULLIF(SUM(CASE WHEN defense_type = 'trans' THEN IS_A ELSE 0 END), 0) AS trans_defense_is_percentage,

    -- Press Defense
    SUM(CASE WHEN defense_type = 'press' THEN _3p_M ELSE 0 END) * 1.0 / 
    NULLIF(SUM(CASE WHEN defense_type = 'press' THEN _3P_A ELSE 0 END), 0) AS press_defense_3p_percentage,
    
    SUM(CASE WHEN defense_type = 'press' THEN IS_M ELSE 0 END) * 1.0 / 
    NULLIF(SUM(CASE WHEN defense_type = 'press' THEN IS_A ELSE 0 END), 0) AS press_defense_is_percentage

FROM offense_stats os;


-- Gets IS% for all defense types
SELECT 
    SUM(CASE WHEN defense_type = 'half' THEN IS_M ELSE 0 END) * 1.0 / 
    SUM(CASE WHEN defense_type = 'half' THEN IS_A ELSE 0 END) AS half_defense_IS_percentage,
    
    SUM(CASE WHEN defense_type = 'zone' THEN IS_M ELSE 0 END) * 1.0 / 
    SUM(CASE WHEN defense_type = 'zone' THEN IS_A ELSE 0 END) AS zone_defense_IS_percentage,
	    
	SUM(CASE WHEN defense_type = 'man' THEN IS_M ELSE 0 END) * 1.0 / 
    SUM(CASE WHEN defense_type = 'man' THEN IS_A ELSE 0 END) AS man_defense_IS_percentage,
	
	SUM(CASE WHEN defense_type = 'trans' THEN IS_M ELSE 0 END) * 1.0 / 
    SUM(CASE WHEN defense_type = 'trans' THEN IS_A ELSE 0 END) AS trans_defense_IS_percentage,
	
	SUM(CASE WHEN defense_type = 'press' THEN IS_M ELSE 0 END) * 1.0 / 
    SUM(CASE WHEN defense_type = 'press' THEN IS_A ELSE 0 END) AS press_defense_IS_percentage
FROM offense_stats os;
