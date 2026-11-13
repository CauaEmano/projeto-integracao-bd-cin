"""python -m pipelines.run etl|elt (usa o banco MYSQL_DATABASE já criado)."""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from .core import ROOT, extract, star, transform
from .database import connect, load_raw, publish, validate


def run(mode):
    start = time.perf_counter()
    raw = extract()
    output = Path(os.getenv('ZIKA_OUTPUT_DIR', ROOT / 'saidas')) / mode
    output.mkdir(parents=True, exist_ok=True)
    if mode == 'etl':
        rows, rejected, audit = transform(raw)
        tables = star(rows)  # Toda a transformação termina antes de acessar o MySQL.
        import pandas as pd
        pd.DataFrame(rejected, columns=list(raw.columns) + ['motivo']).to_csv(output / 'rejeitados.csv', index=False)
        with connect() as connection:
            publish(connection, tables)
            counts = validate(connection)
    elif mode == 'elt':
        with connect() as connection:
            load_raw(connection, raw)
        subprocess.run([sys.executable, '-m', 'dbt.cli.main', 'build', '--project-dir', str(ROOT / 'dbt'),
                        '--profiles-dir', str(ROOT / 'dbt')], check=True,
                       env={**os.environ, 'DBT_SEND_ANONYMOUS_USAGE_STATS': 'false'})
        with connect() as connection:
            publish(connection)
            counts = validate(connection)
            with connection.cursor() as cursor:
                cursor.execute('SELECT COUNT(*) FROM stg_zika_unica')
                unique = cursor.fetchone()[0]
                cursor.execute('SELECT COUNT(*) FROM elt_rejeitados')
                rejected = cursor.fetchone()[0]
            audit = {'brutas':len(raw), 'duplicadas_exatas':len(raw)-unique,
                     'rejeitadas':rejected, 'validas':counts['fato_notificacao_zika']}
    else:
        raise ValueError('Modo deve ser etl ou elt')
    if audit['brutas'] != sum(audit[k] for k in ['duplicadas_exatas','rejeitadas','validas']):
        raise ValueError('Falha na reconciliação de linhas')
    manifest = {'pipeline':mode, 'reconciliacao':audit, 'tabelas':counts,
                'duracao_segundos':round(time.perf_counter()-start, 3)}
    (output / 'manifesto.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['etl','elt'])
    run(parser.parse_args().mode)
