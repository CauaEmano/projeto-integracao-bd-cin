# Universidade Federal de Pernambuco
## Centro de Informática - CIn

**Integrantes (Nome - login):**
* Nome Integrante 1 - `login1@cin.ufpe.br`
* Nome Integrante 2 - `login2@cin.ufpe.br`
* Nome Integrante 3 - `login3@cin.ufpe.br`
* Nome Integrante 4 - `login4@cin.ufpe.br`
* Nome Integrante 5 - `login5@cin.ufpe.br`
* Nome Integrante 6 - `login6@cin.ufpe.br`

**TEMA:** Vigilância Epidemiológica de Arboviroses (Zika Vírus e Febre de Chikungunya) e Produção Científica em Saúde no Brasil (2024–2026)

---

# Relatório do Projeto de Integração — Banco de Dados

---

## 1. Descrição da Base de Dados Unificada (Modelagem Dimensional e Dicionário de Dados)

A base de dados unificada resulta da consolidação de três fontes governamentais abertas do Ministério da Saúde que abrangem o triênio consecutivo de **2024, 2025 e 2026**, totalizando **$362.729$ registros brutos**:
1. **`ZIKABR24.csv` (SINAN — 2024):** Contém $43.312$ notificações de casos suspeitos e confirmados de Zika Vírus no Brasil, estruturadas originalmente em $38$ atributos ($6,56\text{ MB}$, codificação `UTF-8`, delimitador `,`).
2. **`CHIKBR25.csv` (SINAN — 2025):** Contém $253.753$ notificações de Febre de Chikungunya no Brasil, estruturadas em $122$ atributos ($67,12\text{ MB}$, codificação `UTF-8`, delimitador `,`), incluindo variáveis clínicas de sintomas, comorbidades e hospitalização.
3. **`plataforma_brasil_2026.csv` (Plataforma Brasil — 2026):** Contém $65.664$ registros de pareceres éticos de pesquisas científicas envolvendo seres humanos no Brasil, estruturados em $26$ atributos ($37,90\text{ MB}$, codificação `ISO-8859-1`, delimitador `|`). Deste total, $3.519$ projetos concentram-se em doenças infecciosas e epidemiologia, sendo $258$ voltados especificamente a arboviroses (Zika, Chikungunya, Dengue, *Aedes aegypti* e Microcefalia).

### 1.1. Arquitetura do Esquema Estrela (*Star Schema*)

Para viabilizar consultas analíticas complexas que cruzem a pressão epidemiológica das arboviroses com a resposta científica das instituições de pesquisa ao longo do tempo e do território nacional, o Data Warehouse foi modelado em **Esquema Estrela (*Star Schema*)**, composto por **1 Tabela Fato central** (`FATO_VIGILANCIA_E_PESQUISA`) e **5 Tabelas Dimensão** (`DIM_TEMPO`, `DIM_LOCALIDADE`, `DIM_AGRAVO_CID`, `DIM_PACIENTE` e `DIM_PESQUISA_CEP`).

A granularidade da tabela fato foi definida ao nível do **evento individual padronizado** (seja uma notificação epidemiológica do SINAN ou um protocolo de pesquisa avaliado na Plataforma Brasil), garantindo rastreabilidade máxima sem perda de detalhamento demográfico ou institucional. Quando o registro corresponde a uma notificação clínica do SINAN, a chave estrangeira para `DIM_PESQUISA_CEP` aponta para o registro dimensional padrão `sk_pesquisa = 0` (*"Não Aplicável — Notificação Epidemiológica"*); de modo simétrico, quando o evento é um projeto da Plataforma Brasil, a chave para `DIM_PACIENTE` aponta para `sk_paciente = 0` (*"Não Aplicável — Protocolo de Pesquisa"*).

### 1.2. Dicionário de Dados do Esquema Estrela

