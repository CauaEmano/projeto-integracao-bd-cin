"""Contrato e transformação ETL em memória; sem acesso ao SGBD."""
import json
import os
import re
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / 'pipelines/contrato.json').read_text())
TABLES = CONTRACT['tables']
DIMENSIONS = list(TABLES)[:-1]
FACT = 'fato_notificacao_zika'
FILES = ['ZIKABR24.csv', 'ZIKABR25.csv', 'ZIKABR26.csv']
FKS = dict(zip(['fk_tempo_notificacao', 'fk_tempo_sintomas', 'fk_localidade_residencia',
               'fk_unidade_notificadora', 'fk_paciente', 'fk_desfecho'],
              ['dim_tempo', 'dim_tempo', *DIMENSIONS[1:]]))
MONTHS = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
          'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']


def extract(directory=None):
    """Leitura textual: não limpa nem decodifica valores antes da carga ELT."""
    frames = []
    for filename in FILES:
        frame = pd.read_csv(Path(directory or os.getenv('ZIKA_DATA_DIR', ROOT / 'dados')) / filename,
                            dtype=str, keep_default_na=False, encoding='utf-8-sig')
        if list(frame.columns) != CONTRACT['columns']:
            raise ValueError(f'Layout inesperado em {filename}')
        frame['arquivo_origem'] = filename
        frame['linha_origem'] = range(2, len(frame) + 2)
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def number(value):
    text = str(value).strip()
    return int(text.split('.')[0]) if re.fullmatch(r'[0-9]{1,9}(\.0+)?', text) else None


def parsedate(value):
    text = str(value).strip()
    if not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', text):
        return None
    try:
        result = date.fromisoformat(text)
        return result if result.year >= 1000 else None
    except ValueError:
        return None


def epiweek(day):
    def start(year):
        jan4 = date(year, 1, 4)
        return jan4 - timedelta(days=(jan4.weekday() + 1) % 7)
    year = day.year
    if year < 9999 and day >= start(year + 1):
        year += 1
    elif day < start(year):
        year -= 1
    return (day - start(year)).days // 7 + 1


def time_record(day):
    return dict(zip(TABLES['dim_tempo'], [int(day.strftime('%Y%m%d')), day, day.year,
                day.month, MONTHS[day.month - 1], (day.month - 1) // 3 + 1, epiweek(day),
                'Alta Transmissão (Jan-Mai)' if day.month <= 5 else 'Baixa Transmissão (Jun-Dez)']))


def default_record(table):
    values = {column: None for column in TABLES[table]}
    values[next(iter(values))] = 0
    defaults = {
        'dim_tempo': {'nome_mes': 'Não Informado', 'periodo_sazonal': 'Não Informado'},
        'dim_localidade': {'sigla_uf': 'NI', 'nome_estado': 'Não Informado', 'regiao_brasil': 'Não Informado'},
        'dim_unidade_notificadora': {'sigla_uf_notificacao': 'NI'},
        'dim_paciente': {'sexo': 'I', 'descricao_sexo': 'Ignorado', 'faixa_etaria': 'Ignorado',
                         **{k: CONTRACT['domains'][k]['default'] for k in ['raca_cor', 'status_gestante', 'escolaridade']}},
        'dim_investigacao_desfecho': {k: CONTRACT['domains'][k]['default'] for k in list(TABLES['dim_investigacao_desfecho'])[1:]},
    }
    values.update(defaults[table])
    return values


