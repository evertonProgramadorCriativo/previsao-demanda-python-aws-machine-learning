WITH mensal AS (
    SELECT DATE_TRUNC('month', data)::date AS mes,
           SUM(receita) AS receita
    FROM vendas
    GROUP BY 1
)
SELECT mes,
       ROUND(receita, 2) AS receita,
       ROUND(LAG(receita) OVER (ORDER BY mes), 2) AS mes_anterior,
       ROUND(100.0 * (receita - LAG(receita) OVER (ORDER BY mes))
             / NULLIF(LAG(receita) OVER (ORDER BY mes), 0), 1) AS variacao_pct
FROM mensal
ORDER BY mes;