#### Tabela Fato: `FATO_VIGILANCIA_E_PESQUISA`
| Atributo | Tipo de Dado | Restrição | Descrição e Metadados Relevantes |
| :--- | :--- | :--- | :--- |
| `sk_evento_fato` | `INTEGER` | `PRIMARY KEY` | Identificador único substituto (*Surrogate Key*) do registro na tabela fato. |
| `fk_tempo` | `INTEGER` | `FOREIGN KEY` | Referência à `DIM_TEMPO` no formato `YYYYMMDD` (data da notificação ou data do parecer ético). |
| `fk_localidade` | `INTEGER` | `FOREIGN KEY` | Referência à `DIM_LOCALIDADE` (UF e município de ocorrência/proponência). |
| `fk_agravo_cid` | `INTEGER` | `FOREIGN KEY` | Referência à `DIM_AGRAVO_CID` (classificação CID-10 do agravo ou área temática da pesquisa). |
| `fk_perfil_paciente` | `INTEGER` | `FOREIGN KEY` | Referência à `DIM_PACIENTE` (`0` para protocolos da Plataforma Brasil). |
| `fk_protocolo_pesquisa` | `INTEGER` | `FOREIGN KEY` | Referência à `DIM_PESQUISA_CEP` (`0` para notificações do SINAN). |
| `qt_notificacao_zika` | `INTEGER` | `NOT NULL` | Indicador aditivo ($1$ para caso notificado de Zika Vírus; $0$ caso contrário). |
| `qt_notificacao_chik` | `INTEGER` | `NOT NULL` | Indicador aditivo ($1$ para caso notificado de Chikungunya; $0$ caso contrário). |
| `qt_caso_confirmado` | `INTEGER` | `NOT NULL` | Indicador aditivo ($1$ quando `CLASSI_FIN` confirma o agravo clínica ou laboratorialmente; $0$ caso contrário). |
| `qt_hospitalizacao` | `INTEGER` | `NOT NULL` | Indicador aditivo ($1$ quando houve internação hospitalar registrada em `HOSPITALIZ = 1`; $0$ caso contrário). |
| `qt_dias_atraso_notif` | `INTEGER` | `NULLABLE` | Diferença em dias corridos entre a data dos primeiros sintomas (`DT_SIN_PRI`) e a data da notificação (`DT_NOTIFIC`). |
| `qt_pesquisa_aprovada` | `INTEGER` | `NOT NULL` | Indicador aditivo ($1$ para projeto com `situacao_do_parecer = 'Aprovado'`; $0$ caso contrário). |
| `nu_versao_projeto` | `INTEGER` | `NULLABLE` | Quantidade de submissões/versões éticas do protocolo de pesquisa (`versao_projeto`). |

