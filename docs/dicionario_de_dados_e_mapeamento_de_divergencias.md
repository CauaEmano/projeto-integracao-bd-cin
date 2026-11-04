# 🛠️ Guia Técnico para as Duplas de ETL e ELT: Regras de Negócio e Divergências (Zika 2024, 2025 e 2026)

Este documento detalha o mapeamento exato das colunas originais dos arquivos `ZIKABR24.csv`, `ZIKABR25.csv` e `ZIKABR26.csv` para o nosso **Esquema Estrela**, além de listar as **diferenças e problemas reais entre os 3 anos** (item obrigatório na apresentação e no relatório).

---

## 1. Visão Geral das 3 Bases Anuais (`dados/`)

* **Arquivos:** `ZIKABR24.csv` (2024), `ZIKABR25.csv` (2025) e `ZIKABR26.csv` (2026).
* **Formato Físico:** Codificação `UTF-8`, separador vírgula (`,`), $38$ colunas em cada arquivo.
* **Vantagem para o Repositório:** Como os 3 arquivos juntos ocupam menos de $15\text{ MB}$, todos os três podem ficar salvos diretamente na pasta `dados/` do GitHub sem precisar de LFS!

---

## 2. As 5 Diferenças e Problemas ao Longo do Tempo (Para Tratar no Código e Mostrar nos Slides)

A especificação do projeto pede para **destacar diferenças percebidas nos dados ao longo do tempo (de um ano para o outro)**. Aqui estão os 5 pontos reais encontrados nas bases de Zika de 2024, 2025 e 2026:

1. **Vazamento Temporal entre os Arquivos Anuais (`NU_ANO` vs. Arquivo de Origem):**
   * O SINAN exporta os arquivos com base no calendário epidemiológico. Por isso, dentro de `ZIKABR24.csv` existem registros com `NU_ANO = 2025` (da 1ª semana epidemiológica), e o mesmo ocorre na transição entre `ZIKABR25.csv` e `ZIKABR26.csv`.
   * **Regra no ETL/ELT:** Ao concatenar (`UNION ALL` / `pd.concat`) os 3 arquivos, extrair o ano real diretamente de `DT_NOTIFIC` e aplicar deduplicação para evitar que notificações de fronteira de ano sejam contadas duas vezes.
2. **Evolução da Taxa de Casos "Em Aberto / Nulos" entre 2024, 2025 e 2026:**
   * Na base de **2024** (`ZIKABR24.csv`), a maioria das investigações já foi encerrada (`DT_ENCERRA` preenchida e `CLASSI_FIN` definido).
   * Nas bases de **2025** (`ZIKABR25.csv`) e principalmente **2026** (`ZIKABR26.csv`), há um aumento expressivo de valores nulos (`NaN` / `NULL`) nas colunas de desfecho (`CLASSI_FIN`, `CRITERIO`, `EVOLUCAO`, `DT_ENCERRA`), pois muitos casos recentes ainda aguardam resultado laboratorial.
   * **Regra no ETL/ELT:** Nunca descartar linhas que tenham `CLASSI_FIN` nulo! Mapear `NULL` em `CLASSI_FIN`, `CRITERIO` e `EVOLUCAO` para `'Em Investigação / Não Preenchido'`.
3. **Mudança de Tipagem Automática (`float64` vs. `int64`) por Presença de Nulos:**
   * Colunas de código como `SG_UF`, `ID_MN_RESI`, `CS_GESTANT`, `CS_RACA`, `CLASSI_FIN`, `CRITERIO` e `EVOLUCAO` vêm como `float` (`1.0`, `26.0`, `261160.0`) quando há nulos no arquivo anual.
   * **Regra no ETL/ELT:** Converter para inteiro (`Int64` ou `CAST(... AS INTEGER)`) antes de fazer o *join* ou mapeamento de texto.
