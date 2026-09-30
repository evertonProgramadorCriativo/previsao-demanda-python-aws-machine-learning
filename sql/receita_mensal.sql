SELECT DATE_TRUNC('month', data)::date AS mes,
       SUM(quantidade_vendida) AS unidades,
       ROUND(SUM(receita), 2) AS receita
FROM vendas
GROUP BY 1
ORDER BY 1;
