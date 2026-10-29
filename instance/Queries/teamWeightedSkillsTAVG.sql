WITH PositionDistribution AS (
    -- your existing PositionDistribution CTE
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
        psk.Reb,
        psk.IDef,
        psk.PDef,
        psk.IQ,
        psk.Spd,
        psk.Sta
    FROM players p
    JOIN player_avg pavg 
        ON pavg.player_id = p.player_id
    JOIN players_skills psk 
        ON psk.player_id = p.player_id
       AND psk.season_id = pavg.season_id
    WHERE pavg.game_type = 'College'
      AND pavg.season_id = 2046
      AND pavg.Min > 0
),
	WeightedSkills AS (
		SELECT team_id,
			   'PG' AS position, 
			   SUM(height * pg_weight) / SUM(pg_weight) AS height,
			   SUM(weight * pg_weight) / SUM(pg_weight) AS weight,
			   SUM(wingspan * pg_weight) / SUM(pg_weight) AS wingspan,
			   SUM(vertical * pg_weight) / SUM(pg_weight) AS vertical,
			   SUM(Reb * pg_weight) / SUM(pg_weight) AS Reb,
			   SUM(IDef * pg_weight) / SUM(pg_weight) AS IDef,
			   SUM(PDef * pg_weight) / SUM(pg_weight) AS PDef,
			   SUM(IQ * pg_weight) / SUM(pg_weight) AS IQ,
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
			   SUM(Reb * sg_weight) / SUM(sg_weight),
			   SUM(IDef * sg_weight) / SUM(sg_weight),
			   SUM(PDef * sg_weight) / SUM(sg_weight),
			   SUM(IQ * sg_weight) / SUM(sg_weight),
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
			   SUM(Reb * sf_weight) / SUM(sf_weight),
			   SUM(IDef * sf_weight) / SUM(sf_weight),
			   SUM(PDef * sf_weight) / SUM(sf_weight),
			   SUM(IQ * sf_weight) / SUM(sf_weight),
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
			   SUM(Reb * pf_weight) / SUM(pf_weight),
			   SUM(IDef * pf_weight) / SUM(pf_weight),
			   SUM(PDef * pf_weight) / SUM(pf_weight),
			   SUM(IQ * pf_weight) / SUM(pf_weight),
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
			   SUM(Reb * c_weight) / SUM(c_weight),
			   SUM(IDef * c_weight) / SUM(c_weight),
			   SUM(PDef * c_weight) / SUM(c_weight),
			   SUM(IQ * c_weight) / SUM(c_weight),
			   SUM(Spd * c_weight) / SUM(c_weight),
			   SUM(Sta * c_weight) / SUM(c_weight)
		FROM PositionDistribution
		WHERE c_weight > 0
		GROUP BY team_id
	),

	FinalTeamSkills AS (
		SELECT 
			team_id,
			-- PG
			ROUND(MAX(CASE WHEN position='PG' THEN height END),1) AS pg_height,
			ROUND(MAX(CASE WHEN position='PG' THEN weight END),1) AS pg_weight,
			ROUND(MAX(CASE WHEN position='PG' THEN wingspan END),1) AS pg_wingspan,
			ROUND(MAX(CASE WHEN position='PG' THEN vertical END),1) AS pg_vertical,
			ROUND(MAX(CASE WHEN position='PG' THEN Reb END),1) AS pg_Reb,
			ROUND(MAX(CASE WHEN position='PG' THEN IDef END),1) AS pg_IDef,
			ROUND(MAX(CASE WHEN position='PG' THEN PDef END),1) AS pg_PDef,
			ROUND(MAX(CASE WHEN position='PG' THEN IQ END),1) AS pg_IQ,
			ROUND(MAX(CASE WHEN position='PG' THEN Spd END),1) AS pg_Spd,
			ROUND(MAX(CASE WHEN position='PG' THEN Sta END),1) AS pg_Sta,

			-- SG
			ROUND(MAX(CASE WHEN position='SG' THEN height END),1) AS sg_height,
			ROUND(MAX(CASE WHEN position='SG' THEN weight END),1) AS sg_weight,
			ROUND(MAX(CASE WHEN position='SG' THEN wingspan END),1) AS sg_wingspan,
			ROUND(MAX(CASE WHEN position='SG' THEN vertical END),1) AS sg_vertical,
			ROUND(MAX(CASE WHEN position='SG' THEN Reb END),1) AS sg_Reb,
			ROUND(MAX(CASE WHEN position='SG' THEN IDef END),1) AS sg_IDef,
			ROUND(MAX(CASE WHEN position='SG' THEN PDef END),1) AS sg_PDef,
			ROUND(MAX(CASE WHEN position='SG' THEN IQ END),1) AS sg_IQ,
			ROUND(MAX(CASE WHEN position='SG' THEN Spd END),1) AS sg_Spd,
			ROUND(MAX(CASE WHEN position='SG' THEN Sta END),1) AS sg_Sta,

			-- SF
			ROUND(MAX(CASE WHEN position='SF' THEN height END),1) AS sf_height,
			ROUND(MAX(CASE WHEN position='SF' THEN weight END),1) AS sf_weight,
			ROUND(MAX(CASE WHEN position='SF' THEN wingspan END),1) AS sf_wingspan,
			ROUND(MAX(CASE WHEN position='SF' THEN vertical END),1) AS sf_vertical,
			ROUND(MAX(CASE WHEN position='SF' THEN Reb END),1) AS sf_Reb,
			ROUND(MAX(CASE WHEN position='SF' THEN IDef END),1) AS sf_IDef,
			ROUND(MAX(CASE WHEN position='SF' THEN PDef END),1) AS sf_PDef,
			ROUND(MAX(CASE WHEN position='SF' THEN IQ END),1) AS sf_IQ,
			ROUND(MAX(CASE WHEN position='SF' THEN Spd END),1) AS sf_Spd,
			ROUND(MAX(CASE WHEN position='SF' THEN Sta END),1) AS sf_Sta,

			-- PF
			ROUND(MAX(CASE WHEN position='PF' THEN height END),1) AS pf_height,
			ROUND(MAX(CASE WHEN position='PF' THEN weight END),1) AS pf_weight,
			ROUND(MAX(CASE WHEN position='PF' THEN wingspan END),1) AS pf_wingspan,
			ROUND(MAX(CASE WHEN position='PF' THEN vertical END),1) AS pf_vertical,
			ROUND(MAX(CASE WHEN position='PF' THEN Reb END),1) AS pf_Reb,
			ROUND(MAX(CASE WHEN position='PF' THEN IDef END),1) AS pf_IDef,
			ROUND(MAX(CASE WHEN position='PF' THEN PDef END),1) AS pf_PDef,
			ROUND(MAX(CASE WHEN position='PF' THEN IQ END),1) AS pf_IQ,
			ROUND(MAX(CASE WHEN position='PF' THEN Spd END),1) AS pf_Spd,
			ROUND(MAX(CASE WHEN position='PF' THEN Sta END),1) AS pf_Sta,

			-- C
			ROUND(MAX(CASE WHEN position='C' THEN height END),1) AS c_height,
			ROUND(MAX(CASE WHEN position='C' THEN weight END),1) AS c_weight,
			ROUND(MAX(CASE WHEN position='C' THEN wingspan END),1) AS c_wingspan,
			ROUND(MAX(CASE WHEN position='C' THEN vertical END),1) AS c_vertical,
			ROUND(MAX(CASE WHEN position='C' THEN Reb END),1) AS c_Reb,
			ROUND(MAX(CASE WHEN position='C' THEN IDef END),1) AS c_IDef,
			ROUND(MAX(CASE WHEN position='C' THEN PDef END),1) AS c_PDef,
			ROUND(MAX(CASE WHEN position='C' THEN IQ END),1) AS c_IQ,
			ROUND(MAX(CASE WHEN position='C' THEN Spd END),1) AS c_Spd,
			ROUND(MAX(CASE WHEN position='C' THEN Sta END),1) AS c_Sta

		FROM WeightedSkills
		GROUP BY team_id
	)
SELECT 
    fts.*, 
    tavg.*
FROM FinalTeamSkills fts
LEFT JOIN team_avg tavg
    ON fts.team_id = tavg.team_id
    AND tavg.season_id = 2046
    AND tavg.stat_type = 'team'
	AND tavg.game_type = "College"
ORDER BY fts.team_id;