#### Tabelas Dimensão (`DIM_TEMPO`, `DIM_LOCALIDADE`, `DIM_AGRAVO_CID`, `DIM_PACIENTE`, `DIM_PESQUISA_CEP`)
| Tabela Dimensão | Atributos (Colunas) | Descrição e Origem dos Metadados |
| :--- | :--- | :--- |
| **`DIM_TEMPO`** | `sk_tempo` (PK), `data_completa` (`DATE`), `ano` (`INT`), `mes` (`INT`), `nome_mes` (`VARCHAR`), `trimestre` (`INT`), `semana_epidemiologica` (`INT`) | Consolida as datas de `DT_NOTIFIC` / `SEM_NOT` (SINAN 2024 e 2025) e `data_do_parecer` (Plataforma Brasil 2026), permitindo análises de sazonalidade e evolução temporal. |
| **`DIM_LOCALIDADE`** | `sk_localidade` (PK), `sigla_uf` (`CHAR(2)`), `cod_uf_ibge` (`INT`), `nome_estado` (`VARCHAR`), `regiao_brasil` (`VARCHAR`), `cod_municipio_ibge6` (`INT`), `nome_municipio` (`VARCHAR`) | Unifica a codificação numérica IBGE do SINAN (`SG_UF_NOT`, `ID_MUNICIP`) com as siglas estaduais e nomes municipais da Plataforma Brasil (`uf_proponente`, `uf_cep`, `municipio_proponente`). |
| **`DIM_AGRAVO_CID`** | `sk_agravo_cid` (PK), `codigo_cid10` (`VARCHAR`), `nome_condicao` (`VARCHAR`), `categoria_arbovirose` (`VARCHAR`), `fonte_origem` (`VARCHAR`) | Padroniza os códigos `A92.8` (Zika Vírus), `A92.0` (Chikungunya) e mapeia os descritores de `descritores_cid_especificos` e `condicoes_de_saude_ou_problemas_estudados` da Plataforma Brasil. |
| **`DIM_PACIENTE`** | `sk_paciente` (PK), `sexo` (`CHAR(1)`), `idade_anos` (`INT`), `faixa_etaria` (`VARCHAR`), `raca_cor` (`VARCHAR`), `status_gestante` (`VARCHAR`), `evolucao_caso` (`VARCHAR`) | Decodifica os domínios epidemiológicos do SINAN: `NU_IDADE_N` (convertido para idade em anos e faixas etárias), `CS_SEXO`, `CS_RACA`, `CS_GESTANT` e `EVOLUCAO`. |
| **`DIM_PESQUISA_CEP`** | `sk_pesquisa` (PK), `numero_caae` (`VARCHAR`), `tipo_estudo` (`VARCHAR`), `tipo_centro` (`VARCHAR`), `instituicao_proponente` (`VARCHAR`), `nome_cep` (`VARCHAR`), `situacao_parecer` (`VARCHAR`) | Armazena os metadados institucionais e regulatórios dos projetos submetidos à Plataforma Brasil em 2026. |

---

## 2. Explicação Detalhada do Processo de Integração

*(Nota para a Macroentrega 2: As Duplas 1 e 2 devem inserir aqui os prints intermediários da execução dos notebooks ETL e ELT, complementando o fluxo estruturado abaixo).*

O processo de integração foi dividido em quatro etapas sistemáticas, desde a ingestão dos arquivos brutos até a carga consolidada no Esquema Estrela:

1. **Coleta e Ingestão Heterogênea:**
   * Leitura das bases do SINAN (`ZIKABR24.csv` e `CHIKBR25.csv`) utilizando codificação `UTF-8` e separador de vírgula (`,`).
   * Leitura da base `plataforma_brasil_2026.csv` utilizando codificação `ISO-8859-1 (latin1)` e separador pipe (`|`), contornando falhas de decodificação de acentos nos títulos e instituições brasileiras.
2. **Alinhamento de Esquema (*Schema Alignment*) e Evolução Temporal:**
   * Tratamento da diferença estrutural entre a base de Zika de 2024 ($38$ colunas) e a de Chikungunya de 2025 ($122$ colunas), selecionando os atributos comuns de vigilância e preservando indicadores clínicos relevantes (como `HOSPITALIZ`).
3. **Resolução de Entidades Geográficas e Temporais:**
   * Aplicação da tabela de mapeamento IBGE para converter os códigos estaduais numéricos de 2 dígitos do SINAN (ex: `26` $\rightarrow$ `PE`, `35` $\rightarrow$ `SP`, `51` $\rightarrow$ `MT`) na mesma chave alfanumérica utilizada pela Plataforma Brasil.
4. **Consolidação nas Dimensões e Carga na Tabela Fato:**
   * Geração das chaves substitutas (*Surrogate Keys*) para as 5 dimensões e povoamento da `FATO_VIGILANCIA_E_PESQUISA` com $362.726$ registros válidos (após expurgo das $3$ linhas corrompidas na origem da Plataforma Brasil).

---

## 3. Justificativa da Escolha da Base de Dados

