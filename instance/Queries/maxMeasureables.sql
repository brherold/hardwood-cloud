SELECT
    AVG(height) AS average_height,
    MAX(height) AS max_height,
    AVG(weight) AS average_weight,
    MAX(weight) AS max_weight,
    AVG(wingspan) AS average_wingspan,
    MAX(wingspan) AS max_wingspan,
    AVG(vertical) AS average_vertical,
    MAX(vertical) AS max_vertical
FROM
    players_skills
WHERE
    class IN ("SR", "RS SR", "JR", "RS JR", "RS SO");