def transform(raw):
    """Retorna somente atributos do contrato; deduplica os 38 campos brutos."""
    unique = raw.drop_duplicates(CONTRACT['columns'], keep='first')
    rows, rejected = [], []
    for source in unique.to_dict('records'):
        notif = parsedate(source['DT_NOTIFIC'])
        if notif is None:
            rejected.append({**source, 'motivo': 'DT_NOTIFIC ausente ou inválida'})
            continue
        symptoms, closed = parsedate(source['DT_SIN_PRI']), parsedate(source['DT_ENCERRA'])
        n = {k: number(v) for k, v in source.items()}
        age = n['NU_IDADE_N']
        age = 0 if age is not None and 1000 <= age < 4000 else age - 4000 if age is not None and 4000 <= age <= 4120 else None
        band = 'Ignorado' if age is None else ('0 a 14 anos' if age < 15 else '15 a 29 anos' if age < 30 else '30 a 44 anos' if age < 45 else '45 a 59 anos' if age < 60 else '60 anos ou mais')
        # Ausência da residência permanece desconhecida; não inferimos residência do atendimento.
        uf = CONTRACT['ufs'].get(str(n['SG_UF']), ['NI', 'Não Informado', 'Não Informado'])
        uf_not = CONTRACT['ufs'].get(str(n['SG_UF_NOT']), ['NI'])[0]
        r = {'data_notificacao': notif, 'data_sintomas': symptoms,
             'cod_uf_ibge': n['SG_UF'] or None, 'sigla_uf': uf[0], 'nome_estado': uf[1],
             'regiao_brasil': uf[2], 'cod_municipio_ibge6': n['ID_MN_RESI'] or None,
             'cod_regional_saude': n['ID_RG_RESI'] or None,
             'cod_unidade_cnes': n['ID_UNIDADE'] or None, 'cod_uf_notificacao': n['SG_UF_NOT'] or None,
             'sigla_uf_notificacao': uf_not, 'cod_municipio_notificacao': n['ID_MUNICIP'] or None,
             'cod_regional_notificacao': n['ID_REGIONA'] or None,
             'sexo': source['CS_SEXO'].strip() if source['CS_SEXO'].strip() in ['M','F','I'] else 'I',
             'idade_anos': age, 'faixa_etaria': band, 'qt_notificacoes': 1,
             'fl_confirmado': int(n['CLASSI_FIN'] == 1), 'fl_descartado': int(n['CLASSI_FIN'] == 2),
             'fl_gestante': int(n['CS_GESTANT'] in [1,2,3,4]), 'fl_obito_zika': int(n['EVOLUCAO'] == 2)}
        for field, domain in CONTRACT['domains'].items():
            code = source[domain['source']].strip() if field == 'descricao_sexo' else str(n[domain['source']])
            r[field] = domain['values'].get(code, domain['default'])
        for field, start, end in [('qt_dias_atraso_notif', symptoms, notif), ('qt_dias_encerramento', notif, closed)]:
            days = (end - start).days if start and end else None
            r[field] = days if days is not None and 0 <= days <= 365 else None
        rows.append(r)
    audit = {'brutas': len(raw), 'duplicadas_exatas': len(raw) - len(unique), 'rejeitadas': len(rejected), 'validas': len(rows)}
    return rows, rejected, audit


def sortkey(values):
    return tuple((value is not None, value if value is not None else '') for value in values)


def star(rows):
    """Modelagem ETL em memória com joins nulos seguros e chaves determinísticas."""
    tables, indexes = {}, {}
    days = {r[k] for r in rows for k in ['data_notificacao', 'data_sintomas'] if r[k]}
    tables['dim_tempo'] = [default_record('dim_tempo')] + [time_record(d) for d in sorted(days)]
    for table in DIMENSIONS[1:]:
        pk, *columns = TABLES[table]
        tuples = {tuple(row[c] for c in columns) for row in rows}
        tables[table] = [default_record(table)] + [dict(zip([pk, *columns], [i, *values]))
                            for i, values in enumerate(sorted(tuples, key=sortkey), 1)]
        indexes[table] = {tuple(r[c] for c in columns): r[pk] for r in tables[table][1:]}
    facts = []
    for i, row in enumerate(rows, 1):
        f = {'sk_notificacao': i}
        for fk, table in FKS.items():
            if table == 'dim_tempo':
                d = row['data_notificacao' if fk == 'fk_tempo_notificacao' else 'data_sintomas']
                f[fk] = int(d.strftime('%Y%m%d')) if d else 0
            else:
                f[fk] = indexes[table][tuple(row[c] for c in list(TABLES[table])[1:])]
        f.update({c: row[c] for c in list(TABLES[FACT])[7:]})
        facts.append(f)
    tables[FACT] = facts
    return tables
