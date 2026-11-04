# Universidade Federal de Pernambuco
## Centro de Informática - CIn

**Integrantes (Nome - login):**
* Cauã Emanuel - `ceor@cin.ufpe.br`
* Allanis Beatriz - `aboml@cin.ufpe.br`
* Arthur Gabriel - `agsl@cin.ufpe.br`
* Allan Fernandes - `afl4@cin.ufpe.br`
* Felipe Melo - `fma4@cin.ufpe.br`
* Amanda Pereira - `apmo@cin.ufpe.br`

**TEMA:** Integração e Análise Dimensional das Notificações de Zika Vírus no Brasil no Triênio 2024–2026 (SINAN / Ministério da Saúde)

---

# Relatório do Projeto de Integração — Banco de Dados

---

## 1. Descrição da Base de Dados Unificada (Modelagem Dimensional e Dicionário de Dados)

A base de dados unificada resulta da integração e consolidação de três conjuntos de dados temporais consecutivos (**2024, 2025 e 2026**) provenientes do **Sistema de Informação de Agravos de Notificação (SINAN — Tema 10: Zika Vírus)** do Ministério da Saúde:
1. **`ZIKABR24.csv` (Ano Base 2024):** Contém as notificações e investigações epidemiológicas de Zika Vírus registradas no Brasil em $2024$ ($43.312$ linhas na extração bruta), distribuídas em $38$ colunas operacionais.
2. **`ZIKABR25.csv` (Ano Base 2025):** Contém os registros de notificações e investigações de Zika Vírus referentes ao período de $2025$, mantendo a estrutura de $38$ colunas da ficha de notificação individual do SINAN.
3. **`ZIKABR26.csv` (Ano Base 2026):** Contém os registros mais recentes de notificações de Zika Vírus em $2026$ ($38$ colunas), incluindo casos com investigação ainda em andamento.

### 1.1. Arquitetura do Esquema Estrela (*Star Schema*)

Para transformar as três tabelas operacionais anuais do SINAN (que possuem códigos numéricos truncados, datas dispersas e atributos mistos de paciente, localidade e investigação na mesma linha) em um repositório analítico de alto desempenho, foi projetado um **Data Warehouse modelado em Esquema Estrela (*Star Schema*)**.

A modelagem é composta por **1 Tabela Fato central** (`FATO_NOTIFICACAO_ZIKA`) cercada por **5 Tabelas Dimensão** (`DIM_TEMPO`, `DIM_LOCALIDADE_RESIDENCIA`, `DIM_UNIDADE_NOTIFICADORA`, `DIM_PACIENTE` e `DIM_INVESTIGACAO_DESFECHO`). A granularidade da tabela fato é o **caso individual notificado e consolidado no triênio 2024–2026**, contendo métricas aditivas e indicadores binários (*flags*) que permitem agregações rápidas por período, estado/município, perfil demográfico (como gestantes) e desfecho clínico.

