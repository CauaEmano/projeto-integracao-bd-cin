"""Gera os modelos SQL a partir dos domínios e colunas do contrato comum.

Execute python -m pipelines.generate_dbt após alterar contrato.json.
"""
from .core import CONTRACT, DIMENSIONS, FACT, FKS, MONTHS, ROOT, TABLES, default_record


def literal(value):
    if value is None:
        return 'NULL'
    if isinstance(value, int):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def numeric(column):
    return f"CASE WHEN TRIM(`{column}`) REGEXP '^[0-9]{{1,9}}([.]0+)?$' THEN CAST(SUBSTRING_INDEX(TRIM(`{column}`), '.', 1) AS SIGNED) END"


def date_sql(column):
    # Valida o dia antes de STR_TO_DATE (evita erro em 2024-02-30 no MySQL estrito).
    c = f'TRIM(`{column}`)'
    first = f"STR_TO_DATE(CONCAT(LEFT({c}, 7), '-01'), '%Y-%m-%d')"
    return f"""CASE WHEN {c} REGEXP '^[1-9][0-9]{{3}}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$'
        THEN CASE WHEN CAST(RIGHT({c}, 2) AS UNSIGNED) <= DAY(LAST_DAY({first}))
        THEN STR_TO_DATE({c}, '%Y-%m-%d') END END"""


def ref(name):
    return "{{ ref('" + name + "') }}"


