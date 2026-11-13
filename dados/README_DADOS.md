# Dados brutos — Zika/SINAN (2024–2026)

Os três arquivos versionados são `ZIKABR24.csv`, `ZIKABR25.csv` e `ZIKABR26.csv`.
Todos usam vírgula, UTF-8 (BOM tolerado) e o mesmo layout de 38 colunas.
2026 é parcial. As três extrações somam 82.460 linhas antes da deduplicação.

As regras e origens dos campos estão no [dicionário](../docs/dicionario_de_dados_e_mapeamento_de_divergencias.md).
Os pipelines leem estes arquivos sem modificá-los. Configure `ZIKA_DATA_DIR` para outra pasta.