### 1.2. Dicionário de Dados do Esquema Estrela

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
| **`DIM_TEMPO`** | `sk_tempo` (PK), `data_completa` (`DATE`), `ano` (`INT`), `mes` (`INT`), `nome_mes` (`VARCHAR`), `trimestre` (`INT`), `semana_epidemiologica` (`INT`), `periodo_sazonal` (`VARCHAR`) | Extraída de `DT_NOTIFIC`, `DT_SIN_PRI`, `NU_ANO` e `SEM_NOT`. Classifica os meses em `'Alta Transmissão (Jan-Mai)'` e `'Baixa Transmissão (Jun-Dez)'`. |
| **`DIM_LOCALIDADE`** | `sk_localidade` (PK), `cod_uf_ibge` (`INT`), `sigla_uf` (`CHAR(2)`), `nome_estado` (`VARCHAR`), `regiao_brasil` (`VARCHAR`), `cod_municipio_ibge6` (`INT`), `cod_regional_saude` (`INT`) | Extraída de `SG_UF`, `ID_MN_RESI` e `ID_RG_RESI`. Converte os códigos numéricos de UF do IBGE (`11` a `53`) em siglas (`RO` a `DF`), nomes de estados e macrorregiões. |
| **`DIM_UNIDADE_NOTIFICADORA`** | `sk_unidade` (PK), `cod_unidade_cnes` (`INT`), `cod_uf_notificacao` (`INT`), `sigla_uf_notificacao` (`CHAR(2)`), `cod_municipio_notificacao` (`INT`), `cod_regional_notificacao` (`INT`) | Extraída de `ID_UNIDADE`, `SG_UF_NOT`, `ID_MUNICIP` e `ID_REGIONA`. Permite cruzar o local de residência do paciente com o local efetivo de atendimento médico. |
| **`DIM_PACIENTE`** | `sk_paciente` (PK), `sexo` (`CHAR(1)`), `descricao_sexo` (`VARCHAR`), `idade_anos` (`INT`), `faixa_etaria` (`VARCHAR`), `raca_cor` (`VARCHAR`), `status_gestante` (`VARCHAR`), `escolaridade` (`VARCHAR`) | Decodifica `CS_SEXO`, `NU_IDADE_N` (convertido de código composto de 4 dígitos para anos e faixas etárias), `CS_RACA`, `CS_GESTANT` e `CS_ESCOL_N`. |
| **`DIM_INVESTIGACAO_DESFECHO`** | `sk_desfecho` (PK), `classificacao_final` (`VARCHAR`), `criterio_confirmacao` (`VARCHAR`), `evolucao_caso` (`VARCHAR`), `tipo_autoctonia` (`VARCHAR`), `doenca_trabalho` (`VARCHAR`) | Decodifica os domínios epidemiológicos de `CLASSI_FIN`, `CRITERIO`, `EVOLUCAO`, `TPAUTOCTO` e `DOENCA_TRA`. |

---

## 2. Explicação Detalhada do Processo de Integração

*(Nota para a Macroentrega 2: As Duplas 1 e 2 devem inserir aqui os prints intermediários da execução dos notebooks ETL e ELT).*

O processo de integração dos três arquivos anuais (`ZIKABR24.csv`, `ZIKABR25.csv` e `ZIKABR26.csv`) foi estruturado em quatro etapas:

1. **Coleta e Ingestão Unificada:** Leitura dos três arquivos CSV referentes aos anos de $2024$, $2025$ e $2026$, adicionando uma coluna de metadado de rastreabilidade (`arquivo_origem`) para identificar a qual extração anual cada registro pertence originalmente.
2. **Saneamento de Vazamento Temporal e Deduplicação Interanual:** No SINAN, a extração por ano epidemiológico frequentemente inclui registros da virada do ano seguinte (ex: registros com `NU_ANO = 2025` presentes dentro do arquivo `ZIKABR24.csv` devido à semana epidemiológica `SEM_NOT`). Durante a integração, os três conjuntos são consolidados e deduplicados para evitar dupla contagem de notificações na fronteira entre $2024/2025$ e $2025/2026$.
3. **Padronização e Decodificação de Domínios:** Conversão das variáveis codificadas numericamente (como `NU_IDADE_N`, `CS_GESTANT`, `CS_RACA`, `CLASSI_FIN`, `CRITERIO`, `EVOLUCAO` e `SG_UF`) em descrições analíticas legíveis para compor as dimensões.
4. **Geração de Chaves Substitutas (*Surrogate Keys*) e Carga Dimensional:** Povoamento das 5 tabelas dimensão com registros únicos e inserção dos eventos e métricas calculadas na tabela fato `FATO_NOTIFICACAO_ZIKA`.

---

## 3. Justificativa da Escolha da Base de Dados

A escolha da base de dados de **Zika Vírus do SINAN (Tema 10)** abrangendo os três anos consecutivos de **2024, 2025 e 2026** (`ZIKABR24.csv`, `ZIKABR25.csv` e `ZIKABR26.csv`) justifica-se por sua alta relevância epidemiológica nacional e regional, bem como pela aderência exemplar aos requisitos de integração temporal e modelagem dimensional da disciplina de Banco de Dados.

Do ponto de vista de saúde pública, o monitoramento contínuo do vírus Zika é prioritário no Brasil — e particularmente sensível em Pernambuco e no Nordeste — devido à associação direta entre a infecção aguda em gestantes e o desenvolvimento da Síndrome Congênita do Zika Vírus (incluindo microcefalia e alterações neuropsicomotoras). Analisar três anos consecutivos recentes ($2024$, $2025$ e $2026$) permite avaliar a dinâmica sazonal pós-pandemia, identificar estados com recrudescimento de transmissão e verificar a agilidade da rede de vigilância na confirmação laboratorial de casos em gestantes.

