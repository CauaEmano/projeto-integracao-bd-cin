# Dicionário de dados e mapeamento de divergências — Zika/SINAN

Este é o dicionário do projeto, extraído do relatório e consolidado para **ETL e ELT**.
Os nomes físicos são minúsculos no MySQL. Ambos publicam exatamente as mesmas seis tabelas,
com o mesmo [DDL](../sql/01_script_ddl_do_esquema_estrela.sql).
O [contrato executável](../pipelines/contrato.json) centraliza colunas, tipos e domínios.
Os modelos dbt são gerados dele por `python -m pipelines.generate_dbt`.

## 1. Dicionário de Dados do Esquema Estrela

#### Tabela Fato: `FATO_NOTIFICACAO_ZIKA`
| Atributo | Tipo de Dado | Restrição | Descrição e Metadados Relevantes |
| :--- | :--- | :--- | :--- |
| `sk_notificacao` | `INTEGER` | `PRIMARY KEY` | Chave substituta (*Surrogate Key*) única do registro na tabela fato. |
| `fk_tempo_notificacao` | `INTEGER` | `FOREIGN KEY` | Referência à `DIM_TEMPO` para a data da notificação (`DT_NOTIFIC`, formato `YYYYMMDD`). |
| `fk_tempo_sintomas` | `INTEGER` | `FOREIGN KEY` | Referência à `DIM_TEMPO` para a data dos primeiros sintomas (`DT_SIN_PRI`, ou `0` se ausente). |
| `fk_localidade_residencia`| `INTEGER` | `FOREIGN KEY` | Referência à `DIM_LOCALIDADE` (UF e município de residência do paciente: `SG_UF`, `ID_MN_RESI`). |
| `fk_unidade_notificadora`| `INTEGER` | `FOREIGN KEY` | Referência à `DIM_UNIDADE_NOTIFICADORA` (CNES, UF e município onde o atendimento foi notificado). |
| `fk_paciente` | `INTEGER` | `FOREIGN KEY` | Referência à `DIM_PACIENTE` (perfil sociodemográfico: sexo, faixa etária, raça/cor, gestante, escolaridade). |
| `fk_desfecho` | `INTEGER` | `FOREIGN KEY` | Referência à `DIM_INVESTIGACAO_DESFECHO` (classificação final, critério, evolução, autoctonia). |
| `qt_notificacoes` | `INTEGER` | `NOT NULL` | Métrica aditiva base ($1$ para cada notificação válida integrada). |
| `fl_confirmado` | `INTEGER` | `NOT NULL` | Indicador binário ($1$ se `CLASSI_FIN = 1` — Caso Confirmado; $0$ caso contrário). |
| `fl_descartado` | `INTEGER` | `NOT NULL` | Indicador binário ($1$ se `CLASSI_FIN = 2` — Caso Descartado; $0$ caso contrário). |
| `fl_gestante` | `INTEGER` | `NOT NULL` | Indicador binário ($1$ se `CS_GESTANT` estiver entre $1$ e $4$ — Paciente Gestante; $0$ caso contrário). |
| `fl_obito_zika` | `INTEGER` | `NOT NULL` | Indicador binário ($1$ se `EVOLUCAO = 2` — Óbito pelo agravo notificado; $0$ caso contrário). |
| `qt_dias_atraso_notif` | `INTEGER` | `NULLABLE` | Métrica contínua: diferença em dias entre `DT_NOTIFIC` e `DT_SIN_PRI` ($\text{DT\_NOTIFIC} - \text{DT\_SIN\_PRI}$). |
| `qt_dias_encerramento` | `INTEGER` | `NULLABLE` | Métrica contínua: diferença em dias entre o encerramento (`DT_ENCERRA`) e a notificação (`DT_NOTIFIC`). |

