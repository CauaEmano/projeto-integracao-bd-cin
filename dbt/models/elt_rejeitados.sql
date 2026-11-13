-- Gerado por python -m pipelines.generate_dbt; não editar manualmente.
SELECT *, 'DT_NOTIFIC ausente ou inválida' AS motivo FROM {{ ref('int_zika_tipificada') }} WHERE d_DT_NOTIFIC IS NULL
