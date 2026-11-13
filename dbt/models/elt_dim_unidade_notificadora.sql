-- Gerado por python -m pipelines.generate_dbt; não editar manualmente.
{{ config(post_hook=["ALTER TABLE {{ this }} ADD PRIMARY KEY (sk_unidade)", "CREATE INDEX idx_atributos ON {{ this }} (cod_unidade_cnes, cod_uf_notificacao, sigla_uf_notificacao, cod_municipio_notificacao, cod_regional_notificacao)"]) }}
SELECT 0 AS sk_unidade, NULL AS cod_unidade_cnes, NULL AS cod_uf_notificacao, 'NI' AS sigla_uf_notificacao, NULL AS cod_municipio_notificacao, NULL AS cod_regional_notificacao
UNION ALL
SELECT ROW_NUMBER() OVER (ORDER BY cod_unidade_cnes, cod_uf_notificacao, sigla_uf_notificacao, cod_municipio_notificacao, cod_regional_notificacao) AS sk_unidade, cod_unidade_cnes, cod_uf_notificacao, sigla_uf_notificacao, cod_municipio_notificacao, cod_regional_notificacao
FROM (SELECT DISTINCT cod_unidade_cnes, cod_uf_notificacao, sigla_uf_notificacao, cod_municipio_notificacao, cod_regional_notificacao FROM {{ ref('int_zika') }}) d
