# 📊 Projeto de Integração de Dados — Data Warehouse de Vigilância Epidemiológica e Pesquisa Clínica (2024–2026)

**Universidade Federal de Pernambuco (UFPE)**  
**Centro de Informática (CIn) — Ciência da Computação**  
**Disciplina:** Banco de Dados  

---

## 🎯 Sobre o Projeto

Este repositório centraliza os artefatos do **Projeto de Integração de Dados**, cujo objetivo é consolidar três conjuntos de dados públicos do Ministério da Saúde que abrangem anos consecutivos (**2024, 2025 e 2026**), totalizando **$362.729$ registros**, em um **Data Warehouse modelado em Esquema Estrela (*Star Schema*)**:

1. **Tema 10 — Zika Vírus (SINAN, 2024):** Arquivo `ZIKABR24.csv` ($43.312$ registros e $38$ colunas) com notificações e investigações de casos de Zika no Brasil.
2. **Tema 8 — Febre de Chikungunya (SINAN, 2025):** Arquivo `CHIKBR25.csv` ($253.753$ registros e $122$ colunas) com notificações clínico-epidemiológicas de Chikungunya.
3. **Tema 11 — Plataforma Brasil (Ministério da Saúde, 2026):** Arquivo `plataforma_brasil_2026.csv` ($65.664$ registros e $26$ colunas) com projetos de pesquisa envolvendo seres humanos submetidos aos Comitês de Ética em Pesquisa (CEPs).

O projeto implementa e compara dois pipelines distintos construídos no ambiente **Google Colab**:
* **Pipeline ETL (*Extract, Transform, Load*):** Tratamento, limpeza, decodificação e padronização em memória (Python/Pandas) antes da carga no Esquema Estrela.
* **Pipeline ELT (*Extract, Load, Transform*):** Extração e carga bruta diretamente em tabelas *Staging* no SGBD, realizando todas as transformações via scripts SQL dentro do banco de dados.

---

## 📂 Estrutura do Repositório

```text
📦 projeto-integracao-bd/
 ┣ 📂 dados/
 ┃  ┗ 📜 README_DADOS.md                        # Link para o Google Drive com os 3 CSVs originais
 ┣ 📂 docs/
 ┃  ┣ 📜 relatorio_projeto_integracao.md        # Relatório completo no formato do Template CIn-UFPE
 ┃  ┣ 📜 dicionario_dados_e_divergencias.md     # Esquema Estrela, Dicionário e Anomalias mapeadas
 ┃  ┗ 🖼️ diagrama_fluxo_integracao.drawio.png   # Diagrama visual da arquitetura ETL/ELT (Draw.io)
 ┣ 📂 notebooks/
 ┃  ┣ 📓 pipeline_ETL.ipynb                     # Notebook Google Colab do processo ETL
 ┃  ┗ 📓 pipeline_ELT.ipynb                     # Notebook Google Colab do processo ELT
 ┣ 📂 sql/
 ┃  ┣ 📜 01_create_star_schema.sql              # DDL de criação das tabelas Fato e Dimensões
 ┃  ┣ 📜 02_transformacoes_elt.sql              # Scripts SQL de transformação dentro do SGBD (ELT)
 ┃  ┗ 📜 03_consultas_analises_insights.sql     # Queries analíticas das 3 Análises e Insights
 ┗ 📜 README.md                                 # Documentação principal e instruções de execução
```

---

## 🚀 Como Reproduzir e Executar o Projeto

1. **Obtenção das Bases de Dados Brutas:**
   * Como o arquivo `CHIKBR25.csv` possui $67,12\text{ MB}$ (acima do limite recomendado de $50\text{ MB}$ do GitHub padrão), os três arquivos originais (`ZIKABR24.csv`, `CHIKBR25.csv` e `plataforma_brasil_2026.csv`) estão disponíveis na pasta compartilhada do Google Drive indicada em `dados/README_DADOS.md`.
2. **Execução do Pipeline ETL:**
   * Abra o arquivo `notebooks/pipeline_ETL.ipynb` no **Google Colab**.
   * Monte o Google Drive (ou faça upload dos CSVs) e execute todas as células sequencialmente para realizar a extração, transformação via Pandas e carga no banco dimensional.
3. **Execução do Pipeline ELT:**
   * Abra o arquivo `notebooks/pipeline_ELT.ipynb` no **Google Colab**.
   * O notebook realizará a carga bruta (*Staging*) dos três arquivos e executará os scripts contidos em `sql/01_create_star_schema.sql` e `sql/02_transformacoes_elt.sql` diretamente no banco de dados.

---

## 👥 Equipe e Divisão de Responsabilidades

| Integrante | Login CIn | Dupla / Frente Principal | Responsabilidades no Projeto |
| :--- | :--- | :--- | :--- |
| **Integrante 1 (Você)** | `@login1` | Dupla 1 — Arquitetura & ETL | Concepção da Macroentrega 1, Modelagem Star Schema, Dicionário de Dados, Pipeline ETL |
| **Integrante 2** | `@login2` | Dupla 1 — Arquitetura & ETL | Desenvolvimento do Notebook Colab ETL, tratamento em Python/Pandas e carga dimensional |
| **Integrante 3** | `@login3` | Dupla 2 — Engenharia ELT & BD | Configuração do SGBD, carga *Staging* e desenvolvimento do Notebook Colab ELT |
| **Integrante 4** | `@login4` | Dupla 2 — Engenharia ELT & BD | Scripts SQL de transformação interna (`02_transformacoes_elt.sql`) e comparativo ETL vs. ELT |
| **Integrante 5** | `@login5` | Dupla 3 — Analytics & Docs | Diagrama de fluxo no Draw.io, Consultas SQL e Visualizações das 3 Análises e Insights |
| **Integrante 6** | `@login6` | Dupla 3 — Analytics & Docs | Consolidação do Relatório Final, Evidências Intermediárias e Slides da Apresentação |

---

## ⚠️ Padrão Obrigatório de Commits no GitHub

Para atender aos critérios de avaliação da disciplina, **todos os integrantes devem realizar commits utilizando suas próprias contas do GitHub** e seguir o padrão descritivo abaixo (mensagens genéricas como `"update"`, `"teste"` ou `"ajuste final"` são proibidas):

* `feat(etl): implementacao da decodificacao da coluna NU_IDADE_N na base ZIKABR24`
* `feat(elt): criacao da query SQL de padronizacao de UF por codigo IBGE`
* `docs(relatorio): adicao dos graficos e insights da analise 1 sobre distribuicao regional`
* `docs(arquitetura): inclusao do diagrama de integracao exportado do draw.io`