Do ponto de vista técnico de Engenharia de Dados, os arquivos anuais do SINAN exigem transformações não triviais que evidenciam as diferenças práticas entre **ETL** e **ELT**:
1. **Codificação Composta de Atributos:** A idade (`NU_IDADE_N`) utiliza uma máscara numérica posicional de 4 dígitos que mistura unidades de tempo (horas, dias, meses e anos) com o valor numérico, exigindo lógica condicional e aritmética para extração da idade real.
2. **Anomalias de Fronteira Temporal entre Arquivos Anuais:** Os arquivos separados por ano apresentam sobreposição de semanas epidemiológicas e variações significativas na taxa de preenchimento de campos de encerramento (`CLASSI_FIN`, `DT_ENCERRA`, `EVOLUCAO`) conforme o ano se aproxima do período atual ($2026$).
3. **Riqueza Dimensional Implícita:** Uma única tabela desnormalizada de $38$ colunas oculta múltiplas entidades distintas (Tempo de Notificação, Tempo de Sintomas, Local de Residência, Unidade de Saúde Notificadora, Paciente e Investigação), tornando a decomposição em Esquema Estrela altamente didática e eficiente.

---

## 4. Descrição dos Processos de Transformação Aplicados

*(Nota para a Macroentrega 2: Inserir prints do código e resultados intermediários das 5 transformações abaixo).*

Para garantir a qualidade e a consistência dos dados integrados nos pipelines ETL e ELT, foram aplicadas cinco transformações principais:

1. **Consolidação Interanual e Tratamento de Vazamento de Ano (`NU_ANO`):**
   * **Problema:** O arquivo `ZIKABR24.csv` contém $69$ registros cujo `NU_ANO` já pertence a $2025$ (notificados nos últimos dias de dezembro/primeira semana epidemiológica), fenômeno que se repete nas fronteiras de `ZIKABR25.csv` e `ZIKABR26.csv`.
   * **Transformação:** Unificação dos três arquivos com padronização do ano real a partir de `DT_NOTIFIC` e remoção de eventuais registros duplicados na transição entre anos.
2. **Decodificação da Idade (`NU_IDADE_N`) e Expurgo de Outliers ($> 120\text{ anos}$):**
   * **Problema:** O campo `NU_IDADE_N` codifica no $1^{\circ}$ dígito a unidade ($1=\text{Hora}$, $2=\text{Dia}$, $3=\text{Mês}$, $4=\text{Ano}$) e nos $3$ dígitos seguintes a quantidade (ex: `4031` $= 31\text{ anos}$; `3008` $= 8\text{ meses}$). Além disso, há registros com idades extremas/inválidas ou divergentes de `ANO_NASC`.
   * **Transformação:** Códigos $< 4000$ foram convertidos para `idade_anos = 0` (menores de 1 ano); códigos $\ge 4000$ tiveram $4000$ subtraído (`NU_IDADE_N - 4000`); valores resultantes $> 120\text{ anos}$ foram tratados como `NULL` e classificados na faixa etária `'Ignorado'`.
3. **Conversão de Tipagem (`Float` $\rightarrow$ `Int`) e Tratamento de Valores Ausentes/Ignorados:**
   * **Problema:** Devido à presença de células vazias (`NaN`), colunas categóricas inteiras como `CLASSI_FIN`, `CRITERIO`, `EVOLUCAO`, `CS_GESTANT`, `CS_RACA` e `ID_MN_RESI` são lidas como números de ponto flutuante (`1.0`, `2.0`, `9.0`), e a proporção de nulos cresce nos arquivos mais recentes ($2025$ e $2026$) por conterem casos ainda em investigação.
   * **Transformação:** Conversão segura para inteiro e mapeamento de valores ausentes (`NULL`/`NaN`) ou códigos `9` para categorias explícitas (`'Em Investigação / Não Preenchido'` ou `'Ignorado'`), preservando os registros na Tabela Fato sem perda de notificações.