def generate():
    models = {}
    columns = ', '.join('`'+c+'`' for c in CONTRACT['columns'])
    models['stg_zika_unica'] = f"""SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY {columns}
        ORDER BY arquivo_origem, linha_origem) AS repeticao
    FROM {{{{ source('bruto', 'stg_zika') }}}}
) r WHERE repeticao = 1
"""
    numcols = ['SG_UF','SG_UF_NOT','ID_MN_RESI','ID_RG_RESI','ID_UNIDADE','ID_MUNICIP','ID_REGIONA','NU_IDADE_N','CLASSI_FIN','CRITERIO','EVOLUCAO','CS_GESTANT','CS_RACA','CS_ESCOL_N','TPAUTOCTO','DOENCA_TRA']
    base = [f'{numeric(c)} AS n_{c}' for c in numcols]
    base += [f'{date_sql(c)} AS d_{c}' for c in ['DT_NOTIFIC','DT_SIN_PRI','DT_ENCERRA']]
    models['int_zika_tipificada'] = 'SELECT *,\n' + ',\n'.join(base) + '\nFROM ' + ref('stg_zika_unica') + '\n'
    models['elt_rejeitados'] = "SELECT *, 'DT_NOTIFIC ausente ou inválida' AS motivo FROM " + ref('int_zika_tipificada') + ' WHERE d_DT_NOTIFIC IS NULL\n'
    expressions = {'data_notificacao':'d_DT_NOTIFIC','data_sintomas':'d_DT_SIN_PRI',
                   'idade_anos': 'CASE WHEN n_NU_IDADE_N BETWEEN 1000 AND 3999 THEN 0 WHEN n_NU_IDADE_N BETWEEN 4000 AND 4120 THEN n_NU_IDADE_N - 4000 END',
                   'sexo': "CASE WHEN TRIM(CS_SEXO) IN ('M','F','I') THEN TRIM(CS_SEXO) ELSE 'I' END"}
    for target, src in {'cod_uf_ibge':'SG_UF','cod_municipio_ibge6':'ID_MN_RESI','cod_regional_saude':'ID_RG_RESI',
                        'cod_unidade_cnes':'ID_UNIDADE','cod_uf_notificacao':'SG_UF_NOT','cod_municipio_notificacao':'ID_MUNICIP','cod_regional_notificacao':'ID_REGIONA'}.items():
        expressions[target] = f'NULLIF(n_{src}, 0)'
    for target, code, index, default in [('sigla_uf','SG_UF',0,'NI'),('nome_estado','SG_UF',1,'Não Informado'),('regiao_brasil','SG_UF',2,'Não Informado'),('sigla_uf_notificacao','SG_UF_NOT',0,'NI')]:
        expressions[target] = f'CASE n_{code} ' + ' '.join(f'WHEN {k} THEN {literal(v[index])}' for k,v in CONTRACT['ufs'].items()) + f' ELSE {literal(default)} END'
    for field, domain in CONTRACT['domains'].items():
        code = 'TRIM(CS_SEXO)' if field == 'descricao_sexo' else 'n_' + domain['source']
        expressions[field] = 'CASE ' + code + ' ' + ' '.join(f'WHEN {literal(k) if field == "descricao_sexo" else k} THEN {literal(v)}' for k,v in domain['values'].items()) + ' ELSE ' + literal(domain['default']) + ' END'
    expressions.update({'qt_notificacoes':'1', 'fl_confirmado':'IF(n_CLASSI_FIN = 1, 1, 0)',
                        'fl_descartado':'IF(n_CLASSI_FIN = 2, 1, 0)', 'fl_gestante':'IF(n_CS_GESTANT IN (1,2,3,4), 1, 0)',
                        'fl_obito_zika':'IF(n_EVOLUCAO = 2, 1, 0)'})
    for field, start, end in [('qt_dias_atraso_notif','DT_SIN_PRI','DT_NOTIFIC'),('qt_dias_encerramento','DT_NOTIFIC','DT_ENCERRA')]:
        diff = f'DATEDIFF(d_{end}, d_{start})'
        expressions[field] = f'CASE WHEN {diff} BETWEEN 0 AND 365 THEN {diff} END'
    sql = 'SELECT arquivo_origem, linha_origem,\n' + ',\n'.join(f'{expr} AS {field}' for field,expr in expressions.items())
    models['int_zika_decodificada'] = sql + '\nFROM ' + ref('int_zika_tipificada') + ' WHERE d_DT_NOTIFIC IS NOT NULL\n'
    models['int_zika'] = """SELECT *, CASE WHEN idade_anos IS NULL THEN 'Ignorado'
    WHEN idade_anos < 15 THEN '0 a 14 anos' WHEN idade_anos < 30 THEN '15 a 29 anos'
    WHEN idade_anos < 45 THEN '30 a 44 anos' WHEN idade_anos < 60 THEN '45 a 59 anos'
    ELSE '60 anos ou mais' END AS faixa_etaria
FROM """ + ref('int_zika_decodificada') + '\n'
    for table in DIMENSIONS[1:]:
        pk, *cols = TABLES[table]
        collist = ', '.join(cols)
        default = ', '.join(f'{literal(v)} AS {k}' for k,v in default_record(table).items())
        models['elt_' + table] = f'SELECT {default}\nUNION ALL\nSELECT ROW_NUMBER() OVER (ORDER BY {collist}) AS {pk}, {collist}\nFROM (SELECT DISTINCT {collist} FROM {ref("int_zika")}) d\n'
    default = ', '.join(f'{literal(v)} AS {k}' for k,v in default_record('dim_tempo').items())
    # WEEK(date, 6): dimanche/sábado, semana 1 com >= 4 dias (1..53).
    models['elt_dim_tempo'] = f"""SELECT {default}
UNION ALL
SELECT CAST(DATE_FORMAT(data_completa, '%Y%m%d') AS SIGNED), data_completa,
    YEAR(data_completa), MONTH(data_completa),
    ELT(MONTH(data_completa), {', '.join(literal(v) for v in MONTHS)}),
    QUARTER(data_completa), WEEK(data_completa, 6),
    CASE WHEN MONTH(data_completa) <= 5 THEN 'Alta Transmissão (Jan-Mai)' ELSE 'Baixa Transmissão (Jun-Dez)' END
FROM (
    SELECT data_notificacao AS data_completa FROM {ref('int_zika')}
    UNION SELECT data_sintomas FROM {ref('int_zika')} WHERE data_sintomas IS NOT NULL
) dates
"""
    selections = ['ROW_NUMBER() OVER (ORDER BY z.arquivo_origem, z.linha_origem) AS sk_notificacao']
    joins = []
    for i,(fk,table) in enumerate(FKS.items()):
        if table == 'dim_tempo':
            column = 'data_notificacao' if fk == 'fk_tempo_notificacao' else 'data_sintomas'
            selections.append(f"COALESCE(CAST(DATE_FORMAT(z.{column}, '%Y%m%d') AS SIGNED), 0) AS {fk}")
            # Dependência explícita para o DAG dbt.
            joins.append(f"JOIN {ref('elt_dim_tempo')} d{i} ON d{i}.sk_tempo = COALESCE(CAST(DATE_FORMAT(z.{column}, '%Y%m%d') AS SIGNED), 0)")
        else:
            pk,*cols = TABLES[table]
            selections.append(f'd{i}.{pk} AS {fk}')
            joins.append(f'JOIN {ref("elt_"+table)} d{i} ON d{i}.{pk} > 0 AND ' + ' AND '.join(f'z.{c} <=> d{i}.{c}' for c in cols))
    selections += ['z.' + c for c in list(TABLES[FACT])[7:]]
    models['elt_' + FACT] = 'SELECT\n' + ',\n'.join(selections) + '\nFROM ' + ref('int_zika') + ' z\n' + '\n'.join(joins) + '\n'
    for table in DIMENSIONS:
        pk, *cols = TABLES[table]
        hooks = [f'ALTER TABLE {{{{ this }}}} ADD PRIMARY KEY ({pk})']
        if table != 'dim_tempo':
            hooks.append(f'CREATE INDEX idx_atributos ON {{{{ this }}}} (' + ', '.join(cols) + ')')
        import json
        config = '{{ config(post_hook=' + json.dumps(hooks) + ') }}\n'
        models['elt_' + table] = config + models['elt_' + table]
    return models


def main():
    for name,sql in generate().items():
        (ROOT / 'dbt/models' / (name + '.sql')).write_text('-- Gerado por python -m pipelines.generate_dbt; não editar manualmente.\n' + sql)


if __name__ == '__main__':
    main()
