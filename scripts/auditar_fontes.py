"""Gera metadados verificáveis dos CSVs sem modificar as fontes (somente stdlib)."""
import argparse
import csv
import hashlib
import json
import re
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = ['ZIKABR24.csv', 'ZIKABR25.csv', 'ZIKABR26.csv']
SOURCE = 'https://dadosabertos.saude.gov.br/dataset/arboviroses-zika-virus'


def audit(directory):
    contract = json.loads((ROOT / 'pipelines/contrato.json').read_text())
    seen = set()
    files = []
    for name in FILES:
        path = directory / name
        dates, invalid, duplicate, total = [], 0, 0, 0
        years = {}
        empty = {column: 0 for column in contract['columns']}
        mismatch = 0
        with path.open(encoding='utf-8-sig', newline='') as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != contract['columns']:
                raise ValueError(f'Layout inesperado: {name}')
            for row in reader:
                total += 1
                if None in row or any(value is None for value in row.values()):
                    raise ValueError(f'Linha CSV malformada: {name}:{reader.line_num}')
                key = tuple(row[column] for column in contract['columns'])
                duplicate += int(key in seen)
                seen.add(key)
                for column, value in row.items():
                    empty[column] += int(not value.strip())
                try:
                    text = row['DT_NOTIFIC'].strip()
                    if not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', text):
                        raise ValueError('Formato de data fora do contrato')
                    notified = date.fromisoformat(text)
                    if notified.year < 1000:
                        raise ValueError('Ano fora do contrato MySQL')
                except ValueError:
                    invalid += 1
                    continue
                dates.append(notified.isoformat())
                year = str(notified.year)
                years[year] = years.get(year, 0) + 1
                mismatch += int(year != '20' + name[6:8])
        files.append({
            'arquivo': name, 'bytes': path.stat().st_size,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'linhas': total, 'colunas': len(reader.fieldnames),
            'dt_notific_min': min(dates) if dates else None,
            'dt_notific_max': max(dates) if dates else None,
            'dt_notific_invalidas': invalid,
            'ano_dt_notific_distribuicao_bruta': dict(sorted(years.items())),
            'ano_dt_notific_diferente_do_nome_arquivo': mismatch,
            'duplicatas_exatas_removidas_na_ordem_de_leitura': duplicate,
            'campos_vazios_ou_so_espacos': empty,
        })
    return {
        'fonte_declarada': SOURCE,
        'data_download_original': None,
        'observacao_proveniencia': (
            'Fonte temática declarada no projeto. A data de download, os URLs diretos '
            'dos recursos e eventuais conversões anteriores ao CSV não foram registrados. '
            'Hashes identificam os arquivos locais, não comprovam correspondência com '
            'a versão atual do portal. Contagens por ano são brutas, antes da deduplicação.'
        ),
        'encoding_leitura': 'utf-8-sig', 'separador': ',',
        'ordem_deduplicacao': FILES, 'colunas': contract['columns'],
        'arquivos': files,
        'totais': {'brutas': sum(f['linhas'] for f in files),
                   'duplicatas_exatas': sum(f['duplicatas_exatas_removidas_na_ordem_de_leitura'] for f in files),
                   'distintas_38_campos': len(seen)},
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dados', type=Path, default=ROOT / 'dados')
    parser.add_argument('--saida', type=Path, default=ROOT / 'dados/metadados_fontes.json')
    args = parser.parse_args()
    result = audit(args.dados)
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result['totais'], ensure_ascii=False))
