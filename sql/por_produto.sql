SELECT p.nome AS produto,
       SUM(v.quantidade_vendida) AS total_unidades,
       ROUND(SUM(v.receita), 2) AS receita_total
FROM vendas v
JOIN produtos p ON p.id_produto = v.id_produto
GROUP BY p.nome
ORDER BY receita_total DESC;
