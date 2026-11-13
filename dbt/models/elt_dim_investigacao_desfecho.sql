-- Gerado por python -m pipelines.generate_dbt; não editar manualmente.
{{ config(post_hook=["ALTER TABLE {{ this }} ADD PRIMARY KEY (sk_desfecho)", "CREATE INDEX idx_atributos ON {{ this }} (classificacao_final, criterio_confirmacao, evolucao_caso, tipo_autoctonia, doenca_trabalho)"]) }}
SELECT 0 AS sk_desfecho, 'Inconclusivo / Em Investigação' AS classificacao_final, 'Ignorado / Não Preenchido' AS criterio_confirmacao, 'Ignorado / Em Acompanhamento' AS evolucao_caso, 'Indeterminado / Ignorado' AS tipo_autoctonia, 'Ignorado' AS doenca_trabalho
UNION ALL
SELECT ROW_NUMBER() OVER (ORDER BY classificacao_final, criterio_confirmacao, evolucao_caso, tipo_autoctonia, doenca_trabalho) AS sk_desfecho, classificacao_final, criterio_confirmacao, evolucao_caso, tipo_autoctonia, doenca_trabalho
FROM (SELECT DISTINCT classificacao_final, criterio_confirmacao, evolucao_caso, tipo_autoctonia, doenca_trabalho FROM {{ ref('int_zika') }}) d
