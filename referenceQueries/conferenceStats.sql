SELECT
    t.team_name,
    team_stats.*,
    opp_stats.PTS AS O_PTS,
    opp_stats.ORTG AS DRtg,
    opp_stats.efg_P AS O_eFG_P,
    opp_stats.TO_P AS O_TO_P,
    opp_stats.FT_FG_A AS O_FT_FG_A
FROM team_avg team_stats
JOIN teams t ON t.team_id = team_stats.team_id
JOIN team_avg opp_stats
    ON team_stats.team_id = opp_stats.team_id
    AND opp_stats.stat_type = 'opponent'
    AND opp_stats.season_id = team_stats.season_id
    AND opp_stats.game_type = team_stats.game_type
    AND opp_stats.conference_id = team_stats.conference_id
WHERE team_stats.conference_id = ?
  AND team_stats.season_id = ?
  AND team_stats.game_type = 'Conference'
  AND team_stats.stat_type = 'team'
ORDER BY team_stats.GW DESC;
