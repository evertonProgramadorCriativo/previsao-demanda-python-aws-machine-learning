SELECT COUNT(*) AS linhas,
       MIN(data) AS primeira_data,
       MAX(data) AS ultima_data,
       COUNT(DISTINCT id_produto) AS produtos,
       COUNT(DISTINCT id_regiao) AS regioes,
       ROUND(SUM(receita), 2) AS receita_total
FROM vendas;