#### Tabelas Dimensão (`DIM_TEMPO`, `DIM_LOCALIDADE`, `DIM_UNIDADE_NOTIFICADORA`, `DIM_PACIENTE`, `DIM_INVESTIGACAO_DESFECHO`)
| Tabela Dimensão | Atributos (Colunas) | Descrição e Origem dos Metadados no SINAN |
| :--- | :--- | :--- |
| **`DIM_TEMPO`** | `sk_tempo` (PK), `data_completa` (`DATE`), `ano` (`INT`), `mes` (`INT`), `nome_mes` (`VARCHAR`), `trimestre` (`INT`), `semana_epidemiologica` (`INT`), `periodo_sazonal` (`VARCHAR`) | Extraída das datas válidas de `DT_NOTIFIC` e `DT_SIN_PRI`; semana epidemiológica recalculada pela data. Classifica os meses em `'Alta Transmissão (Jan-Mai)'` e `'Baixa Transmissão (Jun-Dez)'`. |
| **`DIM_LOCALIDADE`** | `sk_localidade` (PK), `cod_uf_ibge` (`INT`), `sigla_uf` (`CHAR(2)`), `nome_estado` (`VARCHAR`), `regiao_brasil` (`VARCHAR`), `cod_municipio_ibge6` (`INT`), `cod_regional_saude` (`INT`) | Extraída de `SG_UF`, `ID_MN_RESI` e `ID_RG_RESI`. Converte os códigos numéricos de UF do IBGE (`11` a `53`) em siglas (`RO` a `DF`), nomes de estados e macrorregiões. |
| **`DIM_UNIDADE_NOTIFICADORA`** | `sk_unidade` (PK), `cod_unidade_cnes` (`INT`), `cod_uf_notificacao` (`INT`), `sigla_uf_notificacao` (`CHAR(2)`), `cod_municipio_notificacao` (`INT`), `cod_regional_notificacao` (`INT`) | Extraída de `ID_UNIDADE`, `SG_UF_NOT`, `ID_MUNICIP` e `ID_REGIONA`. Permite cruzar o local de residência do paciente com o local efetivo de atendimento médico. |
| **`DIM_PACIENTE`** | `sk_paciente` (PK), `sexo` (`CHAR(1)`), `descricao_sexo` (`VARCHAR`), `idade_anos` (`INT`), `faixa_etaria` (`VARCHAR`), `raca_cor` (`VARCHAR`), `status_gestante` (`VARCHAR`), `escolaridade` (`VARCHAR`) | Decodifica `CS_SEXO`, `NU_IDADE_N` (convertido de código composto de 4 dígitos para anos e faixas etárias), `CS_RACA`, `CS_GESTANT` e `CS_ESCOL_N`. |
| **`DIM_INVESTIGACAO_DESFECHO`** | `sk_desfecho` (PK), `classificacao_final` (`VARCHAR`), `criterio_confirmacao` (`VARCHAR`), `evolucao_caso` (`VARCHAR`), `tipo_autoctonia` (`VARCHAR`), `doenca_trabalho` (`VARCHAR`) | Decodifica os domínios epidemiológicos de `CLASSI_FIN`, `CRITERIO`, `EVOLUCAO`, `TPAUTOCTO` e `DOENCA_TRA`. |


## 2. Regras comuns e granularidade

- Uma linha da fato representa uma linha válida distinta do conjunto de **38 campos brutos**.
  Deduplicação exata entre arquivos, preservando a primeira ocorrência pela ordem arquivo/linha.
  Sem identificador único na fonte, não se presume que linhas diferentes sejam o mesmo caso.
- Os três CSVs usam UTF-8 (BOM tolerado), vírgula e o mesmo cabeçalho de 38 campos.
  ELT armazena todo o texto em `stg_zika` antes de qualquer limpeza, com `arquivo_origem`
  e `linha_origem`. ETL lê o mesmo texto em Pandas e transforma em memória.
- `DT_NOTIFIC` deve ser uma data ISO válida (`YYYY-MM-DD`, anos 1000–9999).
  Ausência ou data impossível causa quarentena. ETL exporta `saidas/etl/rejeitados.csv`;
  ELT mantém `elt_rejeitados` no MySQL. As datas opcionais inválidas tornam-se NULL.
- Ano, mês e trimestre vêm da data efetiva; `NU_ANO` e o nome do arquivo não definem o calendário.
  `SEM_NOT`/`SEM_PRI` são preservados no staging; `dim_tempo` usa semana de domingo a sábado,
  primeira semana com ao menos quatro dias do ano (MySQL `WEEK(data,6)`).
