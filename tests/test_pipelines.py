import unittest
from pathlib import Path

import pandas as pd

from pipelines.core import CONTRACT, ROOT, TABLES, epiweek, extract, star, transform
from pipelines.generate_dbt import generate
from datetime import date


def fixtures():
    base = {c:'' for c in CONTRACT['columns']}
    base.update(DT_NOTIFIC='2024-01-01', DT_SIN_PRI='2024-01-02', DT_ENCERRA='2026-01-01',
                NU_IDADE_N='3999', CS_SEXO='X', CS_ESCOL_N='0', EVOLUCAO='3',
                arquivo_origem='ZIKABR24.csv', linha_origem=2)
    cases = [base, {**base,'NU_IDADE_N':'4121','DT_NOTIFIC':'2024-02-29','linha_origem':3},
             {**base,'NU_IDADE_N':'4030.0','CLASSI_FIN':'1.0','CS_GESTANT':'4','EVOLUCAO':'2','linha_origem':4},
             {**base,'DT_NOTIFIC':'2024-02-30','linha_origem':5},
             {**base,'DT_NOTIFIC':'','linha_origem':6},
             {**base,'DT_NOTIFIC':'2025-01-01','DT_SIN_PRI':'2024-12-31','DT_ENCERRA':'2025-12-31','linha_origem':7},
             {**base,'arquivo_origem':'ZIKABR25.csv','linha_origem':2},
             {**base,'NU_IDADE_N':'bad','DT_NOTIFIC':'0000-00-00','linha_origem':8},
             {**base,'NU_IDADE_N':'1001','SG_UF':'26.0','CS_SEXO':'F','DT_NOTIFIC':'2024-01-01 ','linha_origem':9}]
    return pd.DataFrame(cases)


class ContractTests(unittest.TestCase):
    def test_edge_cases(self):
        rows, rejected, audit = transform(fixtures())
        self.assertEqual(audit, {'brutas':9,'duplicadas_exatas':1,'rejeitadas':3,'validas':5})
        self.assertEqual(rows[0]['idade_anos'],0)
        self.assertIsNone(rows[1]['idade_anos'])
        self.assertEqual(rows[2]['idade_anos'],30)
        self.assertEqual(rows[0]['escolaridade'],'Analfabeto')
        self.assertEqual(rows[0]['fl_obito_zika'],0)
        self.assertEqual(rows[2]['fl_obito_zika'],1)
        self.assertIsNone(rows[0]['qt_dias_atraso_notif'])
        self.assertIsNone(rows[0]['qt_dias_encerramento'])
        self.assertEqual(rows[3]['qt_dias_atraso_notif'],1)
        self.assertEqual(rows[3]['qt_dias_encerramento'],364)
        self.assertEqual(rows[0]['sigla_uf'],'NI')
        self.assertEqual(rows[0]['classificacao_final'],'Inconclusivo / Em Investigação')
        tables = star(rows)
        self.assertEqual(len(tables['fato_notificacao_zika']),5)
        for table, records in tables.items():
            self.assertEqual(list(records[0]),list(TABLES[table]))
        for table in list(TABLES)[:-1]:
            self.assertEqual(next(iter(tables[table][0].values())),0)

    def test_generated_models_match_contract(self):
        for name, sql in generate().items():
            self.assertEqual((ROOT/'dbt/models'/f'{name}.sql').read_text().split('\n',1)[1],sql)

    def test_ddl_columns_match_contract(self):
        import re
        ddl=(ROOT/'sql/01_script_ddl_do_esquema_estrela.sql').read_text()
        physical={}
        for table,body in re.findall(r'CREATE TABLE IF NOT EXISTS (\w+) \((.*?)\n\)',ddl,re.S):
            columns={}
            for line in body.splitlines():
                match=re.match(r'\s*(\w+) (INTEGER|DATE|CHAR\(\d+\)|VARCHAR\(\d+\))',line)
                if match:
                    columns[match[1]]=match[2].replace('INTEGER','INT')
            physical[table]=columns
        self.assertEqual(physical,TABLES)
        self.assertEqual(ddl.count('FOREIGN KEY'),6)

    def test_notebooks_are_clean_and_valid(self):
        import nbformat
        for path in (ROOT/'notebooks').glob('*.ipynb'):
            notebook=nbformat.read(path,as_version=4)
            nbformat.validate(notebook)
            for cell in notebook.cells:
                if cell.cell_type=='code':
                    compile(cell.source,str(path),'exec')
                    self.assertFalse(cell.outputs)
                    self.assertIsNone(cell.execution_count)
            if path.name.startswith('pipeline_'):
                self.assertNotIn('plt.',str(notebook))

    def test_calendar_boundary(self):
        self.assertEqual(epiweek(date(2024,12,29)),1)
        self.assertEqual(epiweek(date(2021,1,1)),53)

    def test_full_input_reconciliation(self):
        raw=extract()
        rows, rejected, audit=transform(raw)
        self.assertEqual(audit,{'brutas':82460,'duplicadas_exatas':56,'rejeitadas':0,'validas':82404})
        self.assertEqual(len(star(rows)['fato_notificacao_zika']),82404)


if __name__ == '__main__':
    unittest.main()
