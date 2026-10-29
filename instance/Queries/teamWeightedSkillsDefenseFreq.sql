-- Define the season as a "variable" using a CTE
WITH params AS (
    SELECT 2046 AS season_id
),
-- 1) Player Position Distribution
PositionDistribution AS (
    SELECT 
        p.player_id,
        p.name,
        p.team_id,
        pavg.Min AS minutes,
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
        pavg.C_Min  * pavg.GP AS c_weight,
        psk.height,
        psk.weight,
        psk.wingspan,
        psk.vertical,
        psk.`IS`,
        psk.OS,
        psk.Rng,
        psk.Reb,
        psk.IDef,
        psk.PDef,
        psk.IQ,
        psk.Pass,
        psk.Hnd,
        psk.Drv,
        psk.Spd,
        psk.Sta
    FROM players p
    JOIN player_avg pavg 
        ON pavg.player_id = p.player_id
    JOIN players_skills psk 
        ON psk.player_id = p.player_id
       AND psk.season_id = pavg.season_id
    JOIN params prm
       ON prm.season_id = pavg.season_id
    WHERE pavg.game_type = 'College'
      AND pavg.Min > 0
),

-- 2) Weighted Skills per Position
WeightedSkills AS (
    SELECT team_id, 'PG' AS position, 
           SUM(height * pg_weight) / SUM(pg_weight) AS height,
           SUM(weight * pg_weight) / SUM(pg_weight) AS weight,
           SUM(wingspan * pg_weight) / SUM(pg_weight) AS wingspan,
           SUM(vertical * pg_weight) / SUM(pg_weight) AS vertical,
           SUM(`IS` * pg_weight) / SUM(pg_weight) AS `IS`,
           SUM(OS * pg_weight) / SUM(pg_weight) AS OS,
           SUM(Rng * pg_weight) / SUM(pg_weight) AS Rng,
           SUM(Reb * pg_weight) / SUM(pg_weight) AS Reb,
           SUM(IDef * pg_weight) / SUM(pg_weight) AS IDef,
           SUM(PDef * pg_weight) / SUM(pg_weight) AS PDef,
           SUM(IQ * pg_weight) / SUM(pg_weight) AS IQ,
           SUM(Pass * pg_weight) / SUM(pg_weight) AS Pass,
           SUM(Hnd * pg_weight) / SUM(pg_weight) AS Hnd,
           SUM(Drv * pg_weight) / SUM(pg_weight) AS Drv,
           SUM(Spd * pg_weight) / SUM(pg_weight) AS Spd,
           SUM(Sta * pg_weight) / SUM(pg_weight) AS Sta
    FROM PositionDistribution
    WHERE pg_weight > 0
    GROUP BY team_id
    UNION ALL
    SELECT team_id, 'SG',
           SUM(height * sg_weight) / SUM(sg_weight),
           SUM(weight * sg_weight) / SUM(sg_weight),
           SUM(wingspan * sg_weight) / SUM(sg_weight),
           SUM(vertical * sg_weight) / SUM(sg_weight),
           SUM(`IS` * sg_weight) / SUM(sg_weight),
           SUM(OS * sg_weight) / SUM(sg_weight),
           SUM(Rng * sg_weight) / SUM(sg_weight),
           SUM(Reb * sg_weight) / SUM(sg_weight),
           SUM(IDef * sg_weight) / SUM(sg_weight),
           SUM(PDef * sg_weight) / SUM(sg_weight),
           SUM(IQ * sg_weight) / SUM(sg_weight),
           SUM(Pass * sg_weight) / SUM(sg_weight),
           SUM(Hnd * sg_weight) / SUM(sg_weight),
           SUM(Drv * sg_weight) / SUM(sg_weight),
           SUM(Spd * sg_weight) / SUM(sg_weight),
           SUM(Sta * sg_weight) / SUM(sg_weight)
    FROM PositionDistribution
    WHERE sg_weight > 0
    GROUP BY team_id
    UNION ALL
    SELECT team_id, 'SF',
           SUM(height * sf_weight) / SUM(sf_weight),
           SUM(weight * sf_weight) / SUM(sf_weight),
           SUM(wingspan * sf_weight) / SUM(sf_weight),
           SUM(vertical * sf_weight) / SUM(sf_weight),
           SUM(`IS` * sf_weight) / SUM(sf_weight),
           SUM(OS * sf_weight) / SUM(sf_weight),
           SUM(Rng * sf_weight) / SUM(sf_weight),
           SUM(Reb * sf_weight) / SUM(sf_weight),
           SUM(IDef * sf_weight) / SUM(sf_weight),
           SUM(PDef * sf_weight) / SUM(sf_weight),
           SUM(IQ * sf_weight) / SUM(sf_weight),
           SUM(Pass * sf_weight) / SUM(sf_weight),
           SUM(Hnd * sf_weight) / SUM(sf_weight),
           SUM(Drv * sf_weight) / SUM(sf_weight),
           SUM(Spd * sf_weight) / SUM(sf_weight),
           SUM(Sta * sf_weight) / SUM(sf_weight)
    FROM PositionDistribution
    WHERE sf_weight > 0
    GROUP BY team_id
    UNION ALL
    SELECT team_id, 'PF',
           SUM(height * pf_weight) / SUM(pf_weight),
           SUM(weight * pf_weight) / SUM(pf_weight),
           SUM(wingspan * pf_weight) / SUM(pf_weight),
           SUM(vertical * pf_weight) / SUM(pf_weight),
           SUM(`IS` * pf_weight) / SUM(pf_weight),
           SUM(OS * pf_weight) / SUM(pf_weight),
           SUM(Rng * pf_weight) / SUM(pf_weight),
           SUM(Reb * pf_weight) / SUM(pf_weight),
           SUM(IDef * pf_weight) / SUM(pf_weight),
           SUM(PDef * pf_weight) / SUM(pf_weight),
           SUM(IQ * pf_weight) / SUM(pf_weight),
           SUM(Pass * pf_weight) / SUM(pf_weight),
           SUM(Hnd * pf_weight) / SUM(pf_weight),
           SUM(Drv * pf_weight) / SUM(pf_weight),
           SUM(Spd * pf_weight) / SUM(pf_weight),
           SUM(Sta * pf_weight) / SUM(pf_weight)
    FROM PositionDistribution
    WHERE pf_weight > 0
    GROUP BY team_id
    UNION ALL
    SELECT team_id, 'C',
           SUM(height * c_weight) / SUM(c_weight),
           SUM(weight * c_weight) / SUM(c_weight),
           SUM(wingspan * c_weight) / SUM(c_weight),
           SUM(vertical * c_weight) / SUM(c_weight),
           SUM(`IS` * c_weight) / SUM(c_weight),
           SUM(OS * c_weight) / SUM(c_weight),
           SUM(Rng * c_weight) / SUM(c_weight),
           SUM(Reb * c_weight) / SUM(c_weight),
           SUM(IDef * c_weight) / SUM(c_weight),
           SUM(PDef * c_weight) / SUM(c_weight),
           SUM(IQ * c_weight) / SUM(c_weight),
           SUM(Pass * c_weight) / SUM(c_weight),
           SUM(Hnd * c_weight) / SUM(c_weight),
           SUM(Drv * c_weight) / SUM(c_weight),
           SUM(Spd * c_weight) / SUM(c_weight),
           SUM(Sta * c_weight) / SUM(c_weight)
    FROM PositionDistribution
    WHERE c_weight > 0
    GROUP BY team_id
),

