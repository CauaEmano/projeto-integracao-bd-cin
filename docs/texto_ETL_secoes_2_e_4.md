# Texto do ETL para o relatório 

---

## SEÇÃO 2 — inserir no relatório

### 2.1. Fluxo ETL (Python/Pandas → MySQL)

No fluxo ETL, toda a transformação acontece em memória, em Python, **antes** de qualquer conexão com o banco.
O MySQL recebe apenas o resultado final: as cinco dimensões e a tabela fato. O código está em
[`pipelines/core.py`](../pipelines/core.py) (`extract`, `transform` e `star`) e na publicação em
[`pipelines/database.py`](../pipelines/database.py). A demonstração em etapas está em
[`notebooks/pipeline_ETL.ipynb`](../notebooks/pipeline_ETL.ipynb), executada no Google Colab em
**[17/11/2026]** com MySQL instalado no próprio ambiente. A cópia executada está em
`docs/evidencias/etl_colab_executado.ipynb`.

#### Extract — leitura dos três CSVs

A função `extract` lê `ZIKABR24.csv`, `ZIKABR25.csv` e `ZIKABR26.csv` com Pandas, usando `dtype=str` e
`keep_default_na=False`. Todos os valores entram como texto, sem conversão automática de tipos. Assim,
campos numéricos que contêm vazios não viram `float` e nenhum valor é alterado antes de ser validado.

Para cada arquivo, a função confere se o cabeçalho é idêntico às 38 colunas do contrato
([`contrato.json`](../pipelines/contrato.json)); se não for, a execução é interrompida. Depois, acrescenta duas colunas de
rastreabilidade: `arquivo_origem` e `linha_origem` (a linha do CSV, contando o cabeçalho como linha 1). Os três
DataFrames são então concatenados.

Resultado: **82.460 linhas brutas** (43.312 + 25.764 + 13.384).

#### Transform — limpeza, decodificação e métricas

A função `transform` percorre os registros e aplica, nesta ordem:

1. **Deduplicação exata.** `drop_duplicates` compara os 38 campos originais, ainda como texto, e mantém a
   primeira ocorrência. Linhas que diferem em qualquer campo permanecem, porque a extração não tem identificador único de caso.
2. **Validação da data obrigatória.** `DT_NOTIFIC` precisa estar no formato AAAA-MM-DD e ser uma data real.
   Se não estiver, o registro vai para a lista de rejeitados, com o motivo. Nesta entrada, nenhum registro foi rejeitado.
3. **Datas opcionais.** `DT_SIN_PRI` e `DT_ENCERRA` inválidas ou ausentes viram `NULL`; o registro é mantido.
4. **Códigos numéricos.** Valores como `26` e `26.0` são convertidos para inteiro; textos fora do padrão viram `NULL`.
5. **Idade.** O código composto `NU_IDADE_N` é decodificado: 1000–3999 vira 0 anos; 4000–4120 vira o código menos 4000;
   qualquer outro valor vira `NULL`. A idade em anos é então enquadrada em faixa etária.
6. **Geografia.** `SG_UF` é traduzido em sigla, nome do estado e região pelo mapa do contrato. UF vazia ou desconhecida vira `NI / Não Informado`;
   a residência não é inferida a partir do local de atendimento.
7. **Domínios.** Sexo, raça/cor, gestação, escolaridade, classificação final, critério, evolução, autoctonia e doença
   relacionada ao trabalho são traduzidos em descrições legíveis. Códigos fora do domínio recebem o valor padrão do contrato.
8. **Indicadores e métricas.** São calculados `fl_confirmado`, `fl_descartado`, `fl_gestante`, `fl_obito_zika` e `qt_notificacoes = 1`.
   Também são calculados `qt_dias_atraso_notif` (sintomas → notificação) e `qt_dias_encerramento` (notificação → encerramento). Intervalos
   fora de 0–365 dias viram `NULL`, sem excluir a notificação.

A função devolve os registros válidos, os rejeitados e um resumo de auditoria. A reconciliação fecha:

| Brutas | Duplicatas exatas | Rejeitadas | Válidas |
|---:|---:|---:|---:|
| 82.460 | 56 | 0 | **82.404** |

O notebook confere essa soma com um `assert`: `brutas = duplicadas_exatas + rejeitadas + validas`.

#### Modelagem dimensional em memória

A função `star` monta o esquema estrela com os registros válidos:

