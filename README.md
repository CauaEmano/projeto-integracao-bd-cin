# 📊 Projeto de Integração de Dados — Data Warehouse de Vigilância Epidemiológica de Zika Vírus no Brasil (2024–2026)

**Universidade Federal de Pernambuco (UFPE)**  
**Centro de Informática (CIn) — Ciência da Computação**  
**Disciplina:** Banco de Dados  

---

## Sobre o Projeto

Este repositório centraliza os artefatos do **Projeto de Integração de Dados**, cujo objetivo é consolidar três conjuntos de dados temporais consecutivos (**2024, 2025 e 2026**) referentes às notificações de **Zika Vírus no Brasil (Tema 10 — SINAN / Ministério da Saúde)** em um **Data Warehouse modelado em Esquema Estrela (*Star Schema*)**:

1. **Base 2024 (`ZIKABR24.csv`):** Microdados de notificações e investigações de Zika Vírus registrados em $2024$ ($38$ atributos originais).
2. **Base 2025 (`ZIKABR25.csv`):** Microdados de notificações e investigações de Zika Vírus registrados em $2025$ ($38$ atributos originais).
3. **Base 2026 (`ZIKABR26.csv`):** Microdados de notificações e investigações de Zika Vírus registrados em $2026$ ($38$ atributos originais).

O projeto implementa e compara dois pipelines distintos construídos no ambiente **Google Colab**:
* **Pipeline ETL (*Extract, Transform, Load*):** Extração dos 3 arquivos anuais, tratamento de vazamento temporal entre anos, limpeza de *outliers*, decodificação de domínios do SINAN em memória (Python/Pandas) e carga no Esquema Estrela.
* **Pipeline ELT (*Extract, Load, Transform*):** Extração e carga bruta dos 3 arquivos diretamente em tabelas *Staging* no SGBD, executando todas as transformações, deduplicações e padronizações via scripts SQL dentro do banco de dados.

---

## Estrutura do Repositório

    projeto-integracao-bd/
     ┣ dados/
     ┃  ┣ ZIKABR24.csv                           # Base SINAN Zika Vírus - Ano 2024
     ┃  ┣ ZIKABR25.csv                           # Base SINAN Zika Vírus - Ano 2025
     ┃  ┗ ZIKABR26.csv                           # Base SINAN Zika Vírus - Ano 2026
     ┣ docs/
     ┃  ┣ relatorio_projeto_integracao.md        # Relatório completo no formato do Template CIn-UFPE
     ┃  ┣ dicionario_dados_e_divergencias.md     # Esquema Estrela, Dicionário e Divergências entre os 3 anos
     ┃  ┗ diagrama_fluxo_integracao.drawio.png   # Diagrama visual da arquitetura ETL/ELT (Draw.io)
     ┣ notebooks/
     ┃  ┣ pipeline_ETL.ipynb                     # Notebook Google Colab do processo ETL
     ┃  ┗ pipeline_ELT.ipynb                     # Notebook Google Colab do processo ELT
     ┣ sql/
     ┃  ┣ 01_create_star_schema.sql              # DDL de criação das tabelas Fato e Dimensões
     ┃  ┣ 02_transformacoes_elt.sql              # Scripts SQL de transformação dentro do SGBD (ELT)
     ┃  ┗ 03_consultas_analises_insights.sql     # Queries analíticas das 3 Análises e Insights
     ┗ README.md                                 # Documentação principal e instruções de execução

---

## Como Reproduzir e Executar o Projeto

1. **Bases de Dados Brutas (`dados/`):**
   * Como os três arquivos de Zika Vírus (`ZIKABR24.csv`, `ZIKABR25.csv` e `ZIKABR26.csv`) são leves (cerca de $6,5\text{ MB}$ em $2024$, e ainda menores em $2025$ e $2026$), eles já estão versionados diretamente na pasta `dados/` deste repositório, permitindo que os notebooks do Google Colab façam a leitura direta via URL do GitHub ou clonagem do repositório.
2. **Execução do Pipeline ETL:**
   * Abra o arquivo `notebooks/pipeline_ETL.ipynb` no **Google Colab**.
   * Execute todas as células sequencialmente para realizar a extração dos 3 anos, transformação via Pandas e carga no banco dimensional.
3. **Execução do Pipeline ELT:**
   * Abra o arquivo `notebooks/pipeline_ELT.ipynb` no **Google Colab**.
   * O notebook realizará a carga bruta (*Staging*) dos três arquivos CSV e executará os scripts contidos em `sql/01_create_star_schema.sql` e `sql/02_transformacoes_elt.sql` diretamente no SGBD.

---

## Equipe e Divisão de Responsabilidades

| Integrante | Login CIn | Dupla / Frente Principal | Responsabilidades no Projeto |
| :--- | :--- | :--- | :--- |
| **Cauã Emanuel** | `ceor` | Dupla 1 — Arquitetura & ETL | Concepção da Macroentrega 1, Modelagem Star Schema, Dicionário de Dados, Pipeline ETL |
| **Allanis Beatriz** | `aboml` | Dupla 1 — Arquitetura & ETL | Desenvolvimento do Notebook Colab ETL, tratamento em Python/Pandas e carga dimensional |
| **Arthur Gabriel** | `agsl` | Dupla 2 — Engenharia ELT & BD | Configuração do SGBD, carga *Staging* e desenvolvimento do Notebook Colab ELT |
| **Allan Fernandes** | `afl4` | Dupla 2 — Engenharia ELT & BD | Scripts SQL de transformação interna (`02_transformacoes_elt.sql`) e comparativo ETL vs. ELT |
| **Felipe Melo** | `fma4` | Dupla 3 — Analytics & Docs | Diagrama de fluxo no Draw.io, Consultas SQL e Visualizações das 3 Análises e Insights |
| **Amanda Pereira** | `apmo` | Dupla 3 — Analytics & Docs | Consolidação do Relatório Final, Evidências Intermediárias e Slides da Apresentação |

---

## Padrão Obrigatório de Commits no GitHub

Para atender aos critérios de avaliação da disciplina, **todos os integrantes devem realizar commits utilizando suas próprias contas do GitHub** e seguir o padrão descritivo abaixo (mensagens genéricas como `"update"`, `"teste"` ou `"ajuste final"` são proibidas):

* `feat(etl): implementacao da decodificacao da coluna NU_IDADE_N nas bases de Zika 2024 a 2026`
* `feat(elt): criacao da query SQL de padronizacao de UF e deduplicacao temporal entre anos`
* `docs(relatorio): adicao dos graficos e insights da analise 1 sobre sazonalidade dos casos`
* `docs(arquitetura): inclusao do diagrama de integracao exportado do draw.io`