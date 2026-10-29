SELECT
    player_id,
    (
        CASE WHEN pg_rapm IS NOT NULL THEN pg_rapm * PG_Min ELSE 0 END +
        CASE WHEN sg_rapm IS NOT NULL THEN sg_rapm * SG_Min ELSE 0 END +
        CASE WHEN sf_rapm IS NOT NULL THEN sf_rapm * SF_Min ELSE 0 END +
        CASE WHEN pf_rapm IS NOT NULL THEN pf_rapm * PF_Min ELSE 0 END +
        CASE WHEN c_rapm  IS NOT NULL THEN c_rapm  * C_Min  ELSE 0 END
    ) /
    NULLIF(
        (CASE WHEN pg_rapm IS NOT NULL THEN PG_Min ELSE 0 END +
         CASE WHEN sg_rapm IS NOT NULL THEN SG_Min ELSE 0 END +
         CASE WHEN sf_rapm IS NOT NULL THEN SF_Min ELSE 0 END +
         CASE WHEN pf_rapm IS NOT NULL THEN PF_Min ELSE 0 END +
         CASE WHEN c_rapm  IS NOT NULL THEN C_Min  ELSE 0 END),
        0
    ) AS total_rapm, EPM
FROM player_avg
WHERE season_id = 2046
  AND game_type = 'College'
  AND GP >= 15
  AND Min >= 20
  ORDER BY total_rapm desc
  