- `dim_tempo` recebe cada data distinta de notificação e de sintomas, com chave no formato AAAAMMDD, mais o membro desconhecido (chave 0).
- As outras quatro dimensões recebem as **combinações distintas** de seus atributos, ordenadas, com chaves substitutas
  sequenciais, mais o membro desconhecido (chave 0).
- A fato recebe uma linha por registro válido, com a chave substituta `sk_notificacao`, as seis chaves estrangeiras
  (duas delas para `dim_tempo`: notificação e sintomas) e as métricas.

Tabelas geradas:

| Tabela | Linhas |
|---|---:|
| `dim_tempo` | 1.003 |
| `dim_localidade` | 2.562 |
| `dim_unidade_notificadora` | 6.631 |
| `dim_paciente` | 9.024 |
| `dim_investigacao_desfecho` | 128 |
| `fato_notificacao_zika` | 82.404 |

#### Load — publicação no MySQL

Com a transformação concluída, o notebook abre a conexão e chama `publish`, que carrega as dimensões **antes** da fato,
respeitando as chaves estrangeiras, e substitui o conteúdo das seis tabelas em uma única transação. Se
qualquer etapa falhar, ocorre rollback. Em seguida, `validate` conta as linhas de cada tabela, e o notebook verifica que
a fato tem o mesmo número de registros válidos da transformação.

#### Resultado da execução no Colab

- Ambiente: Google Colab, MySQL **[8.0.46: versão do `mysql --version`]** instalado no próprio ambiente, banco `zika_dw`.
- Registros na fato: **[82.404]**.
- Tempo total do ETL (`run("etl")`, incluindo leitura, transformação e carga): **[31.061]** segundos.
- Evidências: `docs/evidencias/etl_colab_executado.ipynb` e `docs/evidencias/manifesto_etl.json`.

Esse tempo vem de uma única execução e serve ao comparativo da seção 5, sem sustentar conclusões gerais de desempenho.

---

## SEÇÃO 4 — exemplos reais do ETL (inserir depois da tabela 4.1)

### 4.3. Exemplos reais de transformação no ETL

Os exemplos abaixo são linhas reais de `ZIKABR24.csv`, identificadas pela linha do arquivo, antes e depois da função `transform`.

| Linha (`ZIKABR24.csv`) | Entrada (campos brutos) | Saída (após o ETL) |
|---|---|---|
| 2 | `NU_IDADE_N=4033`, `CS_GESTANT=1`, `SG_UF=32`, `CLASSI_FIN=2`, `EVOLUCAO=0` | 33 anos, faixa "30 a 44 anos"; "1º Trimestre", `fl_gestante=1`; ES / Espírito Santo / Sudeste; "Descartado" (`fl_descartado=1`); evolução "Ignorado / Em Acompanhamento" |
| 26 | `NU_IDADE_N=2005`, `CS_GESTANT=5` | 0 anos, faixa "0 a 14 anos" (código 2xxx tratado como menor de 1 ano); "Não Gestante", `fl_gestante=0` |
| 5445 | `SG_UF=26`, `NU_IDADE_N=3010`, `CS_GESTANT=6`, `EVOLUCAO=1` | PE / Pernambuco / Nordeste; 0 anos; "Não se aplica"; evolução "Cura" |
| 5987 | `SG_UF` vazio, `EVOLUCAO` vazio | UF `NI / Não Informado / Não Informado`; registro mantido, evolução "Ignorado / Em Acompanhamento" |
| 2 | `DT_SIN_PRI=2024-01-07`, `DT_NOTIFIC=2024-01-08`, `DT_ENCERRA=2024-01-16` | `qt_dias_atraso_notif=1`, `qt_dias_encerramento=8` |
| 2333 e 2334 | Duas linhas idênticas nos 38 campos | Uma única linha na fato (a primeira ocorrência é preservada) |

**Observações sobre os resultados:**

- Das 82.404 notificações válidas, **7.184** têm `fl_gestante=1`, **4.619** têm `fl_confirmado=1` e **1** tem `fl_obito_zika=1`.
- `qt_dias_atraso_notif` ficou preenchido em todas as linhas. `qt_dias_encerramento` ficou `NULL` em **1.923**: **1.850** têm `DT_ENCERRA` vazio, e os
  outros 73 têm data inválida ou intervalo fora de 0–365 dias. Ao calcular médias, só os valores preenchidos entram.
- Nenhum registro foi rejeitado por `DT_NOTIFIC` inválida; a quarentena (`rejeitados.csv`) ficou vazia.
