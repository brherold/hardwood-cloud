SELECT 
    p.team_id,
    pavg.season_id,
    SUM(pavg.OEPM * pavg.GP * pavg.Min) / SUM(pavg.GP * pavg.Min) AS OEPM,
    SUM(pavg.DEPM * pavg.GP * pavg.Min) / SUM(pavg.GP * pavg.Min) AS DEPM,
    SUM(pavg.EPM * pavg.GP * pavg.Min) / SUM(pavg.GP * pavg.Min) AS EPM,
    SUM(pavg.OBPM * pavg.GP * pavg.Min) / SUM(pavg.GP * pavg.Min) AS OBPM,
    SUM(pavg.BPM * pavg.GP * pavg.Min) / SUM(pavg.GP * pavg.Min) AS DBPM,
    SUM(pavg.BPM * pavg.GP * pavg.Min) / SUM(pavg.GP * pavg.Min) AS BPM,
    (1.0 * tavg.GW / tavg.GP) AS WP,
    tavg.NetRtg
FROM players p
JOIN player_avg pavg 
    ON pavg.player_id = p.player_id
JOIN team_avg tavg 
    ON tavg.team_id = p.team_id
    AND tavg.game_type = pavg.game_type
    AND tavg.stat_type = "team"
    AND tavg.season_id = pavg.season_id
WHERE pavg.game_type = 'College'
  AND pavg.season_id IN (2044, 2045, 2046)
GROUP BY p.team_id, pavg.season_id, tavg.GW, tavg.GP, tavg.NetRtg
ORDER BY EPM DESC;
