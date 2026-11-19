# Índice dos entregáveis — 2026.2

Estado após revisão local de 18/11/2026. Critérios: enunciado fornecido pela equipe, páginas 1–3. Os materiais históricos não integram a entrega atual.

| Requisito | Material atual | Situação |
|---|---|---|
| Três bases e proveniência | [Fontes](../dados/README_DADOS.md), [inventário](../dados/metadados_fontes.json) | Presentes; 2026 parcial, download original não registrado |
| Esquema estrela e dicionário | [Relatório §1](relatorio_projeto_integracao.md), [dicionário](dicionario_de_dados_e_mapeamento_de_divergencias.md), [DDL](../sql/01_script_ddl_do_esquema_estrela.sql) | Cinco dimensões, uma fato e seis FKs |
| Relatório completo | [Sete seções consolidadas](relatorio_projeto_integracao.md) | Integração, justificativa, transformações, comparação, três insights e reflexão |
| Apresentação detalhada | [Slides PPTX](apresentacao/apresentacao_zika.pptx), [roteiro e notas](apresentacao/roteiro.md), [fluxo](diagrama_fluxo_integracao.png) | 13 slides; revisar com o grupo e ensaiar |
| ETL Colab e resultado no banco | [Notebook-fonte](../notebooks/pipeline_ETL.ipynb), [cópia Colab executada](evidencias/etl_colab_executado.ipynb), [manifesto](evidencias/manifesto_etl.json) | Evidência já fornecida pela equipe; 82.404 notificações no MySQL |
| ELT Colab, SQL e resultado no banco | [Notebook-fonte](../notebooks/pipeline_ELT_completo_executado.ipynb), [modelos SQL](../dbt/models/), [validação local histórica](validacao_pipelines.md) | Código presente; **falta cópia executada em Colab** |
| Três análises e insights | [Relatório §6](relatorio_projeto_integracao.md), [notebook](../notebooks/analises_zika.ipynb), [tabelas](analises/tabelas/), [manifesto](evidencias/validacao_analises.json) | Seis consultas reproduzidas localmente; três principais no relatório |
| Reprodução | [README](../README.md), [testes](../tests/) | Seis testes Python aprovados; MySQL não repetido nesta revisão |
| GitHub público e contribuições | [Repositório](https://github.com/CauaEmano/projeto-integracao-bd-cin), histórico Git | Conferir publicação das alterações e acesso público; não houve push nesta revisão |

## Pendências para fechar a entrega

1. Arthur/equipe: executar ELT do início ao fim em Colab com runtime compatível e MySQL, salvar cópia em `docs/evidencias/elt_colab_executado.ipynb`. Incluir staging, dbt, reconciliação e consultas finais. Não basta renomear o notebook-fonte.
2. Todos: revisar materiais e registrar contribuições reais com autoria própria e mensagens descritivas. A revisão não cria commits em nome dos integrantes.
3. Equipe: conferir que todos os arquivos finais estão no GitHub público e os links Colab abrem; confirmar o envio pelo canal oficial.
4. Todos: ensaiar apresentação, conhecer os dois fluxos e confirmar presença. Esses requisitos não podem ser comprovados apenas pelo repositório.

Uma medição ELT comparável seria útil, mas o enunciado não exige benchmark. Não inventar tempo para preencher tabela. O relatório Markdown com dicionário vinculado atende ao conteúdo; o enunciado não impõe exportação em PDF.

## Reprodução das verificações desta revisão

```bash
python -m unittest tests.test_pipelines
python -m scripts.validar_analises
```

O segundo comando usa SQLite temporário sobre a estrela ETL, sem publicar no MySQL. Para testar publicação, FKs, rollback e paridade SQL, usar `python -m tests.integration_mysql` com MySQL e permissão de criar/remover bancos temporários, conforme README.

Os slides têm fonte em `scripts/gerar_apresentacao.mjs`. A geração requer Node, `@oai/artifact-tool`, Python e os validadores da skill Presentations; informar `ARTIFACT_NODE_MODULES`, `ARTIFACT_PYTHON` e `PRESENTATIONS_SKILL` como caminhos locais. O PPTX e o roteiro podem ser usados diretamente sem essas dependências. O gerador não sobrescreve o PPTX existente: para uma nova versão, definir outro `finalPath` no script.
