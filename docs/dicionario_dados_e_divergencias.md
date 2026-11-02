# 🛠️ Guia Técnico para as Duplas de ETL e ELT: Divergências e Regras de Mapeamento

Este documento serve como referência rápida para a **Dupla 1 (ETL)** e a **Dupla 2 (ELT)** desenvolverem seus pipelines na **Macroentrega 2**, garantindo que ambos os notebooks gerem exatamente o mesmo resultado no banco de dados final.

---

## 1. Resumo Físico dos 3 Arquivos Brutos

| Arquivo | Ano Base | Registros | Colunas | Tamanho | Encoding | Separador (`sep`) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `ZIKABR24.csv` | 2024 | $43.312$ | $38$ | $6,56\text{ MB}$ | `utf-8` | `,` (vírgula) |
| `CHIKBR25.csv` | 2025 | $253.753$ | $122$ | $67,12\text{ MB}$ | `utf-8` | `,` (vírgula) |
| `plataforma_brasil_2026.csv` | 2026 | $65.664$ | $26$ | $37,90\text{ MB}$ | `latin1` (`iso-8859-1`) | `\|` (pipe) |

---

## 2. As 5 Divergências Críticas que o ETL e o ELT Devem Tratar (E Mostrar nos Slides!)

### Divergência 1: Evolução de Colunas no SINAN (2024 vs. 2025)
* `ZIKABR24.csv` possui **$38$ colunas** (foco demográfico e epidemiológico básico).
* `CHIKBR25.csv` possui **$122$ colunas** (adiciona $84$ colunas de sintomas clínicos como `FEBRE`, `MIALGIA`, `CEFALEIA`, `ARTRALGIA`, comorbidades como `DIABETES`, `HIPERTENSA`, dados de internação `HOSPITALIZ` e sorologia).
* **Ação no Pipeline:** Mapear o núcleo comum para as dimensões e extrair `HOSPITALIZ = 1` de `CHIKBR25` para a métrica `qt_hospitalizacao` (definindo `0` como padrão para Zika, onde a coluna não é exportada).

### Divergência 2: Diferença nos Códigos de Confirmação (`CLASSI_FIN`)
* Em `ZIKABR24.csv`, os valores de `CLASSI_FIN` são: `1.0` (Confirmado — $7.136$ casos), `2.0` (Descartado — $23.163$ casos), `8.0` (Inconclusivo — $9.811$ casos).
* Em `CHIKBR25.csv`, o SINAN utiliza a codificação expandida de arboviroses: `13.0` (Confirmado Chikungunya — $116.599$ casos), `5.0` (Descartado — $93.192$ casos), `8.0` (Inconclusivo — $32.275$ casos).
* **Ação no Pipeline:**
  * Para `ZIKABR24`: `qt_caso_confirmado = 1` quando `CLASSI_FIN == 1`.
  * Para `CHIKBR25`: `qt_caso_confirmado = 1` quando `CLASSI_FIN == 13`.

### Divergência 3: Codificação de Idade (`NU_IDADE_N`) e Outliers $> 120$ Anos
* No SINAN, `NU_IDADE_N` é um inteiro de 4 dígitos:
  * Se `NU_IDADE_N < 4000` (horas, dias ou meses): `idade_anos = 0`.
  * Se `NU_IDADE_N >= 4000`: `idade_anos = NU_IDADE_N - 4000`.
* **Anomalia Real Encontrada:** Em `CHIKBR25.csv`, existem **$10$ registros** onde `NU_IDADE_N > 4120` (ex: `4829` $\rightarrow 829\text{ anos}$; `4401` $\rightarrow 401\text{ anos}$).
* **Ação no Pipeline:** Se `idade_anos > 120` ou `idade_anos < 0`, substituir por `NULL` e classificar `faixa_etaria = 'Ignorado'`.

### Divergência 4: Linhas Corrompidas e UFs Nulas na `plataforma_brasil_2026.csv`
* Existem **$3$ linhas deslocadas** onde `uf_proponente` vale `'68'`, `tipo_do_estudo` vale `'SP'` e `situacao_do_parecer` vale `'cappesq.adm@hc.fm.usp.br'`.
* Existem **$1.365$ linhas** onde `uf_proponente` está vazio (`NaN`), mas `uf_cep` possui a sigla correta da UF.
* **Ação no Pipeline:**
  1. Filtrar/remover registros onde `situacao_do_parecer != 'Aprovado'` (isso já elimina as $3$ linhas corrompidas, restando $65.661$ linhas válidas).
  2. Definir a UF final da pesquisa como `COALESCE(uf_proponente, uf_cep)`.

### Divergência 5: Código Numérico IBGE vs. Sigla de UF
* `ZIKABR24` e `CHIKBR25` usam códigos numéricos em `SG_UF_NOT` (`11` a `53`).
* `plataforma_brasil_2026` usa siglas de 2 letras (`RO` a `DF`).
* **Tabela de Mapeamento Oficial para usar no Python (ETL) e no SQL (ELT):**

| Código IBGE (`SG_UF_NOT`) | Sigla UF | Nome do Estado | Região |
| :---: | :---: | :--- | :--- |
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