-- 3) Pivot weighted skills into one row per team
FinalTeamSkills AS (
    SELECT 
        team_id,
        -- PG
        ROUND(MAX(CASE WHEN position='PG' THEN height END),1) AS pg_height,
        ROUND(MAX(CASE WHEN position='PG' THEN weight END),1) AS pg_weight,
        ROUND(MAX(CASE WHEN position='PG' THEN wingspan END),1) AS pg_wingspan,
        ROUND(MAX(CASE WHEN position='PG' THEN vertical END),1) AS pg_vertical,
        ROUND(MAX(CASE WHEN position='PG' THEN `IS` END),1) AS pg_IS,
        ROUND(MAX(CASE WHEN position='PG' THEN OS END),1) AS pg_OS,
        ROUND(MAX(CASE WHEN position='PG' THEN Rng END),1) AS pg_Rng,
        ROUND(MAX(CASE WHEN position='PG' THEN Reb END),1) AS pg_Reb,
        ROUND(MAX(CASE WHEN position='PG' THEN IDef END),1) AS pg_IDef,
        ROUND(MAX(CASE WHEN position='PG' THEN PDef END),1) AS pg_PDef,
        ROUND(MAX(CASE WHEN position='PG' THEN IQ END),1) AS pg_IQ,
        ROUND(MAX(CASE WHEN position='PG' THEN Pass END),1) AS pg_Pass,
        ROUND(MAX(CASE WHEN position='PG' THEN Hnd END),1) AS pg_Hnd,
        ROUND(MAX(CASE WHEN position='PG' THEN Drv END),1) AS pg_Drv,
        ROUND(MAX(CASE WHEN position='PG' THEN Spd END),1) AS pg_Spd,
        ROUND(MAX(CASE WHEN position='PG' THEN Sta END),1) AS pg_Sta,
        -- SG
        ROUND(MAX(CASE WHEN position='SG' THEN height END),1) AS sg_height,
        ROUND(MAX(CASE WHEN position='SG' THEN weight END),1) AS sg_weight,
        ROUND(MAX(CASE WHEN position='SG' THEN wingspan END),1) AS sg_wingspan,
        ROUND(MAX(CASE WHEN position='SG' THEN vertical END),1) AS sg_vertical,
        ROUND(MAX(CASE WHEN position='SG' THEN `IS` END),1) AS sg_IS,
        ROUND(MAX(CASE WHEN position='SG' THEN OS END),1) AS sg_OS,
        ROUND(MAX(CASE WHEN position='SG' THEN Rng END),1) AS sg_Rng,
        ROUND(MAX(CASE WHEN position='SG' THEN Reb END),1) AS sg_Reb,
        ROUND(MAX(CASE WHEN position='SG' THEN IDef END),1) AS sg_IDef,
        ROUND(MAX(CASE WHEN position='SG' THEN PDef END),1) AS sg_PDef,
        ROUND(MAX(CASE WHEN position='SG' THEN IQ END),1) AS sg_IQ,
        ROUND(MAX(CASE WHEN position='SG' THEN Pass END),1) AS sg_Pass,
        ROUND(MAX(CASE WHEN position='SG' THEN Hnd END),1) AS sg_Hnd,
        ROUND(MAX(CASE WHEN position='SG' THEN Drv END),1) AS sg_Drv,
        ROUND(MAX(CASE WHEN position='SG' THEN Spd END),1) AS sg_Spd,
        ROUND(MAX(CASE WHEN position='SG' THEN Sta END),1) AS sg_Sta,
        -- SF
        ROUND(MAX(CASE WHEN position='SF' THEN height END),1) AS sf_height,
        ROUND(MAX(CASE WHEN position='SF' THEN weight END),1) AS sf_weight,
        ROUND(MAX(CASE WHEN position='SF' THEN wingspan END),1) AS sf_wingspan,
        ROUND(MAX(CASE WHEN position='SF' THEN vertical END),1) AS sf_vertical,
        ROUND(MAX(CASE WHEN position='SF' THEN `IS` END),1) AS sf_IS,
        ROUND(MAX(CASE WHEN position='SF' THEN OS END),1) AS sf_OS,
        ROUND(MAX(CASE WHEN position='SF' THEN Rng END),1) AS sf_Rng,
        ROUND(MAX(CASE WHEN position='SF' THEN Reb END),1) AS sf_Reb,
        ROUND(MAX(CASE WHEN position='SF' THEN IDef END),1) AS sf_IDef,
        ROUND(MAX(CASE WHEN position='SF' THEN PDef END),1) AS sf_PDef,
        ROUND(MAX(CASE WHEN position='SF' THEN IQ END),1) AS sf_IQ,
        ROUND(MAX(CASE WHEN position='SF' THEN Pass END),1) AS sf_Pass,
        ROUND(MAX(CASE WHEN position='SF' THEN Hnd END),1) AS sf_Hnd,
        ROUND(MAX(CASE WHEN position='SF' THEN Drv END),1) AS sf_Drv,
        ROUND(MAX(CASE WHEN position='SF' THEN Spd END),1) AS sf_Spd,
        ROUND(MAX(CASE WHEN position='SF' THEN Sta END),1) AS sf_Sta,
        -- PF
        ROUND(MAX(CASE WHEN position='PF' THEN height END),1) AS pf_height,
        ROUND(MAX(CASE WHEN position='PF' THEN weight END),1) AS pf_weight,
        ROUND(MAX(CASE WHEN position='PF' THEN wingspan END),1) AS pf_wingspan,
        ROUND(MAX(CASE WHEN position='PF' THEN vertical END),1) AS pf_vertical,
        ROUND(MAX(CASE WHEN position='PF' THEN `IS` END),1) AS pf_IS,
        ROUND(MAX(CASE WHEN position='PF' THEN OS END),1) AS pf_OS,
        ROUND(MAX(CASE WHEN position='PF' THEN Rng END),1) AS pf_Rng,
        ROUND(MAX(CASE WHEN position='PF' THEN Reb END),1) AS pf_Reb,
        ROUND(MAX(CASE WHEN position='PF' THEN IDef END),1) AS pf_IDef,
        ROUND(MAX(CASE WHEN position='PF' THEN PDef END),1) AS pf_PDef,
        ROUND(MAX(CASE WHEN position='PF' THEN IQ END),1) AS pf_IQ,
        ROUND(MAX(CASE WHEN position='PF' THEN Pass END),1) AS pf_Pass,
        ROUND(MAX(CASE WHEN position='PF' THEN Hnd END),1) AS pf_Hnd,
        ROUND(MAX(CASE WHEN position='PF' THEN Drv END),1) AS pf_Drv,
        ROUND(MAX(CASE WHEN position='PF' THEN Spd END),1) AS pf_Spd,
        ROUND(MAX(CASE WHEN position='PF' THEN Sta END),1) AS pf_Sta,
        -- C
        ROUND(MAX(CASE WHEN position='C' THEN height END),1) AS c_height,
        ROUND(MAX(CASE WHEN position='C' THEN weight END),1) AS c_weight,
        ROUND(MAX(CASE WHEN position='C' THEN wingspan END),1) AS c_wingspan,
        ROUND(MAX(CASE WHEN position='C' THEN vertical END),1) AS c_vertical,
        ROUND(MAX(CASE WHEN position='C' THEN `IS` END),1) AS c_IS,
        ROUND(MAX(CASE WHEN position='C' THEN OS END),1) AS c_OS,
        ROUND(MAX(CASE WHEN position='C' THEN Rng END),1) AS c_Rng,
        ROUND(MAX(CASE WHEN position='C' THEN Reb END),1) AS c_Reb,
        ROUND(MAX(CASE WHEN position='C' THEN IDef END),1) AS c_IDef,
        ROUND(MAX(CASE WHEN position='C' THEN PDef END),1) AS c_PDef,
        ROUND(MAX(CASE WHEN position='C' THEN IQ END),1) AS c_IQ,
        ROUND(MAX(CASE WHEN position='C' THEN Pass END),1) AS c_Pass,
        ROUND(MAX(CASE WHEN position='C' THEN Hnd END),1) AS c_Hnd,
        ROUND(MAX(CASE WHEN position='C' THEN Drv END),1) AS c_Drv,
        ROUND(MAX(CASE WHEN position='C' THEN Spd END),1) AS c_Spd,
        ROUND(MAX(CASE WHEN position='C' THEN Sta END),1) AS c_Sta
    FROM WeightedSkills
    GROUP BY team_id
),

