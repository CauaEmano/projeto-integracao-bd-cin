-- Gerado por python -m pipelines.generate_dbt; não editar manualmente.
SELECT *, CASE WHEN idade_anos IS NULL THEN 'Ignorado'
    WHEN idade_anos < 15 THEN '0 a 14 anos' WHEN idade_anos < 30 THEN '15 a 29 anos'
    WHEN idade_anos < 45 THEN '30 a 44 anos' WHEN idade_anos < 60 THEN '45 a 59 anos'
    ELSE '60 anos ou mais' END AS faixa_etaria
FROM {{ ref('int_zika_decodificada') }}