A escolha dos conjuntos de dados de **Zika Vírus (`ZIKABR24.csv`, 2024)**, **Febre de Chikungunya (`CHIKBR25.csv`, 2025)** e **Plataforma Brasil (`plataforma_brasil_2026.csv`, 2026)** fundamenta-se em dois eixos centrais: **relevância socioepidemiológica** e **riqueza de desafios para a Engenharia de Dados**.

Sob a perspectiva de saúde pública e gestão científica, o Brasil enfrenta epidemias recorrentes de arboviroses transmitidas pelo vetor *Aedes aegypti*, com impactos severos que incluem desde quadros articulares crônicos incapacitantes (Chikungunya) até a Síndrome Congênita associada à infecção pelo vírus Zika em gestantes — tema de importância histórica para o estado de Pernambuco e para a Região Nordeste. Ao integrar os microdados de vigilância epidemiológica de 2024 e 2025 com a base nacional de pesquisas envolvendo seres humanos de 2026, o Data Warehouse permite investigar uma questão estratégica inédita: **a distribuição regional e temática das pesquisas científicas aprovadas nos Comitês de Ética no Brasil reflete a real carga epidemiológica dos surtos de arboviroses nas Unidades da Federação?**

Sob a perspectiva técnica da disciplina de Banco de Dados, a tríade escolhida oferece um laboratório real e desafiador para contrastar as arquiteturas **ETL** e **ELT**:
1. **Volume Expressivo e Assimetria:** As três bases totalizam $362.729$ linhas e mais de $111\text{ MB}$ de dados brutos, exigindo otimização de memória no Google Colab e operações vetoriais/relacionais eficientes.
2. **Evolução de Esquema entre Anos Consecutivos:** Mesmo pertencendo ao mesmo sistema de origem (SINAN), a estrutura de 2024 (`ZIKABR24`) possui $38$ colunas, enquanto a de 2025 (`CHIKBR25`) expande para $122$ colunas, além de apresentar diferenças nos códigos de classificação final (`CLASSI_FIN`).
3. **Heterogeneidade Sintática e Semântica:** As fontes utilizam codificações de caracteres distintas (`UTF-8` vs. `ISO-8859-1`), delimitadores diferentes (`,` vs. `|`), formatos de data variados (`YYYY-MM-DD` vs. `YYYY/MM/DD HH:MM:SS`) e chaves geográficas incompatíveis na origem (código numérico IBGE vs. sigla textual de UF).

---

## 4. Descrição dos Processos de Transformação Aplicados

*(Nota para a Macroentrega 2: Inserir trechos de código Python/SQL e prints do "antes e depois" de cada uma das 5 transformações abaixo).*

Para assegurar a qualidade, integridade referencial e consistência analítica do Data Warehouse, foram implementadas cinco regras principais de transformação (tanto via Python/Pandas no pipeline ETL quanto via SQL no pipeline ELT):

1. **Saneamento de Linhas Deslocadas e Recuperação de UF na Plataforma Brasil (2026):**
   * **Problema identificado:** A inspeção da base `plataforma_brasil_2026.csv` revelou $3$ registros corrompidos por quebra indevida de delimitador (onde a coluna `uf_proponente` continha o número `'68'` e `situacao_do_parecer` continha o e-mail `'cappesq.adm@hc.fm.usp.br'`), além de $1.365$ registros com `uf_proponente` nulo (`NaN`).
   * **Transformação aplicada:** Filtragem e descarte das $3$ linhas estruturalmente corrompidas e aplicação de regra de *coalesce* (`COALESCE(uf_proponente, uf_cep)`) para recuperar a UF a partir da localização do Comitê de Ética em $1.365$ projetos.
