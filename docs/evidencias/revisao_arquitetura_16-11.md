# Revisão da arquitetura e das fontes — 16/11/2026

Frente de Cauã Emanuel: modelagem, dicionário, metadados, seções 1/3/4 do relatório, README e preparação da integração final.

## Entregas desta frente

- Dicionário com **49 atributos físicos**, tipos/comprimentos, nulabilidade e origem nas seis tabelas; mapeamento do destino dos **38 campos brutos**.
- Desenho do esquema estrela em [SVG](../figuras/esquema_estrela.svg) e [PNG](../figuras/esquema_estrela.png), com [fonte editável](../figuras/esquema_estrela.dot). Cinco dimensões, uma fato e seis FKs; tempo é usado nos papéis de notificação e sintomas. As imagens foram inspecionadas visualmente.
- Inventário das fontes com contagens, cobertura, SHA-256, distribuição bruta dos anos e preenchimento dos campos: [documentação](../../dados/README_DADOS.md) e [JSON](../../dados/metadados_fontes.json).
- [Auditor reexecutável](../../scripts/auditar_fontes.py), usando apenas a biblioteca padrão Python e sem modificar CSVs.
- Seções 1, 3 e 4 do [relatório](../relatorio_projeto_integracao.md) revisadas; correções factuais pontuais nas seções 2 e 5 para eliminar contradições com o código.
- README com links para os materiais disponíveis, preparação Colab, localização real das transformações SQL e orientação de versionamento das evidências.
- [Índice de entregáveis](../entregaveis.md), com responsáveis e pendências explícitas para relatório final, slides, análises e execuções Colab.

## Conferências técnicas

| Conferência | Resultado |
|---|---|
| Contrato × DDL | Seis tabelas, 49 atributos/tipos e seis FKs coerentes, conferidos pelo teste existente |
| Contrato × dicionário/diagrama | Nomes e tipos dos 49 atributos conferidos; seis relações no desenho |
| Destino dos campos | Todos os 38 campos cobertos no mapeamento bruto → estrela/staging |
| CSVs | 43.312 + 25.764 + 13.384 = 82.460 linhas; layout comum de 38 campos |
| Reconciliação | 56 duplicatas exatas, 0 rejeições por data obrigatória e 82.404 válidas |
| Integridade dos arquivos | SHA-256 de cada CSV conferido contra o inventário |
| Testes locais existentes | `venv/bin/python -m unittest tests.test_pipelines`: 6 testes aprovados em 16/11/2026 |
| Reprodução isolada | Mesmos 6 testes aprovados em cópia dos arquivos do projeto sem saídas/caches ignorados; dependências fornecidas pelo Python do venv existente |
| Inventário reproduzido | Auditor executado na cópia isolada produz JSON idêntico ao inventário entregue |
| Links de documentação | 74 referências locais/âncoras conferidas no README, documentação das fontes e arquivos Markdown de docs |
| Whitespace do diff | `git diff --check` aprovado |

O DDL foi revisado e não exigiu alteração funcional: já contém PKs, FKs, tipos e checks de domínio necessários à modelagem atual. Não foi feita migração do banco nem alteração nas regras de transformação.

## Proveniência e acesso público

O [portal do Ministério da Saúde](https://dadosabertos.saude.gov.br/dataset/arboviroses-zika-virus) foi consultado em 16/11/2026 para confirmar a fonte temática. A data de download original e as etapas anteriores à produção dos CSVs não estão registradas; isso está declarado nos metadados. Não se afirma igualdade com os recursos atuais do portal.

O [repositório GitHub](https://github.com/CauaEmano/projeto-integracao-bd-cin) foi aberto pela consulta web em 16/11/2026 e identificado como **Public**. A consulta Git direta a `refs/heads/main` não foi concluída, portanto o SHA remoto não foi confirmado. A marca local `origin/main` é apenas o estado conhecido localmente, não uma verificação atual do servidor.

## Limites e integração final

Esta revisão não executou os notebooks no Colab nem repetiu a integração MySQL. O registro em [validacao_pipelines.md](../validacao_pipelines.md) refere-se à execução anterior de 13/11/2026. Os tempos de execução, insights, versão final do relatório, slides e evidências Colab continuam nas frentes atribuídas à equipe.

As alterações desta frente estão preparadas no workspace; não foi realizado commit ou push. O fechamento remoto depende da revisão/publicação dessas alterações e dos materiais dos demais integrantes. A alteração preexistente em `notebooks/pipeline_ETL.ipynb` foi preservada e não foi incorporada a um commit automático. O checklist geral permanece aberto onde há dependências reais.

Comandos principais de reprodução, na raiz do clone:

```bash
python3 scripts/auditar_fontes.py
python -m unittest tests.test_pipelines
git diff --check
```

O primeiro comando requer apenas Python; os testes usam as dependências de `requirements.txt`. A reprodução completa com MySQL e Colab segue as instruções do README e das respectivas frentes.
