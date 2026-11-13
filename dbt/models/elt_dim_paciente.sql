-- Gerado por python -m pipelines.generate_dbt; não editar manualmente.
{{ config(post_hook=["ALTER TABLE {{ this }} ADD PRIMARY KEY (sk_paciente)", "CREATE INDEX idx_atributos ON {{ this }} (sexo, descricao_sexo, idade_anos, faixa_etaria, raca_cor, status_gestante, escolaridade)"]) }}
SELECT 0 AS sk_paciente, 'I' AS sexo, 'Ignorado' AS descricao_sexo, NULL AS idade_anos, 'Ignorado' AS faixa_etaria, 'Ignorado' AS raca_cor, 'Ignorado' AS status_gestante, 'Ignorado' AS escolaridade
UNION ALL
SELECT ROW_NUMBER() OVER (ORDER BY sexo, descricao_sexo, idade_anos, faixa_etaria, raca_cor, status_gestante, escolaridade) AS sk_paciente, sexo, descricao_sexo, idade_anos, faixa_etaria, raca_cor, status_gestante, escolaridade
FROM (SELECT DISTINCT sexo, descricao_sexo, idade_anos, faixa_etaria, raca_cor, status_gestante, escolaridade FROM {{ ref('int_zika') }}) d
