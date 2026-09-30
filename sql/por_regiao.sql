SELECT r.nome AS regiao,
       SUM(v.quantidade_vendida) AS total_unidades,
       ROUND(SUM(v.receita), 2) AS receita_total
FROM vendas v
JOIN regioes r ON r.id_regiao = v.id_regiao
GROUP BY r.nome
ORDER BY receita_total DESC;
