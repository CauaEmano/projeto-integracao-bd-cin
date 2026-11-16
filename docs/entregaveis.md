# Índice de entregáveis — 18/11/2026

Estado em 16/11/2026, após revisão da frente de arquitetura de Cauã. “Disponível” indica arquivo local existente; publicação das alterações depende de commit e push. Nenhum item pendente é tratado como concluído.

| Material | Arquivo disponível | Estado / próximo passo | Responsável |
|---|---|---|---|
| Relatório | [Texto com sete seções](relatorio_projeto_integracao.md) | Seções 1, 3 e 4 revisadas; concluir evidências, comparação, análises, reflexão coletiva e edição final | Amanda, com insumos de todos |
| Dicionário de dados | [49 atributos físicos e mapeamento dos 38 campos](dicionario_de_dados_e_mapeamento_de_divergencias.md) | Revisado com contrato e DDL; acompanhar a exportação do relatório | Cauã |
| Modelagem dimensional | [SVG](figuras/esquema_estrela.svg), [PNG](figuras/esquema_estrela.png) e [fonte editável](figuras/esquema_estrela.dot) | Disponíveis; seis tabelas e seis FKs | Cauã |
| Fontes e metadados | [Documentação](../dados/README_DADOS.md), [inventário](../dados/metadados_fontes.json), [auditor](../scripts/auditar_fontes.py) | Disponíveis; download original sem data registrada | Cauã |
| DDL | [Esquema físico MySQL](../sql/01_script_ddl_do_esquema_estrela.sql) | Revisado; nenhuma mudança funcional necessária nesta frente | Cauã |
| ETL | [Notebook](../notebooks/pipeline_ETL.ipynb), [transformações Python](../pipelines/core.py) | Fonte disponível; falta evidência de execução Colab e resultado no banco | Allanis |
| ELT | [Notebook](../notebooks/pipeline_ELT_completo_executado.ipynb), [SQLs dbt](../dbt/models/) | Fonte disponível; o nome “executado” não comprova execução; falta evidência Colab | Arthur |
| Comparativo ETL/ELT | [Seção 5 do relatório](relatorio_projeto_integracao.md#5-comparativo-entre-etl-e-elt) | Pendentes medições e revisão final; `Comparativo_ETL-ELT.pdf` é histórico, com regras divergentes, e não deve servir de documento final | Allan |
| Três análises | [Consultas e visualizações](../notebooks/analises_zika.ipynb) | Implementadas; publicar tabelas/gráficos atuais e três insights quantitativos | Felipe |
| Fluxo de integração | [Diagrama existente](diagrama_fluxo_integracao.png) | Disponível para relatório e slides | Felipe |
| Evidências técnicas | [Validação de 13/11](validacao_pipelines.md), [revisão de 16/11](evidencias/revisao_arquitetura_16-11.md) | Resultados locais documentados; falta pacote Colab | Allanis e Arthur |
| Slides | Ainda sem arquivo no repositório | Criar e inserir o link nesta tabela quando existir | Amanda |
| Relatório final exportado | Ainda sem arquivo consolidado | Concluir conteúdo, revisar layout e anexar dicionário; inserir link quando existir | Amanda |
| Revisão/envio final | [Checklist e cronograma](plano_pendencias_18-11.md) | Depende das entregas acima, presença/ensaio e confirmação do canal/horário | Cauã e Amanda, com todos |

## Publicação e conferência

O [repositório GitHub](https://github.com/CauaEmano/projeto-integracao-bd-cin) foi consultado pela web em 16/11/2026 e aparece como **Public**. A visibilidade pública não comprova que alterações ainda locais estejam publicadas. A consulta Git direta à referência remota não foi concluída nesta revisão; não há afirmação de sincronização com `origin/main`.

Ao consolidar a entrega:

1. Cada integrante revisa e faz commit dos arquivos de sua contribuição, com mensagem descritiva e autoria própria.
2. Revisar a alteração local preexistente no notebook ETL com seu autor antes de incluí-la em qualquer commit.
3. Integrar as contribuições e atualizar esta tabela com os links dos materiais finais.
4. Conferir `git status`, arquivos selecionados e branch antes de enviar; publicar os commits autorizados.
5. Abrir o repositório público sem sessão, conferir os arquivos e reproduzir os links a partir do README.
6. Confirmar canal/horário e registrar o envio antes do prazo oficial em 18/11.

Manter evidências em `docs/evidencias/` e figuras finais em `docs/figuras/`. Evitar credenciais em logs, imagens ou notebooks. O índice não aponta para arquivos finais que ainda não existem.
