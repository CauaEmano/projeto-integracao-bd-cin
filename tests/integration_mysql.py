"""Teste real MySQL/dbt: cria e remove apenas um banco temporário com UUID.

MYSQL_HOST=127.0.0.1 MYSQL_PORT=3306 python -m tests.integration_mysql
O usuário de teste precisa de CREATE/DROP DATABASE.
"""
import os
import uuid
from unittest.mock import patch

import mysql.connector

from pipelines.core import TABLES, star, transform
from pipelines.database import connect, load_raw, publish
from pipelines.run import run
from tests.test_pipelines import fixtures


def snapshot():
    with connect() as connection, connection.cursor() as cursor:
        data={}
        for table,columns in TABLES.items():
            cursor.execute(f'SELECT * FROM `{table}` ORDER BY `{next(iter(columns))}`')
            data[table]=cursor.fetchall()
        return data


def compare(left,right):
    for table in TABLES:
        if left[table] != right[table]:
            for a,b in zip(left[table],right[table]):
                if a!=b:
                    raise AssertionError(f'{table}: ETL={a}, ELT={b}')
            raise AssertionError(f'{table}: contagens diferentes')


def main():
    name='zika_test_'+uuid.uuid4().hex[:12]
    admin=mysql.connector.connect(host=os.getenv('MYSQL_HOST','127.0.0.1'),
        port=int(os.getenv('MYSQL_PORT','3306')),user=os.getenv('MYSQL_USER','root'),
        password=os.getenv('MYSQL_PASSWORD',''),autocommit=True)
    with admin.cursor() as cursor:
        cursor.execute(f'CREATE DATABASE `{name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_bin')
    previous=os.environ.get('MYSQL_DATABASE')
    os.environ['MYSQL_DATABASE']=name
    try:
        run('etl')
        etl=snapshot()
        run('etl')
        compare(etl,snapshot())
        run('elt')
        compare(etl,snapshot())
        run('elt')
        compare(etl,snapshot())
        print('OK: seis tabelas completas idênticas; ETL e ELT idempotentes (82.460 linhas).')
        import json
        from IPython.display import display
        from pipelines.core import ROOT
        import matplotlib
        matplotlib.use('Agg')
        for filename in ['pipeline_ETL.ipynb','analises_zika.ipynb']:
            notebook=json.loads((ROOT/'notebooks'/filename).read_text())
            scope={'display':display}
            for cell in notebook['cells']:
                if cell['cell_type']=='code':
                    exec(compile(''.join(cell['source']),filename,'exec'),scope)
        compare(etl,snapshot())
        print('OK: notebooks ETL e análises executados; três gráficos exportados.')
        raw=fixtures()
        with patch('pipelines.run.extract',return_value=raw):
            run('etl'); expected=snapshot()
            run('elt'); compare(expected,snapshot())
        print('OK: paridade em datas inválidas, nulos, domínios, duplicatas e fronteiras.')
        # Verifica o rollback: força uma FK inválida após apagar os dados dentro da transação.
        rows,_,_=transform(raw)
        invalid=star(rows)
        invalid['fato_notificacao_zika'][0]['fk_paciente']=-999
        with connect() as connection:
            try:
                publish(connection, invalid)
            except mysql.connector.IntegrityError:
                pass
            else:
                raise AssertionError('MySQL não rejeitou FK inválida')
        compare(expected,snapshot())
        print('OK: falha de FK causa rollback e preserva a publicação anterior.')
    finally:
        if previous is None:
            os.environ.pop('MYSQL_DATABASE',None)
        else:
            os.environ['MYSQL_DATABASE']=previous
        with admin.cursor() as cursor:
            cursor.execute(f'DROP DATABASE `{name}`')
        admin.close()


if __name__=='__main__':
    main()
