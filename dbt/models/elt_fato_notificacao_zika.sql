-- Gerado por python -m pipelines.generate_dbt; não editar manualmente.
SELECT
ROW_NUMBER() OVER (ORDER BY z.arquivo_origem, z.linha_origem) AS sk_notificacao,
COALESCE(CAST(DATE_FORMAT(z.data_notificacao, '%Y%m%d') AS SIGNED), 0) AS fk_tempo_notificacao,
COALESCE(CAST(DATE_FORMAT(z.data_sintomas, '%Y%m%d') AS SIGNED), 0) AS fk_tempo_sintomas,
d2.sk_localidade AS fk_localidade_residencia,
d3.sk_unidade AS fk_unidade_notificadora,
d4.sk_paciente AS fk_paciente,
d5.sk_desfecho AS fk_desfecho,
z.qt_notificacoes,
z.fl_confirmado,
z.fl_descartado,
z.fl_gestante,
z.fl_obito_zika,
z.qt_dias_atraso_notif,
z.qt_dias_encerramento
FROM {{ ref('int_zika') }} z
JOIN {{ ref('elt_dim_tempo') }} d0 ON d0.sk_tempo = COALESCE(CAST(DATE_FORMAT(z.data_notificacao, '%Y%m%d') AS SIGNED), 0)
JOIN {{ ref('elt_dim_tempo') }} d1 ON d1.sk_tempo = COALESCE(CAST(DATE_FORMAT(z.data_sintomas, '%Y%m%d') AS SIGNED), 0)
JOIN {{ ref('elt_dim_localidade') }} d2 ON d2.sk_localidade > 0 AND z.cod_uf_ibge <=> d2.cod_uf_ibge AND z.sigla_uf <=> d2.sigla_uf AND z.nome_estado <=> d2.nome_estado AND z.regiao_brasil <=> d2.regiao_brasil AND z.cod_municipio_ibge6 <=> d2.cod_municipio_ibge6 AND z.cod_regional_saude <=> d2.cod_regional_saude
JOIN {{ ref('elt_dim_unidade_notificadora') }} d3 ON d3.sk_unidade > 0 AND z.cod_unidade_cnes <=> d3.cod_unidade_cnes AND z.cod_uf_notificacao <=> d3.cod_uf_notificacao AND z.sigla_uf_notificacao <=> d3.sigla_uf_notificacao AND z.cod_municipio_notificacao <=> d3.cod_municipio_notificacao AND z.cod_regional_notificacao <=> d3.cod_regional_notificacao
JOIN {{ ref('elt_dim_paciente') }} d4 ON d4.sk_paciente > 0 AND z.sexo <=> d4.sexo AND z.descricao_sexo <=> d4.descricao_sexo AND z.idade_anos <=> d4.idade_anos AND z.faixa_etaria <=> d4.faixa_etaria AND z.raca_cor <=> d4.raca_cor AND z.status_gestante <=> d4.status_gestante AND z.escolaridade <=> d4.escolaridade
JOIN {{ ref('elt_dim_investigacao_desfecho') }} d5 ON d5.sk_desfecho > 0 AND z.classificacao_final <=> d5.classificacao_final AND z.criterio_confirmacao <=> d5.criterio_confirmacao AND z.evolucao_caso <=> d5.evolucao_caso AND z.tipo_autoctonia <=> d5.tipo_autoctonia AND z.doenca_trabalho <=> d5.doenca_trabalho