4. **Decodificação Geográfica Completa (Código IBGE $\rightarrow$ UF, Estado e Região):**
   * **Problema:** As UFs de notificação (`SG_UF_NOT`) e de residência (`SG_UF`) estão representadas apenas por códigos numéricos de 2 dígitos do IBGE (`11` a `53`).
   * **Transformação:** Aplicação de dicionário/tabela de mapeamento para enriquecer a `DIM_LOCALIDADE` e a `DIM_UNIDADE_NOTIFICADORA` com a sigla da UF (`RO` a `DF`), o nome completo do estado e a macrorregião geográfica (Norte, Nordeste, Centro-Oeste, Sudeste e Sul).
5. **Cálculo e Saneamento de Métricas de Tempo de Vigilância (`qt_dias_atraso_notif` e `qt_dias_encerramento`):**
   * **Problema:** Erros de digitação na ponta geram datas de primeiros sintomas (`DT_SIN_PRI`) posteriores à data de notificação (`DT_NOTIFIC`) ou com anos antigos incorretos (diferenças $> 365\text{ dias}$).
   * **Transformação:** Cálculo da diferença em dias corridos restringindo o intervalo válido a $[0, 365]\text{ dias}$; valores fora desse intervalo (negativos ou extremos) foram convertidos para `NULL` para não distorcer a média e o desvio padrão nas análises.

---

## 5. Comparativo entre ETL e ELT

*(Nota para a Macroentrega 3: Preencher os tempos medidos na execução dos notebooks no Google Colab).*

| Critério Analisado | Pipeline ETL (Python / Pandas $\rightarrow$ BD) | Pipeline ELT (Carga Staging $\rightarrow$ SQL no SGBD) |
| :--- | :--- | :--- |
| **Fluxo de Processamento** | Os 3 CSVs (`2024`, `2025`, `2026`) são lidos, limpos e modelados em *DataFrames* no Pandas antes de inserir no banco. | Os 3 CSVs são carregados diretamente em tabelas brutas (`stg_zika_2024`, `stg_zika_2025`, `stg_zika_2026`) e transformados via SQL. |
| **Decodificação de Domínios (`NU_IDADE_N`, `CS_GESTANT`, UF)** | Realizada via funções vetorizadas do Pandas (`.map()`, `np.select()`). Muito intuitiva para limpeza de tipos mistos. | Realizada via expressões declarativas `CASE WHEN` e `COALESCE` diretamente nas queries `INSERT INTO ... SELECT`. |
| **Deduplicação e Geração de Dimensões** | Exige `.drop_duplicates()` em memória e controle manual de índices para gerar as *Surrogate Keys* (`sk_`). | O próprio SGBD garante unicidade via `DISTINCT` / `GROUP BY` e chaves `AUTOINCREMENT` / `ROW_NUMBER()`. |
| **Reprocessamento e Auditoria** | Qualquer mudança em regra de negócio exige reler os CSVs do disco e rodar todo o script Python novamente. | Como os dados brutos já estão persistidos nas tabelas *Staging* do banco, basta reexecutar o script SQL em poucos segundos. |
| **Tempo Total de Execução (Colab)** | `[Inserir tempo medido na Macroentrega 3]` | `[Inserir tempo medido na Macroentrega 3]` |

---

## 6. Apresentação de Três Análises e Insights

*(Nota para a Macroentrega 3: A Dupla 3 deve inserir aqui os gráficos gerados pelo notebook/SQL das 3 análises abaixo).*

### Análise 1: Evolução Temporal, Sazonalidade e Taxa de Confirmação no Triênio (2024–2026)
* **Objetivo da Análise:** Comparar a curva mensal e trimestral de notificações de Zika Vírus nos anos de $2024$, $2025$ e $2026$, avaliando a concentração sazonal nos meses chuvosos ($1^{\circ}$ semestre) e a evolução da proporção de casos Confirmados (`CLASSI_FIN = 1`), Descartados (`CLASSI_FIN = 2`) e Inconclusivos/Em Investigação (`CLASSI_FIN = 8` ou `NULL`).
* **Referência da Base de 2024:** Em $2024$, das $43.312$ notificações, $7.136$ ($16,5\%$) foram confirmadas, $23.163$ ($53,5\%$) descartadas e $13.013$ ($30,0\%$) permaneceram inconclusivas ou sem preenchimento, com pico concentrado entre fevereiro e maio.
* **Insight Obtido:** A comparação entre os três anos demonstra o efeito do ciclo sazonal do *Aedes aegypti* (concentração massiva nos dois primeiros trimestres do ano) e evidencia como a proporção de casos sem classificação final (`NULL`/`Inconclusivo`) aumenta nos anos mais recentes ($2025$ e $2026$) devido ao represamento laboratorial de sorologias no SINAN.

