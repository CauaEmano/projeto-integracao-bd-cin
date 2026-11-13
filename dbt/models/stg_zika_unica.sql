-- Gerado por python -m pipelines.generate_dbt; não editar manualmente.
SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY `TP_NOT`, `ID_AGRAVO`, `DT_NOTIFIC`, `SEM_NOT`, `NU_ANO`, `SG_UF_NOT`, `ID_MUNICIP`, `ID_REGIONA`, `ID_UNIDADE`, `DT_SIN_PRI`, `SEM_PRI`, `ANO_NASC`, `NU_IDADE_N`, `CS_SEXO`, `CS_GESTANT`, `CS_RACA`, `CS_ESCOL_N`, `SG_UF`, `ID_MN_RESI`, `ID_RG_RESI`, `ID_PAIS`, `NDUPLIC_N`, `IN_VINCULA`, `DT_INVEST`, `ID_OCUPA_N`, `CLASSI_FIN`, `CRITERIO`, `TPAUTOCTO`, `COUFINF`, `COPAISINF`, `COMUNINF`, `DOENCA_TRA`, `EVOLUCAO`, `DT_OBITO`, `DT_ENCERRA`, `DT_DIGITA`, `TP_SISTEMA`, `TPUNINOT`
        ORDER BY arquivo_origem, linha_origem) AS repeticao
    FROM {{ source('bruto', 'stg_zika') }}
) r WHERE repeticao = 1