-- 4) Total team plays for defense percentages
total_team_plays AS (
    SELECT 
        def.team_id,
        SUM(plays) AS team_total_plays
    FROM defense_stats def
    JOIN games g ON g.game_id = def.game_id
    JOIN params prm ON prm.season_id = g.season_id
    WHERE g.game_type IN ('Non-Conference','Conference','Playoff','Tournament')
    GROUP BY def.team_id
),

-- 5) Defense summary
DefenseSummary AS (
    SELECT 
        def.team_id,
        CASE 
            WHEN defense_type LIKE 'z_%' THEN 'zone'
            WHEN defense_type LIKE 'm_%' THEN 'man'
            ELSE defense_type
        END AS combined_defense,
        SUM(plays) AS plays
    FROM defense_stats def
    JOIN games g ON g.game_id = def.game_id
    JOIN params prm ON prm.season_id = g.season_id
    WHERE g.game_type IN ('Non-Conference','Conference','Playoff','Tournament')
    GROUP BY def.team_id, combined_defense
)

-- 6) Final combined query
SELECT 
    fts.*,
    tavg_team.*,
    -- defense percentages in one row per team
    ROUND(SUM(CASE WHEN ds.combined_defense = 'man' THEN ds.plays END) * 1.0 / tt.team_total_plays, 3) AS man_pct,
    ROUND(SUM(CASE WHEN ds.combined_defense = 'zone' THEN ds.plays END) * 1.0 / tt.team_total_plays, 3) AS zone_pct,
    ROUND(SUM(CASE WHEN ds.combined_defense = 'press' THEN ds.plays END) * 1.0 / tt.team_total_plays, 3) AS press_pct,
	tavg_opponent.ORtg as DRtg,
	tavg_opponent.F_P as O_F_P,
	tavg_opponent.IS_P as O_IS_P,
	tavg_opponent.MR_P as O_MR_P,
	tavg_opponent._2P_P as O_2P_P,
	tavg_opponent._3P_P as O_3P_P,
	tavg_opponent._3PAr as O_3PAr,
	1 - tavg_opponent._3PAr as O_2PAr,
	tavg_opponent.FTr as O_FTr,
	tavg_opponent.TO_P as O_TO_P

FROM FinalTeamSkills fts
LEFT JOIN team_avg tavg_team
    ON fts.team_id = tavg_team.team_id
    AND tavg_team.season_id = (SELECT season_id FROM params)
    AND tavg_team.stat_type = 'team'
    AND tavg_team.game_type = "College"
LEFT JOIN team_avg tavg_opponent
    ON fts.team_id = tavg_opponent.team_id
    AND tavg_opponent.season_id = (SELECT season_id FROM params)
    AND tavg_opponent.stat_type = 'opponent'
    AND tavg_opponent.game_type = "College"
LEFT JOIN DefenseSummary ds
    ON fts.team_id = ds.team_id
LEFT JOIN total_team_plays tt
    ON fts.team_id = tt.team_id
GROUP BY fts.team_id
ORDER BY fts.team_id;