2. **Decodificação Composta de Idade (`NU_IDADE_N`) e Tratamento de *Outliers* ($\text{Idade} > 120$ anos):**
   * **Problema identificado:** No SINAN, a coluna `NU_IDADE_N` armazena um código de 4 dígitos onde o primeiro dígito define a unidade de tempo ($1 = \text{Hora}$, $2 = \text{Dia}$, $3 = \text{Mês}$, $4 = \text{Ano}$) e os três últimos definem o valor. Na base `CHIKBR25.csv`, foram detectados **$10$ registros com erros graves de digitação** (valores como `4829` e `4401`, que decodificam para idades biologicamente impossíveis de **$829$ anos** e **$401$ anos**).
   * **Transformação aplicada:** Conversão matemática dos códigos iniciados em $1, 2 \text{ e } 3$ para $0$ anos (menores de 1 ano), subtração de $4000$ para códigos iniciados em $4$, e higienização (*capping/nullifying*) convertendo qualquer idade decodificada $> 120$ anos para `NULL` (Faixa Etária = `'Ignorado'`).
3. **Unificação e Padronização Geográfica (De-Para IBGE $\leftrightarrow$ Sigla UF):**
   * **Problema identificado:** `ZIKABR24` e `CHIKBR25` identificam os estados por códigos numéricos do IBGE (`11` a `53`), enquanto `plataforma_brasil_2026` utiliza siglas de 2 letras (`RO` a `DF`).
   * **Transformação aplicada:** Mapeamento relacional unificando todas as fontes na `DIM_LOCALIDADE` com sigla da UF, código IBGE, nome do estado e macrorregião brasileira (Norte, Nordeste, Centro-Oeste, Sudeste, Sul).
4. **Cálculo de Atraso de Notificação e Limpeza de Datas:**
   * **Problema identificado:** Datas em formatos distintos (`YYYY-MM-DD` no SINAN e `YYYY/MM/DD HH:MM:SS.000000000` na Plataforma Brasil) e diferenças extremas ou negativas entre a data dos primeiros sintomas (`DT_SIN_PRI`) e a notificação (`DT_NOTIFIC`).
   * **Transformação aplicada:** Padronização ISO para `DATE`, geração da chave inteira `YYYYMMDD` para `DIM_TEMPO` e cálculo de `qt_dias_atraso_notif`, restringindo ao intervalo válido de $[0, 365]$ dias.
5. **Classificação Temática de Pesquisas em Arboviroses e Infectologia via Expressões Regulares:**
   * **Problema identificado:** Na Plataforma Brasil, os campos `condicoes_de_saude_ou_problemas_estudados` e `descritores_cid_especificos` são textos livres semiestruturados.
   * **Transformação aplicada:** Categorização textual identificando os $258$ estudos focados diretamente em Arboviroses (`Zika`, `Chikungunya`, `Dengue`, `Aedes`, `Microcefalia`, `A90`, `A92`) e os $3.519$ estudos de Infectologia/Vigilância para vínculo direto na `DIM_AGRAVO_CID`.

---

## 5. Comparativo entre ETL e ELT

*(Nota para a Macroentrega 3: Preencher os tempos medidos no Google Colab na tabela abaixo).*

| Critério de Avaliação | Pipeline ETL (Python / Pandas $\rightarrow$ BD) | Pipeline ELT (Carga Bruta $\rightarrow$ SQL no SGBD) |
| :--- | :--- | :--- |
| **Local da Transformação** | Em memória RAM no ambiente Google Colab utilizando *DataFrames* do `pandas`. | Dentro do motor relacional do SGBD utilizando queries SQL (`CASE WHEN`, `JOIN`, `COALESCE`). |
| **Tratamento de Arquivos Sujos (`latin1` / linhas deslocadas)** | **Mais vantajoso:** O `pandas` trata erros de *parsing*, delimitadores quebrados e *regex* textual antes de tocar no banco. | **Mais trabalhoso:** Exige carregar colunas como `TEXT` genérico na área de *Staging* para evitar falha de tipagem na carga inicial. |
| **Uso de Memória e Escalabilidade** | Alto consumo de RAM no Colab ao manter os $362.729$ registros (especialmente as $122$ colunas de `CHIKBR25`) em memória. | Menor consumo de RAM na aplicação; o SGBD gerencia disco, índices e *buffers* com alta eficiência para agregações e *joins*. |
| **Rastreabilidade e Auditoria de Dados** | Os dados brutos originais não ficam persistidos no banco dimensional (apenas o resultado limpo). | Preserva as tabelas *Staging* brutas no banco, permitindo reprocessar regras de negócio apenas rodando o SQL novamente. |
| **Tempo Total de Execução (Colab)** | `[Inserir tempo na Macroentrega 3, ex: ~28s]` | `[Inserir tempo na Macroentrega 3, ex: ~19s]` |

