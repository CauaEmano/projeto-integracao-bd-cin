-- Gerado por python -m pipelines.generate_dbt; não editar manualmente.
{{ config(post_hook=["ALTER TABLE {{ this }} ADD PRIMARY KEY (sk_localidade)", "CREATE INDEX idx_atributos ON {{ this }} (cod_uf_ibge, sigla_uf, nome_estado, regiao_brasil, cod_municipio_ibge6, cod_regional_saude)"]) }}
SELECT 0 AS sk_localidade, NULL AS cod_uf_ibge, 'NI' AS sigla_uf, 'Não Informado' AS nome_estado, 'Não Informado' AS regiao_brasil, NULL AS cod_municipio_ibge6, NULL AS cod_regional_saude
UNION ALL
SELECT ROW_NUMBER() OVER (ORDER BY cod_uf_ibge, sigla_uf, nome_estado, regiao_brasil, cod_municipio_ibge6, cod_regional_saude) AS sk_localidade, cod_uf_ibge, sigla_uf, nome_estado, regiao_brasil, cod_municipio_ibge6, cod_regional_saude
FROM (SELECT DISTINCT cod_uf_ibge, sigla_uf, nome_estado, regiao_brasil, cod_municipio_ibge6, cod_regional_saude FROM {{ ref('int_zika') }}) d