### Análise 2: Monitoramento de Grupo de Risco Prioritário — Gestantes e Perfil Sociodemográfico por UF (2024–2026)
* **Objetivo da Análise:** Investigar a distribuição dos casos notificados e confirmados de Zika Vírus segundo sexo, faixa etária, raça/cor e **condição gestacional (`fl_gestante = 1`)** entre as Unidades da Federação e Regiões do Brasil.
* **Referência Estatística:** Na série analisada, a idade média dos pacientes gira em torno de $33,19\text{ anos}$ ($\text{mediana} = 31\text{ anos}$, $\text{DP} = 19,30$), com forte predominância do sexo feminino ($\approx 61,9\%$) e expressivo volume de notificações em gestantes ($4.159$ gestantes notificadas apenas em $2024$). Estados do Sudeste (ES, MG), Nordeste (BA, PE, RN, CE) e Centro-Oeste (MT) concentram os maiores volumes absolutos.
* **Insight Obtido:** A sobrerrepresentação feminina na faixa de $20\text{ a }39\text{ anos}$ é diretamente explicada pelos protocolos obrigatórios de triagem pré-natal implantados após a epidemia de microcefalia: enquanto homens adultos com sintomas leves frequentemente não procuram unidades de saúde, gestantes são sistematicamente notificadas e submetidas ao critério laboratorial.

### Análise 3: Eficiência da Vigilância Epidemiológica — Atraso de Notificação, Tempo de Encerramento e Mobilidade de Atendimento
* **Objetivo da Análise:** Avaliar a agilidade do sistema de saúde por estado e região através de três indicadores: (i) atraso entre primeiros sintomas e notificação (`qt_dias_atraso_notif`), (ii) tempo até o encerramento da investigação (`qt_dias_encerramento`) e (iii) proporção de pacientes atendidos fora do seu município de residência (`DIM_LOCALIDADE.cod_municipio_ibge6 != DIM_UNIDADE_NOTIFICADORA.cod_municipio_notificacao`).
* **Referência Estatística:** O atraso até a notificação apresenta mediana de $3,0\text{ dias}$, porém média de $5,68\text{ dias}$ ($\text{DP} = 12,39$), puxada por notificações digitadas tardiamente em mutirões de vigilância.
* **Insight Obtido:** Municípios do interior sem laboratório próprio apresentam maior tempo de encerramento da investigação e maior deslocamento de pacientes (especialmente gestantes) para unidades notificadoras localizadas nas capitais e sedes de Regionais de Saúde.

---

## 7. Reflexão sobre o Aprendizado

*(Nota para a Macroentrega 4: Revisar com todo o grupo antes da entrega final em 18/11).*

O desenvolvimento deste projeto permitiu ao grupo vivenciar na prática os desafios reais da construção de um Data Warehouse a partir de microdados governamentais de saúde pública (SINAN/DataSUS). Os principais aprendizados incluem:

1. **Compreensão Profunda das Anomalias em Séries Históricas Reais:** Mesmo trabalhando com uma única fonte temática (Zika Vírus) em três anos consecutivos ($2024$, $2025$ e $2026$), verificamos que dados brutos exigem intenso saneamento devido a vazamentos de semanas epidemiológicas entre arquivos anuais, campos numéricos lidos como *float* por presença de nulos e códigos compostos legados (como `NU_IDADE_N`).
2. **Desnormalização Consciente no Esquema Estrela:** A separação da tabela única do SINAN em cinco dimensões (`DIM_TEMPO`, `DIM_LOCALIDADE`, `DIM_UNIDADE_NOTIFICADORA`, `DIM_PACIENTE` e `DIM_INVESTIGACAO_DESFECHO`) e uma tabela fato central tornou as consultas analíticas das três análises muito mais legíveis, rápidas e semânticas.
3. **Domínio Prático de ETL vs. ELT:** A implementação paralela dos dois pipelines deixou claro como o **ETL em Python/Pandas** facilita a manipulação imperativa de tipos e strings na memória, enquanto o **ELT em SQL** brilha pela simplicidade declarativa, velocidade de agregação em conjunto (*set-based operations*) e manutenção das tabelas *Staging* para auditoria.