---

## 6. Apresentação de Três Análises e Insights

*(Nota para a Macroentrega 3: A Dupla 3 deve inserir aqui os gráficos gerados a partir das queries em `sql/03_consultas_analises_insights.sql`).*

### Análise 1: Descompasso Regional entre Carga Epidemiológica (2024–2025) e Produção Científica (2026)
* **Consulta Realizada:** Cruzamento na Tabela Fato e `DIM_LOCALIDADE` comparando o volume total de notificações de Zika (2024) e Chikungunya (2025) por UF/Região frente ao total de pesquisas aprovadas na Plataforma Brasil em 2026 (geral e específicas de arboviroses).
* **Resultados e Estatísticas:**
  * A média estadual de casos no Brasil foi de $1.604,15$ para Zika ($\text{mediana} = 1.124$; $\text{DP} = 1.461,44$) e de $9.398,26$ para Chikungunya ($\text{mediana} = 3.746$; $\text{DP} = 15.841,13$).
  * **Mato Grosso (MT)** e **Mato Grosso do Sul (MS)** lideram com folga o ranking nacional de casos somados ($69.097$ casos em MT e $51.617$ em MS — concentrando juntos **$40,6\%$ de todos os casos do país**). Contudo, MT e MS registram apenas $504$ e $534$ projetos de pesquisa na Plataforma Brasil em 2026 (menos de $1,6\%$ da produção científica nacional).
  * Em contrapartida, **São Paulo (SP)** concentra $19.660$ pesquisas ($29,9\%$ do Brasil) para $27.427$ casos, e **Pernambuco (PE)** destaca-se positivamente no Nordeste como o 8º estado em notificações ($3.546$ de Zika + $7.673$ de Chikungunya = $11.219$ casos) e o 7º maior polo nacional de pesquisa clínica ($2.477$ projetos aprovados).
* **Insight Obtido:** Existe uma severa desigualdade geográfica entre onde os surtos de arboviroses explodem (Centro-Oeste) e onde a infraestrutura de pesquisa clínica está instalada (Sudeste e polos históricos do Nordeste como PE e BA), indicando a necessidade de editais de fomento descentralizados ou estudos multicêntricos liderados por instituições consolidadas com coleta no Centro-Oeste.

### Análise 2: Perfil Demográfico, Gestantes e Atraso na Vigilância Epidemiológica (Zika 2024 vs. Chikungunya 2025)
* **Consulta Realizada:** Agregação entre `FATO_VIGILANCIA_E_PESQUISA` e `DIM_PACIENTE` avaliando idade, sexo, condição gestacional e atraso médio entre primeiros sintomas e notificação (`qt_dias_atraso_notif`).
* **Resultados e Estatísticas:**
  * Os pacientes acometidos por Zika em 2024 são, em média, mais jovens ($\text{média} = 33,19\text{ anos}$, $\text{mediana} = 31\text{ anos}$, $\text{DP} = 19,30$) do que os acometidos por Chikungunya em 2025 ($\text{média} = 36,90\text{ anos}$, $\text{mediana} = 36\text{ anos}$, $\text{DP} = 20,22$).
  * O sexo feminino representa a maioria expressiva nas duas arboviroses ($61,9\%$ em Zika e $60,1\%$ em Chikungunya), sendo registradas **$4.159$ notificações em gestantes** ($1^{\circ}$ ao $3^{\circ}$ trimestre) em Zika 2024 e **$8.716$ em gestantes** em Chikungunya 2025.
  * O atraso entre o início dos sintomas e a notificação teve mediana de **$3,0\text{ dias}$** em ambas as doenças, mas média de **$5,68\text{ dias}$** ($\text{DP} = 12,39$) na Zika e **$6,23\text{ dias}$** ($\text{DP} = 13,66$) na Chikungunya, além de **$7.826$ hospitalizações** registradas na base de Chikungunya de 2025.
