# Dados brutos — Zika/SINAN (2024–2026)

## Fonte e proveniência

A fonte temática declarada pela equipe é o [conjunto Sinan/Vírus Zika do Ministério da Saúde](https://dadosabertos.saude.gov.br/dataset/arboviroses-zika-virus), também indicado no enunciado da disciplina. A página institucional foi consultada em **16/11/2026** para conferir a identificação da fonte. Essa consulta não representa a data de download dos CSVs do projeto.

**A data original de download não foi registrada.** Também não há registro dos URLs diretos dos recursos baixados ou de eventuais conversões anteriores à produção destes CSVs. Não é possível afirmar que os arquivos locais correspondam à versão atualmente publicada no portal. Datas de arquivos do sistema e datas de commits não substituem a data de obtenção.

Os arquivos usados na entrega são os CSVs preservados neste repositório. Seus hashes SHA-256 e metadados estão em [metadados_fontes.json](metadados_fontes.json); eles identificam exatamente a entrada auditada. A auditoria foi realizada em **16/11/2026**.

## Inventário e cobertura observada

| Arquivo | Linhas brutas | Colunas | Menor DT_NOTIFIC | Maior DT_NOTIFIC | Ano da data diferente do nome do arquivo |
|---|---:|---:|---|---|---:|
| [`ZIKABR24.csv`](ZIKABR24.csv) | 43.312 | 38 | 2024-01-01 | 2025-02-24 | 69 |
| [`ZIKABR25.csv`](ZIKABR25.csv) | 25.764 | 38 | 2024-12-29 | 2026-02-12 | 12 |
| [`ZIKABR26.csv`](ZIKABR26.csv) | 13.384 | 38 | 2026-01-04 | 2026-10-05 | 0 |

Os três arquivos usam vírgula e são lidos como UTF-8 com BOM opcional (`utf-8-sig`). O cabeçalho e a ordem dos **38 campos** são iguais e conferidos contra `pipelines/contrato.json`. Há **82.460 linhas brutas** no conjunto.

Os intervalos acima são mínimos e máximos observados, não garantias de cobertura completa. O nome do arquivo identifica a extração anual; o calendário analítico é derivado da data efetiva `DT_NOTIFIC`. Por exemplo, o arquivo `ZIKABR24.csv` inclui 69 linhas com data de notificação em 2025; `ZIKABR25.csv` inclui 6 em 2024 e 6 em 2026. A auditoria não estabelece a causa dessas diferenças.

**2026 é parcial:** seu arquivo termina em 05/10/2026. Comparações devem explicitar o recorte e, quando necessário, usar períodos equivalentes. Contagens descrevem notificações e não incidência populacional ou pessoas únicas.

## Qualidade e tratamento

A deduplicação considera os **38 valores textuais originais**, antes das conversões de tipo, na ordem `ZIKABR24.csv`, `ZIKABR25.csv`, `ZIKABR26.csv`, preservando a primeira ocorrência. São removidas **56 duplicatas exatas**, restando **82.404 linhas distintas**. A validação do pipeline não encontra rejeições por `DT_NOTIFIC` nesta versão; portanto, a fato contém **82.404 registros**. Uma combinação de atributos de paciente não identifica uma pessoa.

Os metadados registram a distribuição bruta do ano de notificação, duplicatas removidas por arquivo e contagens de campos vazios ou só com espaços. Essas contagens não incluem códigos de desconhecido (como 9), zeros ou datas inválidas; não devem ser interpretadas como uma medição completa de qualidade.

| Campo vazio ou só com espaços | ZIKABR24 | ZIKABR25 | ZIKABR26 |
|---|---:|---:|---:|
| `CLASSI_FIN` | 537 | 433 | 754 |
| `DT_ENCERRA` | 563 | 504 | 786 |
| `EVOLUCAO` | 6.351 | 3.777 | 1.859 |
| `SG_UF` | 9 | 8 | 15 |

Essas diferenças de preenchimento motivam rótulos de investigação e o tratamento explícito de valores desconhecidos, sem excluir automaticamente a notificação.

## Reprodução da auditoria

Na raiz do clone, sem dependências adicionais:

```bash
python3 scripts/auditar_fontes.py
```

O comando atualiza somente `dados/metadados_fontes.json` e imprime os totais; não altera os CSVs. Para comparar outra pasta sem sobrescrever o inventário da entrega:

```bash
python3 scripts/auditar_fontes.py --dados /caminho/dos/csvs --saida /tmp/metadados_zika.json
```

Os pipelines usam `ZIKA_DATA_DIR` para outra pasta. As regras, tipos físicos e origens estão no [dicionário de dados](../docs/dicionario_de_dados_e_mapeamento_de_divergencias.md); a estrutura visual está no [esquema estrela](../docs/figuras/esquema_estrela.svg).
