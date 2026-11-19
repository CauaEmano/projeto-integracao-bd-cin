# Revisão de conformidade — 18/11/2026

## Parecer

O projeto é coerente em tema, três períodos e arquitetura ETL/ELT, mas **a entrega ainda não pode ser declarada integralmente concluída**: falta evidência ELT em Colab, além da conferência de publicação/autoria e apresentação pela equipe. Os requisitos foram extraídos de “Projeto de integração - 2026.2.pdf”, páginas 1–3. O PDF foi tratado como enunciado, não como autorização para publicar, enviar ou atribuir trabalho a terceiros.

## Correções realizadas

- Corrigida variável `tables_out` não definida, que interrompia a quarta análise. As seis consultas agora exportam CSVs.
- Acrescentados denominadores e cobertura aos tempos; média nacional revisada de 5,69 para **5,67** dias até notificação e de 28,99 para **29,05** até encerramento.
- Removidas interpretações causais não sustentadas: clima, protocolos de pré-natal, ausência de circulação viral, surtos e supostas causas dos prazos. Diferenças de município/UF foram descritas como diferenças nos códigos de notificação e residência.
- Separados denominadores municipais e estaduais na consulta complementar; UF NI não entra na proporção interestadual.
- Completadas seções de integração, comparação e três insights do relatório, com números, gráficos, tabelas e limitações. Incorporada a reflexão da contribuição anterior em `relatorio.txt`.
- Criados slides e roteiro cobrindo os itens da apresentação. Preservada a divisão de responsabilidades declarada; não foi fabricada autoria.
- Movidos o PDF comparativo incompatível e o relatório anterior para `docs/historico/`; a versão vigente está indicada no README e no índice.
- Atualizado o índice para reconhecer a evidência ETL Colab e contribuições recentes. O histórico local inclui commits de Felipe e Amanda; a pendência antiga que dizia não encontrá-los está superada.
- Sinalizado que o nome `pipeline_ELT_completo_executado.ipynb` não representa uma execução: o arquivo-fonte permanece limpo.

## Verificações e seus limites

- `python -m unittest tests.test_pipelines`: **6 testes aprovados**, incluindo reconciliação completa, regras de borda, calendário e correspondência contrato/DDL/SQL.
- `python -m scripts.validar_analises`: **6 células analíticas executadas** sobre a estrela reconstruída em Python, usando SQLite em memória; todas as tabelas e figuras foram regeneradas. [Manifesto com hashes e ambiente](evidencias/validacao_analises.json).
- Contagens confirmadas: **82.460 = 56 + 0 + 82.404**. Dimensões: 1.003, 2.562, 6.631, 9.024 e 128.
- Evidência Colab ETL existente: saída do MySQL com 82.404 notificações; manifesto com 31,061 s. Inspecionada, não executada novamente nesta revisão.
- MySQL/dbt: testes de integração não repetidos, pois não havia cliente/servidor MySQL disponível no ambiente. A documentação de 13/11 permanece identificada como histórica; SQLite não verifica FKs, publicação nem equivalência MySQL.
- Apresentação: 13 slides renderizados e inspecionados; pacote, geometria, fontes e reimportação validados pelo Artifact Tool.
- GitHub: não foram feitos push, alterações de histórico ou verificação remota atual. O estado local não comprova a publicação.

## O que ainda depende da equipe

Salvar execução ELT real em Colab, conferir GitHub público e links, revisar a autoria dos commits e realizar apresentação/ensaio. O [índice de entregáveis](entregaveis.md) contém os caminhos e próximos passos. Não há exigência explícita no enunciado de benchmark, dump do banco, vídeo, PDF final ou arquivo Draw editável; não foram tratados como bloqueios obrigatórios.
