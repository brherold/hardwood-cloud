SELECT 
    g.game_id,
    ROUND(SUM(pst.OBPM * pst.Min) / NULLIF(SUM(pst.Min), 0), 2) as cumulative_OBPM,
    ROUND(SUM(pst.DBPM * pst.Min) / NULLIF(SUM(pst.Min), 0), 2) as cumulative_DBPM,
    ROUND(SUM(pst.BPM * pst.Min) / NULLIF(SUM(pst.Min), 0), 2) as cumulative_BPM,
    ROUND(SUM(pst.OEPM * pst.Min) / NULLIF(SUM(pst.Min), 0), 2) as cumulative_OEPM,
    ROUND(SUM(pst.DEPM * pst.Min) / NULLIF(SUM(pst.Min), 0), 2) as cumulative_DEPM,
    ROUND(SUM(pst.EPM * pst.Min) / NULLIF(SUM(pst.Min), 0), 2) as cumulative_EPM,
    tst.outcome as team_outcome,
    ROUND((tst.PTS/tst.Poss) * 100, 2) as ORtg,
    -- Opponent stats (using subquery)
    ROUND((SELECT (opponent_tst.PTS/opponent_tst.Poss) * 100 
     FROM team_stats opponent_tst 
     WHERE opponent_tst.game_id = g.game_id AND opponent_tst.team_id != t.team_id
     LIMIT 1), 2) as DRtg,
    -- NET Rating calculation
    ROUND(((tst.PTS/tst.Poss) * 100) - 
    (SELECT (opponent_tst.PTS/opponent_tst.Poss) * 100 
     FROM team_stats opponent_tst 
     WHERE opponent_tst.game_id = g.game_id AND opponent_tst.team_id != t.team_id
     LIMIT 1), 2) as NETRtg
FROM games g
JOIN team_stats tst ON tst.game_id = g.game_id
JOIN teams t ON t.team_id = tst.team_id
JOIN players p ON p.team_id = t.team_id
JOIN player_stats pst ON pst.player_id = p.player_id AND pst.game_id = g.game_id
GROUP BY g.game_id, t.team_name, t.team_id, tst.outcome, tst.PTS, tst.Poss
ORDER BY g.game_id, t.team_id;