- Idade: `1000 <= NU_IDADE_N < 4000` vira 0 anos; de 4000 a 4120 subtrai-se 4000;
  qualquer outro código vira NULL. As faixas são **0 a 14**, **15 a 29**, **30 a 44**,
  **45 a 59**, **60 anos ou mais** e **Ignorado**.
- Códigos textuais inteiros ou com sufixo `.0` são convertidos para inteiro.
  Zero em códigos geográficos vira NULL; `CS_ESCOL_N=0` permanece **Analfabeto**.
- A residência ausente permanece desconhecida, sem inferência a partir do local de atendimento.
  UF sem cadastro recebe `NI` / `Não Informado`; códigos numéricos válidos são preservados.
- Intervalos entre sintomas/notificação e notificação/encerramento são aceitos entre 0 e 365 dias,
  inclusive. Valores negativos, acima de 365 ou com datas ausentes viram NULL.
- `qt_notificacoes=1`; `fl_confirmado=(CLASSI_FIN=1)`, `fl_descartado=(CLASSI_FIN=2)`,
  `fl_gestante=(CS_GESTANT em 1,2,3,4)` e `fl_obito_zika=(EVOLUCAO=2)`.
  Óbitos por outras causas (`EVOLUCAO=3`) não compõem `fl_obito_zika`.
- Dimensões de perfil são combinações distintas de atributos, não pessoas identificadas.
  As SKs são determinísticas, sequenciais a partir de 1; tempo usa YYYYMMDD.
  Todas as dimensões contêm SK=0 reservado ao membro desconhecido. Datas ausentes referenciam 0.
  Combinações parcialmente desconhecidas conservam seus atributos e recebem SK própria.
- MySQL 8.0.16+, InnoDB, `utf8mb4_0900_bin`; FKs explícitas e checks no DDL comum.
  A publicação substitui os dados das seis tabelas em transação; falha causa rollback.
  Não execute os dois pipelines simultaneamente no mesmo banco.

## 3. Domínios de decodificação

Códigos não listados, vazios ou inválidos usam o padrão da coluna.

### `descricao_sexo` ← `CS_SEXO`

| Código | Descrição |
|---|---|
| `M` | Masculino |
| `F` | Feminino |
| `I` | Ignorado |

**Padrão:** Ignorado.

### `raca_cor` ← `CS_RACA`

| Código | Descrição |
|---|---|
| `1` | Branca |
| `2` | Preta |
| `3` | Amarela |
| `4` | Parda |
| `5` | Indígena |
| `9` | Ignorado |

**Padrão:** Ignorado.

### `status_gestante` ← `CS_GESTANT`

| Código | Descrição |
|---|---|
| `1` | 1º Trimestre |
| `2` | 2º Trimestre |
| `3` | 3º Trimestre |
| `4` | Idade Gestacional Ignorada |
| `5` | Não Gestante |
| `6` | Não se aplica |
| `9` | Ignorado |

**Padrão:** Ignorado.

### `escolaridade` ← `CS_ESCOL_N`

| Código | Descrição |
|---|---|
| `0` | Analfabeto |
| `1` | 1ª a 4ª série incompleta |
| `2` | 4ª série completa |
| `3` | 5ª à 8ª série incompleta |
| `4` | Ensino fundamental completo |
| `5` | Ensino médio incompleto |
| `6` | Ensino médio completo |
| `7` | Educação superior incompleta |
| `8` | Educação superior completa |
| `9` | Ignorado |
| `10` | Não se aplica |

**Padrão:** Ignorado.

### `classificacao_final` ← `CLASSI_FIN`

| Código | Descrição |
|---|---|
| `1` | Confirmado |
| `2` | Descartado |
| `8` | Inconclusivo / Em Investigação |

**Padrão:** Inconclusivo / Em Investigação.

### `criterio_confirmacao` ← `CRITERIO`

| Código | Descrição |
|---|---|
| `1` | Laboratorial |
| `2` | Clínico-Epidemiológico |
| `3` | Em Investigação |

**Padrão:** Ignorado / Não Preenchido.

### `evolucao_caso` ← `EVOLUCAO`

