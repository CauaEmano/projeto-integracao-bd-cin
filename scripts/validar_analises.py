"""Valida as consultas do notebook sobre a estrela ETL em SQLite temporário.

Não comprova execução MySQL/Colab. Exporta tabelas e figuras reprodutíveis.
Execute da raiz: python -m scripts.validar_analises
"""
import hashlib
import json
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from pipelines.core import ROOT, FILES, extract, transform, star


def main():
    rows, _, audit = transform(extract())
    tables = star(rows)
    out = ROOT / 'docs/analises'
    table_dir = out / 'tabelas'
    table_dir.mkdir(parents=True, exist_ok=True)
    notebook = json.loads((ROOT / 'notebooks/analises_zika.ipynb').read_text())
    with sqlite3.connect(':memory:') as connection:
        for name, records in tables.items():
            pd.DataFrame(records).to_sql(name, connection, index=False)
        scope = dict(pd=pd, plt=plt, output=out, tables_out=table_dir,
                     query=lambda sql: pd.read_sql_query(sql, connection), display=lambda _: None)
        # Executa as seis células analíticas reais; substitui somente a conexão.
        cells = [c for c in notebook['cells'] if c['cell_type'] == 'code'
                 and ' = query(' in ''.join(c['source'])]
        assert len(cells) == 6
        for cell in cells:
            exec(compile(''.join(cell['source']), 'analises_zika.ipynb', 'exec'), scope)
            plt.close('all')
        frame = pd.DataFrame(rows)
        frame['ano'] = frame.data_notificacao.map(lambda d: d.year)
        frame['mes'] = frame.data_notificacao.map(lambda d: d.month)
        summary = {
            'data_validacao': datetime.now(ZoneInfo('America/Fortaleza')).isoformat(),
            'ambiente': 'Estrela ETL Python + consultas do notebook em SQLite em memória; não MySQL/Colab',
            'sha256_fontes': {f: hashlib.sha256((ROOT/'dados'/f).read_bytes()).hexdigest() for f in FILES},
            'reconciliacao': audit,
            'tabelas': {name: len(records) for name, records in tables.items()},
            'jan_set_por_ano': frame[frame.mes <= 9].groupby('ano').size().to_dict(),
            'jan_mai': int((frame.mes <= 5).sum()),
            'gestantes': int(frame.fl_gestante.sum()),
            'gestantes_confirmadas': int((frame.fl_gestante * frame.fl_confirmado).sum()),
            'intervalos': {c: {'validos': int(frame[c].count()), 'media': frame[c].mean(),
                              'mediana': frame[c].median()} for c in ['qt_dias_atraso_notif','qt_dias_encerramento']},
            'consultas_executadas': len(cells),
        }
    (ROOT/'docs/evidencias/validacao_analises.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
