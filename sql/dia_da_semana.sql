SELECT EXTRACT(DOW FROM data)::int AS dia_semana,
       ROUND(AVG(unidades_dia), 1) AS media_unidades_por_dia
FROM (
    SELECT data, SUM(quantidade_vendida) AS unidades_dia
    FROM vendas
    GROUP BY data
) t
GROUP BY 1
ORDER BY 1;
