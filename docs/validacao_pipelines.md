# Validação dos pipelines — 13/11/2026

Validação local em Python 3.12, MySQL 8.0.36, dbt Core 1.7.20 e dbt-mysql 1.7.0.
O servidor foi iniciado exclusivamente para os testes; bancos temporários com UUID
foram removidos ao final. Nenhum banco de aplicação foi usado.

## Resultado da entrada versionada

| Etapa | Linhas |
|---|---:|
| Três arquivos brutos | 82.460 |
| Duplicatas exatas nos 38 campos | 56 |
| Rejeições por data de notificação | 0 |
| Notificações publicadas | 82.404 |

| Tabela | Linhas (inclui SK=0 nas dimensões) |
|---|---:|
| dim_tempo | 1.003 |
| dim_localidade | 2.562 |
| dim_unidade_notificadora | 6.631 |
| dim_paciente | 9.024 |
| dim_investigacao_desfecho | 128 |
| fato_notificacao_zika | 82.404 |

## Verificações

- Seis testes Python: regras de borda, reconciliação da entrada completa, calendário,
  correspondência dos modelos gerados ao contrato, correspondência do DDL ao contrato
  e notebooks válidos, sem saídas antigas ou gráficos nos pipelines.
- Construção de 11 modelos e aprovação dos 26 testes dbt: unicidade, chaves não nulas,
  relações entre fato e dimensões, limites de métricas e reconciliação.
- Comparação **integral das seis tabelas**, ordenadas por PK: ETL e ELT idênticos,
  incluindo todos os atributos, métricas e chaves substitutas.
- Reexecução dos dois fluxos sem mudança dos resultados.
- Paridade em entradas sintéticas com nulos, datas impossíveis, duplicatas entre arquivos,
  códigos decimais, escolaridade zero, idade fora do domínio e intervalos inválidos.
- Violação intencional de FK durante a publicação: MySQL rejeita e o rollback preserva
  integralmente a carga anterior.
- Proteção contra esquema legado: colunas incompatíveis são detectadas antes da publicação,
  com orientação para usar um banco dedicado novo.
- Execução do notebook ETL e das três consultas/gráficos do notebook de análises.
  Imagens exportadas para `saidas/analises/` e inspecionadas visualmente.

## Reprodução

Na raiz do repositório, com as dependências instaladas:

```bash
python -m unittest tests.test_pipelines
python -m tests.integration_mysql
```

O segundo comando requer uma conexão MySQL e permissão para criar/remover o banco temporário.
Ele respeita `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER` e `MYSQL_PASSWORD`.
As contagens acima são específicas dos CSVs versionados, não uma exigência para futuras extrações.