| Código | Descrição |
|---|---|
| `1` | Cura |
| `2` | Óbito pelo agravo |
| `3` | Óbito por outras causas |

**Padrão:** Ignorado / Em Acompanhamento.

### `tipo_autoctonia` ← `TPAUTOCTO`

| Código | Descrição |
|---|---|
| `1` | Autóctone |
| `2` | Importado |

**Padrão:** Indeterminado / Ignorado.

### `doenca_trabalho` ← `DOENCA_TRA`

| Código | Descrição |
|---|---|
| `1` | Sim |
| `2` | Não |

**Padrão:** Ignorado.

## 4. Cadastro de UFs

| Código IBGE | Sigla | Estado | Região |
|---|---|---|---|
| 11 | RO | Rondônia | Norte |
| 12 | AC | Acre | Norte |
| 13 | AM | Amazonas | Norte |
| 14 | RR | Roraima | Norte |
| 15 | PA | Pará | Norte |
| 16 | AP | Amapá | Norte |
| 17 | TO | Tocantins | Norte |
| 21 | MA | Maranhão | Nordeste |
| 22 | PI | Piauí | Nordeste |
| 23 | CE | Ceará | Nordeste |
| 24 | RN | Rio Grande do Norte | Nordeste |
| 25 | PB | Paraíba | Nordeste |
| 26 | PE | Pernambuco | Nordeste |
| 27 | AL | Alagoas | Nordeste |
| 28 | SE | Sergipe | Nordeste |
| 29 | BA | Bahia | Nordeste |
| 31 | MG | Minas Gerais | Sudeste |
| 32 | ES | Espírito Santo | Sudeste |
| 33 | RJ | Rio de Janeiro | Sudeste |
| 35 | SP | São Paulo | Sudeste |
| 41 | PR | Paraná | Sul |
| 42 | SC | Santa Catarina | Sul |
| 43 | RS | Rio Grande do Sul | Sul |
| 50 | MS | Mato Grosso do Sul | Centro-Oeste |
| 51 | MT | Mato Grosso | Centro-Oeste |
| 52 | GO | Goiás | Centro-Oeste |
| 53 | DF | Distrito Federal | Centro-Oeste |

## 5. Divergências entre os arquivos e destino dos campos

| Divergência | Tratamento efetivo nos pipelines |
|---|---|
| Ano do arquivo, `NU_ANO` e `DT_NOTIFIC` podem divergir | Calendário derivado de `DT_NOTIFIC`; deduplicação exata interanual. |
| Códigos vazios, zeros e representação decimal | Conversão comum e padrões dos domínios; preserva escolaridade 0. |
| Maior ausência de desfecho em extrações recentes | Mantém notificações e usa os rótulos de investigação definidos acima. |
| Idade composta e valores acima de 120 anos | Decodificação e NULL conforme seção 2. |
| Datas de sintomas ou encerramento incoerentes | Intervalos fora de 0–365 viram NULL. |
| `ID_AGRAVO` como `A92.` e `A928`; `COUFINF` misto (ex.: `ES`) | Preservados no bruto; não são atributos do esquema estrela atual. Não há limpeza dessas colunas na fato. |

Campos usados nas dimensões: `DT_NOTIFIC`, `DT_SIN_PRI`, `SG_UF`, `ID_MN_RESI`, `ID_RG_RESI`,
`ID_UNIDADE`, `SG_UF_NOT`, `ID_MUNICIP`, `ID_REGIONA`, `CS_SEXO`, `NU_IDADE_N`, `CS_RACA`,
`CS_GESTANT`, `CS_ESCOL_N`, `CLASSI_FIN`, `CRITERIO`, `EVOLUCAO`, `TPAUTOCTO`, `DOENCA_TRA`.
`DT_ENCERRA` alimenta a métrica de encerramento. Os demais campos não são promovidos para a estrela;
permanecem nos CSVs e, no ELT, no staging. Não são criadas flags ou dimensões extras.

Na entrada versionada: 82.460 linhas brutas, 56 duplicatas exatas, 0 rejeições e 82.404 linhas na fato.
Esses totais são evidências desta versão, não constantes exigidas para novas extrações.