4. **Codificação Composta de Idade (`NU_IDADE_N`) e Outliers:**
   * A coluna `NU_IDADE_N` usa 4 dígitos: `1xxx` (Horas), `2xxx` (Dias), `3xxx` (Meses), `4xxx` (Anos).
   * **Regra de Decodificação:**
     * Se `NU_IDADE_N < 4000`: `idade_anos = 0` (Menor de 1 ano).
     * Se `NU_IDADE_N >= 4000` e `NU_IDADE_N <= 4120`: `idade_anos = NU_IDADE_N - 4000`.
     * Se `NU_IDADE_N > 4120` ou nulo: `idade_anos = NULL` (trata outliers de erro de digitação).
   * **Faixas Etárias Padronizadas (`faixa_etaria`):**
     * `0 a 14 anos` (Criança/Adolescente)
     * `15 a 29 anos` (Jovem)
     * `30 a 44 anos` (Adulto I)
     * `45 a 59 anos` (Adulto II)
     * `60 anos ou mais` (Idoso)
     * `Ignorado` (quando `idade_anos IS NULL`)
5. **Datas Inválidas no Cálculo de Atraso de Notificação e Encerramento:**
   * Existem registros onde `DT_SIN_PRI > DT_NOTIFIC` (atraso negativo) ou `DT_SIN_PRI` foi digitado com ano errado (ex: 1990, gerando atraso $> 365\text{ dias}$).
   * **Regra no ETL/ELT:** Calcular `qt_dias_atraso_notif = DT_NOTIFIC - DT_SIN_PRI`. Se o valor for $< 0$ ou $> 365$, gravar `NULL`. Aplicar a mesma regra para `qt_dias_encerramento = DT_ENCERRA - DT_NOTIFIC`.

---

## 3. Tabelas de Decodificação de Domínios do SINAN (Para usar no Python e no SQL)

### 3.1. Condição Gestacional (`CS_GESTANT`) $\rightarrow$ `status_gestante` e `fl_gestante`
| Código (`CS_GESTANT`) | Descrição (`status_gestante`) | Flag na Fato (`fl_gestante`) |
| :---: | :--- | :---: |
| `1` | `1º Trimestre` | `1` |
| `2` | `2º Trimestre` | `1` |
| `3` | `3º Trimestre` | `1` |
| `4` | `Idade Gestacional Ignorada` | `1` |
| `5` | `Não Gestante` | `0` |
| `6` | `Não se aplica` | `0` |
| `9` ou `NULL` | `Ignorado` | `0` |

### 3.2. Raça/Cor (`CS_RACA`) $\rightarrow$ `raca_cor`
* `1` $\rightarrow$ `'Branca'`
* `2` $\rightarrow$ `'Preta'`
* `3` $\rightarrow$ `'Amarela'`
* `4` $\rightarrow$ `'Parda'`
* `5` $\rightarrow$ `'Indígena'`
* `9` ou `NULL` $\rightarrow$ `'Ignorado'`

### 3.3. Classificação Final (`CLASSI_FIN`), Critério (`CRITERIO`) e Evolução (`EVOLUCAO`)
* **`CLASSI_FIN`:**
  * `1` $\rightarrow$ `'Confirmado'` (`fl_confirmado = 1`, `fl_descartado = 0`)
  * `2` $\rightarrow$ `'Descartado'` (`fl_confirmado = 0`, `fl_descartado = 1`)
  * `8` ou `NULL` $\rightarrow$ `'Inconclusivo / Em Investigação'` (`fl_confirmado = 0`, `fl_descartado = 0`)
* **`CRITERIO`:**
  * `1` $\rightarrow$ `'Laboratorial'`
  * `2` $\rightarrow$ `'Clínico-Epidemiológico'`
  * `3` $\rightarrow$ `'Em Investigação'`
  * `NULL` / Outros $\rightarrow$ `'Ignorado / Não Preenchido'`
* **`EVOLUCAO`:**
  * `1` $\rightarrow$ `'Cura'` (`fl_obito_zika = 0`)
  * `2` $\rightarrow$ `'Óbito pelo agravo'` (`fl_obito_zika = 1`)
  * `3` $\rightarrow$ `'Óbito por outras causas'` (`fl_obito_zika = 0`)
  * `9` ou `NULL` $\rightarrow$ `'Ignorado / Em Acompanhamento'` (`fl_obito_zika = 0`)

### 3.4. Mapeamento de Código IBGE de UF (`SG_UF` e `SG_UF_NOT`)
| Código IBGE | Sigla UF | Nome do Estado | Região |
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