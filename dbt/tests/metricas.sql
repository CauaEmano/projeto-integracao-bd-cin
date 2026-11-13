SELECT * FROM {{ ref('elt_fato_notificacao_zika') }}
WHERE qt_notificacoes <> 1
   OR fl_confirmado NOT IN (0,1) OR fl_descartado NOT IN (0,1)
   OR fl_gestante NOT IN (0,1) OR fl_obito_zika NOT IN (0,1)
   OR qt_dias_atraso_notif NOT BETWEEN 0 AND 365
   OR qt_dias_encerramento NOT BETWEEN 0 AND 365
