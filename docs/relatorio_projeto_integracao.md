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

A modelagem é composta por **1 Tabela Fato central** (`FATO_NOTIFICACAO_ZIKA`) cercada por **5 Tabelas Dimensão** (`DIM_TEMPO`, `DIM_LOCALIDADE`, `DIM_UNIDADE_NOTIFICADORA`, `DIM_PACIENTE` e `DIM_INVESTIGACAO_DESFECHO`). A granularidade da tabela fato é a **linha válida distinta nos 38 campos brutos das extrações do triênio 2024–2026**, contendo métricas aditivas e indicadores binários (*flags*) que permitem agregações rápidas por período, estado/município, perfil demográfico (como gestantes) e desfecho clínico.

### 1.2. Dicionário de Dados

O dicionário completo, os tipos, as origens e as regras dos dois pipelines estão no
[arquivo próprio do dicionário](dicionario_de_dados_e_mapeamento_de_divergencias.md).
O contrato executável é [`pipelines/contrato.json`](../pipelines/contrato.json) e o
DDL compartilhado é [`sql/01_script_ddl_do_esquema_estrela.sql`](../sql/01_script_ddl_do_esquema_estrela.sql).

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

Os dois pipelines seguem as mesmas regras do [dicionário de dados](dicionario_de_dados_e_mapeamento_de_divergencias.md).
O ETL transforma e modela em Python/Pandas antes da carga no MySQL; o ELT carrega o texto bruto
no MySQL e transforma por consultas SQL gerenciadas pelo dbt. A publicação usa o mesmo DDL,
com cinco dimensões e a fato `fato_notificacao_zika`.

1. Extração dos três CSVs, preservando os 38 campos e registrando arquivo e linha de origem.
2. Remoção apenas de duplicatas exatas nos 38 campos brutos, independentemente do arquivo anual.
   Sem identificador único de notificação, registros com diferenças de conteúdo são preservados.
3. Validação da data real de notificação. Datas obrigatórias inválidas vão à quarentena;
   datas opcionais inválidas tornam-se nulas. O ano é derivado de `DT_NOTIFIC`.
4. Conversão dos códigos numéricos (inclusive texto como `26.0`), decodificação dos domínios
   e idade em anos inteiros; faixas: 0–14, 15–29, 30–44, 45–59, 60+ e Ignorado.
5. Cálculo dos intervalos de notificação e encerramento, mantendo apenas valores de 0 a 365 dias.
   Classificações ausentes permanecem em investigação; `fl_obito_zika` considera apenas `EVOLUCAO=2`.
6. Geração das dimensões, chaves e fatos, seguida de publicação transacional e validação de integridade.

A entrada versionada contém **82.460 linhas**; a deduplicação exata remove **56**, resultando
em **82.404 notificações válidas**, sem rejeições por data de notificação nesta versão dos CSVs.
Valores antigos do relatório calculados sobre a base sem deduplicação precisam ser recalculados
no [notebook de análises](../notebooks/analises_zika.ipynb).

---

## 5. Comparativo entre ETL e ELT

*(Nota para a Macroentrega 3: Preencher os tempos medidos na execução dos notebooks no Google Colab).*

| Critério Analisado | Pipeline ETL (Python / Pandas $\rightarrow$ BD) | Pipeline ELT (Carga Staging $\rightarrow$ SQL no SGBD) |
| :--- | :--- | :--- |
| **Fluxo de Processamento** | Os 3 CSVs (`2024`, `2025`, `2026`) são lidos, limpos e modelados em *DataFrames* no Pandas antes de inserir no banco. | Os 3 CSVs são carregados diretamente em tabelas brutas (`stg_zika`, com arquivo e linha de origem) e transformados via SQL. |
| **Decodificação de Domínios (`NU_IDADE_N`, `CS_GESTANT`, UF)** | Realizada via funções vetorizadas do Pandas (`.map()`, `np.select()`). Muito intuitiva para limpeza de tipos mistos. | Realizada via expressões declarativas `CASE WHEN` e `COALESCE` diretamente nas queries `INSERT INTO ... SELECT`. |
| **Deduplicação e Geração de Dimensões** | Exige `.drop_duplicates()` em memória e controle manual de índices para gerar as *Surrogate Keys* (`sk_`). | O próprio SGBD garante unicidade via `DISTINCT` / `GROUP BY` e chaves `ROW_NUMBER()`. |
| **Reprocessamento e Auditoria** | Qualquer mudança em regra de negócio exige reler os CSVs do disco e rodar todo o script Python novamente. | Como os dados brutos já estão persistidos nas tabelas *Staging* do banco, basta reexecutar o script SQL em poucos segundos. |
| **Tempo Total de Execução (Colab)** | `[Inserir tempo medido na Macroentrega 3]` | `[Inserir tempo medido na Macroentrega 3]` |

---

## 6. Apresentação de Três Análises e Insights

As consultas, gráficos e exportações estão em [`notebooks/analises_zika.ipynb`](../notebooks/analises_zika.ipynb),
executado após ETL ou ELT. Os pipelines contêm apenas reconciliação e validações operacionais.

1. **Sazonalidade:** evolução mensal de notificações por ano real de `DT_NOTIFIC`.
2. **Gestantes:** notificações e confirmações por UF de residência, incluindo a categoria NI.
3. **Vigilância:** médias de atraso de notificação e tempo de encerramento por região,
   considerando apenas intervalos válidos de 0 a 365 dias.

Os gráficos são exportados para `saidas/analises/`. As conclusões devem ser registradas após
executar as análises sobre a versão atual, sem reutilizar estatísticas da carga anterior.
2026 é parcial; contagens absolutas de notificações não medem incidência populacional.

---

## 7. Reflexão sobre o Aprendizado

*(Nota para a Macroentrega 4: Revisar com todo o grupo antes da entrega final em 18/11).*

O desenvolvimento deste projeto permitiu ao grupo vivenciar na prática os desafios reais da construção de um Data Warehouse a partir de microdados governamentais de saúde pública (SINAN/DataSUS). Os principais aprendizados incluem:

1. **Compreensão Profunda das Anomalias em Séries Históricas Reais:** Mesmo trabalhando com uma única fonte temática (Zika Vírus) em três anos consecutivos ($2024$, $2025$ e $2026$), verificamos que dados brutos exigem intenso saneamento devido a vazamentos de semanas epidemiológicas entre arquivos anuais, campos numéricos lidos como *float* por presença de nulos e códigos compostos legados (como `NU_IDADE_N`).
2. **Desnormalização Consciente no Esquema Estrela:** A separação da tabela única do SINAN em cinco dimensões (`DIM_TEMPO`, `DIM_LOCALIDADE`, `DIM_UNIDADE_NOTIFICADORA`, `DIM_PACIENTE` e `DIM_INVESTIGACAO_DESFECHO`) e uma tabela fato central tornou as consultas analíticas das três análises muito mais legíveis, rápidas e semânticas.
3. **Domínio Prático de ETL vs. ELT:** A implementação paralela dos dois pipelines deixou claro como o **ETL em Python/Pandas** facilita a manipulação imperativa de tipos e strings na memória, enquanto o **ELT em SQL** brilha pela simplicidade declarativa, velocidade de agregação em conjunto (*set-based operations*) e manutenção das tabelas *Staging* para auditoria.