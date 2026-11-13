SELECT 1 AS falha
WHERE (SELECT COUNT(*) FROM {{ source('bruto', 'stg_zika') }}) <>
      (SELECT COUNT(*) FROM {{ ref('elt_fato_notificacao_zika') }}) +
      (SELECT COUNT(*) FROM {{ ref('elt_rejeitados') }}) +
      (SELECT COUNT(*) FROM {{ source('bruto', 'stg_zika') }}) -
      (SELECT COUNT(*) FROM {{ ref('stg_zika_unica') }})
