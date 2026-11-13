-- Gerado por python -m pipelines.generate_dbt; não editar manualmente.
{{ config(post_hook=["ALTER TABLE {{ this }} ADD PRIMARY KEY (sk_tempo)"]) }}
SELECT 0 AS sk_tempo, NULL AS data_completa, NULL AS ano, NULL AS mes, 'Não Informado' AS nome_mes, NULL AS trimestre, NULL AS semana_epidemiologica, 'Não Informado' AS periodo_sazonal
UNION ALL
SELECT CAST(DATE_FORMAT(data_completa, '%Y%m%d') AS SIGNED), data_completa,
    YEAR(data_completa), MONTH(data_completa),
    ELT(MONTH(data_completa), 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'),
    QUARTER(data_completa), WEEK(data_completa, 6),
    CASE WHEN MONTH(data_completa) <= 5 THEN 'Alta Transmissão (Jan-Mai)' ELSE 'Baixa Transmissão (Jun-Dez)' END
FROM (
    SELECT data_notificacao AS data_completa FROM {{ ref('int_zika') }}
    UNION SELECT data_sintomas FROM {{ ref('int_zika') }} WHERE data_sintomas IS NOT NULL
) dates