* **Insight Obtido:** A maior presença feminina e o volume superior a $12,8\text{ mil}$ gestantes notificadas no biênio demonstram a busca ativa dos serviços de pré-natal pela testagem de arboviroses. Contudo, a cauda longa no atraso de notificação (média acima do dobro da mediana) revela gargalos de digitação retroativa em municípios do interior, prejudicando o bloqueio oportuno de transmissão vetorial.

### Análise 3: Complexidade Ética e Multicentricidade das Pesquisas em Arboviroses na Plataforma Brasil (2026)
* **Consulta Realizada:** Análise sobre `DIM_PESQUISA_CEP` e `DIM_AGRAVO_CID` comparando o número de versões até aprovação (`nu_versao_projeto`) e a proporção de centros (`tipo_centro`) entre estudos de Arboviroses/Infectologia e demais áreas.
* **Resultados e Estatísticas:**
  * Os projetos aprovados na Plataforma Brasil em 2026 exigem em média **$2,45\text{ versões}$** ($\text{mediana} = 2,0$; $\text{mínimo} = 1$; $\text{máximo} = 54$; $\text{DP} = 2,20$) de tramitação ética nos CEPs.
  * Dos $65.661$ projetos válidos, $94,9\%$ são **Unicêntricos** ($62.340$), apenas $3,2\%$ contam com **Co-participantes** ($2.104$) e $1,9\%$ são **Multicêntricos** ($1.217$).
* **Insight Obtido:** A baixíssima proporção de estudos multicêntricos ($1,9\%$) explica por que estados com surtos explosivos de arboviroses (como MT, MS e RO) ficam desassistidos cientificamente: as grandes universidades do Sudeste e Nordeste conduzem pesquisas majoritariamente unicêntricas restritas aos seus próprios hospitais universitários.

---

## 7. Reflexão sobre o Aprendizado

*(Nota para a Macroentrega 4: Revisar com todo o grupo antes da entrega final em 18/11).*

A realização deste projeto de integração proporcionou ao grupo uma vivência prática e completa do ciclo de Engenharia de Dados utilizando bases governamentais reais do sistema de saúde brasileiro. Entre os principais desafios superados e lições aprendidas, destacam-se:

1. **Dados Reais Não São Limpos:** A transição de exercícios acadêmicos controlados para arquivos reais do DataSUS e da Plataforma Brasil ($362.729$ linhas) exigiu lidar com problemas concretos como divergência de *encoding* (`UTF-8` vs. `ISO-8859-1`), linhas deslocadas por falha de delimitador e erros humanos de digitação no sistema de origem (como idades codificadas acima de $800$ anos).
2. **Valor da Modelagem Dimensional (*Star Schema*):** A criação de dimensões compartilhadas (`DIM_TEMPO`, `DIM_LOCALIDADE` e `DIM_AGRAVO_CID`) provou ser a técnica ideal para integrar fontes com granularidades e propósitos originalmente distintos (notificações clínicas do SINAN e protocolos éticos da Plataforma Brasil), permitindo consultas analíticas unificadas com poucos `JOINs`.
3. **Complementaridade entre ETL e ELT:** O grupo compreendeu na prática que não existe uma abordagem única superior: o **ETL (com Python/Pandas)** mostrou-se mais flexível para higienizar arquivos malformados e aplicar expressões regulares em textos livres, enquanto o **ELT (com SQL no banco)** ofereceu excelente desempenho relacional, padronização declarativa e preservação das tabelas brutas (*Staging*) para auditoria.