"""Conexão, carga e publicação transacional no mesmo DDL MySQL."""
import os
import re

from .core import CONTRACT, ROOT, TABLES


def database_name():
    name = os.getenv('MYSQL_DATABASE', 'zika_dw')
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,63}', name):
        raise ValueError('MYSQL_DATABASE deve ser um identificador simples de até 64 caracteres.')
    return name


def connect():
    import mysql.connector
    return mysql.connector.connect(host=os.getenv('MYSQL_HOST', '127.0.0.1'),
        port=int(os.getenv('MYSQL_PORT', '3306')), user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', ''), database=database_name(),
        charset='utf8mb4', collation='utf8mb4_0900_bin', autocommit=False)


def execute_script(connection, sql):
    sql = re.sub(r'--[^\n]*', '', sql)
    with connection.cursor() as cursor:
        for statement in sql.split(';'):
            if statement.strip():
                cursor.execute(statement)


def prepare(connection):
    # Os antigos notebooks tinham tabelas homônimas com outras colunas.
    # Detecta incompatibilidade antes de qualquer DDL ou alteração dos dados finais.
    with connection.cursor() as cursor:
        for table, columns in TABLES.items():
            cursor.execute("""SELECT COLUMN_NAME, COLUMN_TYPE FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s ORDER BY ORDINAL_POSITION""", (table,))
            existing = cursor.fetchall()
            expected = [(name, kind.upper()) for name, kind in columns.items()]
            actual = [(name, kind.upper()) for name, kind in existing]
            if existing and actual != expected:
                raise ValueError(f'Esquema incompatível em {table}. Configure MYSQL_DATABASE para um novo banco dedicado; consulte README.md.')
    execute_script(connection, (ROOT / 'sql/01_script_ddl_do_esquema_estrela.sql').read_text())
    connection.commit()


def insert_records(cursor, table, records, columns, batch=2000):
    sql = f'INSERT INTO `{table}` (' + ','.join(f'`{c}`' for c in columns) + ') VALUES (' + ','.join(['%s'] * len(columns)) + ')'
    for offset in range(0, len(records), batch):
        cursor.executemany(sql, [tuple(r[c] for c in columns) for r in records[offset:offset+batch]])


def publish(connection, tables=None):
    """Substitui somente as seis tabelas estrela; rollback preserva a carga anterior."""
    prepare(connection)
    try:
        with connection.cursor() as cursor:
            for table in reversed(TABLES):
                cursor.execute(f'DELETE FROM `{table}`')
            for table, columns in TABLES.items():
                if tables is not None:
                    insert_records(cursor, table, tables[table], list(columns))
                else:
                    names = ','.join(f'`{c}`' for c in columns)
                    cursor.execute(f'INSERT INTO `{table}` ({names}) SELECT {names} FROM `elt_{table}`')
        connection.commit()
    except Exception:
        connection.rollback()
        raise


def load_raw(connection, raw):
    """Persiste exatamente o texto lido; não converte códigos nem filtra linhas."""
    columns = CONTRACT['columns'] + ['arquivo_origem','linha_origem']
    ddl = ',\n'.join(f'`{c}` VARCHAR(255) NOT NULL' for c in CONTRACT['columns'])
    with connection.cursor() as cursor:
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS stg_zika (
            {ddl}, arquivo_origem VARCHAR(32) NOT NULL, linha_origem INT NOT NULL,
            PRIMARY KEY (arquivo_origem, linha_origem)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_bin''')
    connection.commit()
    try:
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM stg_zika')
            insert_records(cursor, 'stg_zika', raw.to_dict('records'), columns)
        connection.commit()
    except Exception:
        connection.rollback()
        raise


def validate(connection):
    with connection.cursor() as cursor:
        counts = {}
        for table in TABLES:
            cursor.execute(f'SELECT COUNT(*) FROM `{table}`')
            counts[table] = cursor.fetchone()[0]
        # As FKs físicas são aplicadas pelo MySQL durante a publicação.
        cursor.execute('''SELECT COUNT(*) FROM fato_notificacao_zika WHERE
            qt_notificacoes <> 1 OR fl_confirmado + fl_descartado > 1
            OR qt_dias_atraso_notif NOT BETWEEN 0 AND 365
            OR qt_dias_encerramento NOT BETWEEN 0 AND 365''')
        if cursor.fetchone()[0]:
            raise ValueError('Métricas inválidas na fato')
    return counts
