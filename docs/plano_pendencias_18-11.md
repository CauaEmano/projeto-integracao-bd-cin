# Pendências e divisão de tarefas para a entrega de 18/11/2026

> Plano histórico de 16/11. Para o estado atualizado, consulte [revisão de entrega de 18/11](revisao_entrega_18-11.md) e [índice atual](entregaveis.md). Itens abaixo não foram retroativamente marcados como realizados por seus responsáveis.

Revisão realizada em **16/11/2026**, com base nos dois PDFs fornecidos e no estado local do repositório. Os responsáveis seguem os seis nomes e as frentes já registrados no README. Os horários abaixo são metas internas propostas, no fuso de Fortaleza; o horário oficial de envio não foi informado.

## 1. Escopo e fontes

- **Projeto de integração - 2026.2.pdf**, pp. 1–3: requisitos de integração, relatório, notebooks Colab, repositório público, contribuições individuais e apresentação. O tema Zika aparece na p. 4.
- **Template do relatório - Projeto de Integração - Template do relatório - Projeto de Integração.pdf**, pp. 1–2: capa e sete seções do relatório. A capa contém **2025.1**; adaptar para **2026.2**, conforme o enunciado atual.
- Repositório: README, relatório, dicionário, DDL, pipelines Python, modelos e testes dbt, três notebooks, dados brutos, diagrama, PDF comparativo e histórico Git local.

Os documentos foram usados como critérios de avaliação. Esta revisão organiza o trabalho restante; não executa as tarefas atribuídas à equipe. A data de 18/11 foi fornecida pelo usuário. Não foram verificados o estado remoto do GitHub, sua visibilidade pública, links compartilhados de Colab nem o canal/horário oficial da entrega.

## 2. Diagnóstico

O quadro registra o diagnóstico inicial. As conclusões implementadas posteriormente na frente de Cauã estão marcadas na seção 4 e detalhadas na evidência vinculada nessa seção.

**A implementação central está presente. O maior risco está em entregar resultados sem evidências, análises sem conclusões e documentos contraditórios.** Não é necessário reconstruir os pipelines para cumprir o plano.

| Item solicitado | Estado observado | O que ainda falta | Prioridade / responsável |
|---|---|---|---|
| Integração de três períodos | Presente: CSVs de 2024, 2025 e 2026, com 38 campos cada | Documentar origem, data de obtenção e cobertura efetiva de cada extração; comprovar diferenças temporais | Alta / Cauã e Allanis |
| Esquema estrela e dicionário | Presentes: cinco dimensões, uma fato, DDL com PK/FK e dicionário próprio | Conferir coerência dos documentos e incluir o dicionário no pacote final; desenhar esquema das tabelas como apoio visual | Alta / Cauã |
| Notebook ETL Colab com resultado no banco | Presente, mas sem saídas e sem comprovação atual de execução em Colab | Executar do início ao fim no Colab; guardar evidências de etapas e consulta às tabelas finais | Crítica / Allanis |
| Notebook ELT Colab e transformações SQL | Presentes notebook e modelos SQL dbt, mas sem saídas salvas | Executar em Colab; comprovar staging, transformação SQL, testes e publicação final | Crítica / Arthur |
| Evidências intermediárias e finais | Há documentação de validação de 13/11 e resultados dbt locais, mas não um pacote versionado de evidências da entrega | Versionar logs/resumos/prints em pasta de documentação e vinculá-los ao relatório | Crítica / Allanis e Arthur |
| Explicação detalhada da integração | Relatório §2 resume quatro etapas e ainda pede prints | Separar os dois fluxos, explicar execução real, decisões e resultados por etapa | Alta / Allanis e Arthur |
| Justificativa da base | Presente no relatório §3 | Revisar referências, cobertura parcial e alegações para que correspondam aos resultados demonstrados | Média / Cauã e Amanda |
| Transformações aplicadas | Presentes no código, contrato, dicionário e relatório §4 | Incluir exemplos antes/depois e corrigir divergências de descrição | Alta / Cauã e Allanis |
| Comparativo ETL × ELT | Relatório §5 incompleto; PDF comparativo histórico e incompatível com implementação atual | Redigir comparação atual com vantagens, desvantagens, adequação, limitações e tempos medidos; atualizar ou retirar PDF antigo da entrega final | Crítica / Allan |
| Três análises e insights | Consultas e geração dos três gráficos implementadas; relatório §6 só apresenta temas | Executar na base atual; publicar gráficos/tabelas e escrever três interpretações sustentadas por números | Crítica / Felipe |
| Reflexão sobre aprendizado | Texto inicial presente no §7, com nota para revisão futura | Incorporar desafios reais, contribuições e aprendizados dos seis; retirar nota de macroentrega | Alta / Amanda com todos |
| Relatório completo no template | Sete seções presentes em Markdown; capa sem período e conteúdo ainda incompleto | Consolidar figuras, resultados e dicionário; remover placeholders; adaptar capa para 2026.2; revisar documento final | Crítica / Amanda |
| Slides e apresentação detalhada | Não foram encontrados arquivos de slides no repositório local | Produzir slides com contexto, tecnologias e justificativas, fluxos, diferenças temporais, resultados, comparação e participação individual | Crítica / Amanda com insumos de todos |
| Diagrama de fluxo | PNG presente, versionado e coerente com ETL/Pandas e ELT/MySQL/dbt | Reaproveitar no relatório e nos slides; guardar fonte editável se disponível | Apoio / Felipe |
| README e reprodução | Presentes instruções, requisitos e configuração por variáveis de ambiente | Validar execução em clone limpo/Colab; corrigir referências antigas e adicionar links para entregáveis e evidências | Alta / Cauã e Arthur |
| Repositório público | Git local presente; visibilidade remota não verificada | Confirmar acesso público e que todos os arquivos finais estão enviados à branch de entrega | Crítica / Cauã |
| Autoria individual rastreável | Histórico local apresenta quatro identidades principais da equipe | Não foram encontrados autores identificáveis como Felipe e Amanda; ambos devem entregar trabalho real com commits próprios e descritivos | Crítica / Todos, especialmente Felipe e Amanda |
| Preparação de todos para apresentar | Não verificável apenas pelos arquivos | Ensaio com troca de apresentador e perguntas sobre todas as etapas; confirmar presença dos seis | Crítica / Todos |

**Distinção entre exigência e sugestão:** o enunciado exige comparação ETL/ELT, mas não define benchmark de memória, escalabilidade ou número de repetições. Tempos medidos fecham o campo já previsto no relatório; medições extras ficam fora do caminho crítico. O diagrama Draw é pedido “se possível” e já existe uma imagem do fluxo. Esquema visual das tabelas e fonte `.drawio` são melhorias recomendadas, não novas exigências obrigatórias. Os PDFs não estabelecem explicitamente extensão final do relatório, dump do banco ou vídeo; exportar relatório/slides em PDF é uma sugestão para facilitar a leitura e preservar o layout.

## 3. Correções específicas que não podem passar para a versão final

1. **Comparativo antigo:** `docs/Comparativo_ETL-ELT.pdf` menciona dimensões como `dim_semana_epidemiologica` e `dim_agravo`, regras distintas entre os pipelines e exclusão de 73 registros por intervalos. Na versão atual, os dois fluxos compartilham as mesmas seis tabelas; intervalos inválidos viram NULL e os registros são preservados. O PDF também cita limpeza de `ID_AGRAVO`/`COUFINF` e flags ausentes do esquema atual. Não basta preencher resultados e conclusão: revisar o texto inteiro.
2. **Relatório §5:** retirar campos de tempo não preenchidos e corrigir a explicação de reprocessamento: o comando ELT atual também relê os CSVs e recarrega staging. A existência do staging permite estudar retransformação, mas isso não equivale a uma funcionalidade separada já demonstrada pelo comando completo.
3. **Relatório §2:** esclarecer que a deduplicação remove apenas linhas idênticas nos 38 campos, não qualquer evento que apareça em arquivos de anos diferentes. O calendário analítico usa `DT_NOTIFIC`.
4. **Relatório §6:** faltam números, figuras e insights. Para cada análise, incluir pergunta, consulta/metodologia, gráfico/tabela, achado quantitativo e limitação. Não apresentar notificações como incidência populacional.
5. **Dados de 2026:** o arquivo de 2026 contém datas de notificação de 04/01 a 05/10/2026; não representa o ano completo. Comparações anuais devem explicitar a cobertura ou usar janela comum. O maior valor de `DT_NOTIFIC` não informa a data de download.
6. **Versionamento das evidências:** `saidas/` e `dbt/target/` estão no `.gitignore`. Os três PNGs existem em `saidas/analises/`, mas não em `git ls-files`. Copiar evidências selecionadas para `docs/evidencias/` e gráficos finais para `docs/figuras/`, ou ajustar o ignore de forma específica. Não adicionar indiscriminadamente saídas e caches.
7. **Notebooks e teste de limpeza:** os três notebooks têm zero saídas e contadores nulos. O teste `test_notebooks_are_clean_and_valid` exige esse estado; salvar saídas nesses mesmos arquivos faria o teste falhar. Manter notebooks-fonte limpos e publicar evidências externas reais com links é uma opção compatível com o estado atual. Se forem exigidas cópias executadas, colocá-las fora do diretório coberto pelo teste e documentar a escolha.
8. **Nome enganoso:** `pipeline_ELT_completo_executado.ipynb` atualmente não contém resultados de execução; o nome sozinho não comprova funcionamento.
9. **Colab:** a execução depende de MySQL acessível pelo ambiente. `127.0.0.1` só funciona se o servidor estiver no próprio ambiente de execução; validar a configuração escolhida antes de depender dela na apresentação. Os notebooks importam módulos do repositório: o clone e as dependências fazem parte da reprodução.
10. **Referência antiga no README:** a atribuição de Allan cita `02_transformacoes_elt.sql`, arquivo inexistente. As transformações atuais estão em `dbt/models/`.
11. **Capa e autoria:** preencher 2026.2 e manter os seis nomes/logins. Há mensagens históricas pouco descritivas; melhorar os próximos commits sem reescrever o histórico apenas para aparentar conformidade.

## 4. Divisão executável para seis pessoas

### Pessoa 1 — Cauã Emanuel (`ceor`): arquitetura, dados e fechamento do repositório

- [x] Revisar DDL, dicionário e seções 1, 3 e 4 do relatório com base na implementação atual.
- [x] Complementar proveniência: fonte/link, data de obtenção quando conhecida, arquivo, linhas, colunas e cobertura das notificações. Data de download original declarada como não registrada.
- [x] Produzir o desenho do esquema estrela e explicar a granularidade da fato e os dois papéis de tempo.
- [x] Corrigir a referência antiga de SQL no README; adicionar links para materiais disponíveis e índice de entregáveis, com relatório final/slides explicitamente pendentes de produção.
- [ ] Conferir alterações locais com o autor, integração das contribuições, acesso público e envio final.

**Atualização em 16/11:** produção local de arquitetura concluída e acesso público conferido pela web. [Evidências e limites da revisão](evidencias/revisao_arquitetura_16-11.md). A publicação das alterações e o envio final dependem da integração dos materiais restantes; o SHA remoto não foi confirmado por consulta Git.

**Aceite:** dicionário e relatório descrevem as mesmas cinco dimensões e uma fato; README permite localizar e reproduzir a entrega; materiais finais acessíveis remotamente. **Prazo:** insumos até 17/11 às 10h; fechamento até 17/11 às 20h.

### Pessoa 2 — Allanis Beatriz (`aboml`): demonstração e documentação ETL

- [ ] Executar o notebook ETL em Colab, com clone, dependências e conexão configurados.
- [ ] Capturar leitura dos CSVs, reconciliação, exemplos de transformação, dimensões e consultas ao MySQL após publicação.
- [ ] Registrar tempos comparáveis de execução ponta a ponta junto com Allan; o notebook ETL atual não gera automaticamente o mesmo manifesto do comando CLI.
- [ ] Entregar a descrição detalhada do ETL para a seção 2 e exemplos para a seção 4.
- [ ] Mostrar comparação entre os arquivos: mesmos 38 nomes de coluna, mas diferenças de conteúdo, datas, sobreposições e preenchimento; não inventar mudanças de layout.

**Aceite:** execução sem erros em Colab e evidências legíveis da base final, com data e ambiente; texto pronto para inserir no relatório. **Prazo:** evidências até 17/11 às 12h.

### Pessoa 3 — Arthur Gabriel (`agsl`): demonstração ELT, SQL e validação

- [ ] Validar MySQL acessível pelo Colab e executar o notebook ELT completo.
- [ ] Capturar staging bruto, ordem/dependências dos modelos dbt, transformações SQL, testes e consultas às tabelas finais.
- [ ] Referenciar os SQLs existentes em `dbt/models/` e explicar por que a transformação acontece no SGBD.
- [ ] Documentar verificação de contagens e equivalência ETL/ELT, com apoio de Allan. Usar bancos dedicados separados para preservar ambas as saídas quando necessário; executar sequencialmente se usar o mesmo banco.
- [ ] Entregar texto do ELT para a seção 2 e instruções concretas de reprodução do ambiente usado.

**Aceite:** execução sem erros em Colab, testes e resultados finais demonstrados; nenhuma descrição de dimensões antigas. **Prazo:** evidências até 17/11 às 12h.

### Pessoa 4 — Allan Fernandes (`afl4`): comparativo atual e consistência dos resultados

- [ ] Reescrever o comparativo para refletir o contrato atual: mesmo resultado e mesmas regras, execução da transformação em ambientes diferentes.
- [ ] Medir ETL e ELT com mesma entrada e ambiente comparável; definir início/fim da medição, incluir leitura, transformação/carga e testes quando fizerem parte do comando, e explicitar essas diferenças de escopo. Não comparar o tempo isolado do dbt com o ETL completo.
- [ ] Consolidar reconciliação e evidências de equivalência com Arthur e Allanis.
- [ ] Finalizar seção 5 com vantagens, desvantagens, adequação ao projeto e limitações da medição. Uma execução não sustenta conclusão geral de desempenho.
- [ ] Atualizar o PDF comparativo antigo ou retirá-lo do pacote final, preservando-o como histórico claramente identificado se necessário.

**Aceite:** comparativo sem contradições de esquema/regras, tabela preenchida com medições reais e conclusão contextualizada. **Prazo:** texto e resultados até 17/11 às 15h.

### Pessoa 5 — Felipe Melo (`fma4`): três análises, figuras e insights

- [ ] Executar `notebooks/analises_zika.ipynb` após uma carga validada da base atual.
- [ ] Publicar as três tabelas de resultados e gráficos em caminho versionado e vinculá-los ao relatório.
- [ ] Escrever os três insights: sazonalidade mensal; gestantes notificadas/confirmadas por UF; tempo de notificação e encerramento por região. Incluir números que apoiem cada conclusão.
- [ ] Declarar 2026 parcial, categoria NI, cobertura dos intervalos válidos e limites de comparação. Evitar causalidade ou taxas populacionais sem denominadores.
- [ ] Reaproveitar o diagrama existente nos materiais; entregar à Amanda as figuras e explicações prontas.
- [ ] Fazer commits próprios das análises e documentação, com mensagens específicas.

**Aceite:** seção 6 com três análises distintas, três visualizações legíveis, números verificáveis e três conclusões; contribuição própria rastreável. **Prazo:** figuras e texto até 17/11 às 15h.

### Pessoa 6 — Amanda Pereira (`apmo`): relatório, slides e ensaio

- [ ] Preparar desde 16/11 a estrutura do relatório e dos slides, usando insumos preliminares.
- [ ] Consolidar as sete seções, figuras, dicionário, referências e evidências; corrigir capa para 2026.2 e retirar notas de macroentrega/campos por preencher.
- [ ] Coletar dos seis integrantes desafios e aprendizados concretos e revisar a seção 7.
- [ ] Montar slides cobrindo base/fonte/relevância, tecnologias e justificativas, ETL/ELT, diferenças temporais, três análises, comparação, evidências e contribuições individuais.
- [ ] Preparar a versão final de leitura do relatório e slides, com PDF como formato sugerido, e conferir tabelas, legendas e links.
- [ ] Organizar ensaio com todos, alternando quem explica cada frente; fazer commits próprios dos materiais.

**Aceite:** relatório completo conforme template e slides coerentes com a implementação, sem placeholders e com participação dos seis; todos aptos a responder sobre o projeto. **Prazo:** rascunho até 17/11 às 12h; versão final até 17/11 às 20h.

## 5. Cronograma proposto e dependências

| Quando | Entrega / ação | Responsáveis |
|---|---|---|
| 16/11, até 18h | Confirmar divisão; iniciar configuração Colab/MySQL; rascunhar slides e relatório; registrar proveniência | Todos |
| 16/11, até 22h | Teste inicial dos dois fluxos; estrutura dos materiais pronta; sinalizar bloqueios de conexão imediatamente | Allanis, Arthur e Amanda; apoio de Cauã |
| 17/11, até 10h | Revisão de arquitetura, dicionário e metadados | Cauã |
| 17/11, até 12h | Evidências ETL/ELT, dados finais disponíveis e medições coletadas; rascunho dos materiais | Allanis, Arthur, Allan e Amanda |
| 17/11, até 15h | Comparativo e três análises concluídos e enviados à consolidação | Allan e Felipe |
| 17/11, até 18h | Relatório e slides integrados; revisão técnica cruzada | Amanda e Cauã, com os autores das frentes |
| 17/11, até 20h | Arquivos finais versionados, links conferidos e revisão por outro integrante | Todos |
| 17/11, às 20h | Ensaio geral e perguntas; ajustes de clareza | Todos |
| 18/11, antes do prazo oficial | Conferir acesso remoto, arquivos e canal de entrega; enviar com antecedência | Cauã e Amanda, com confirmação do grupo |

**Caminho crítico:** Colab/MySQL e cargas (Allanis + Arthur) → evidências/medições (Allan) e análises (Felipe) → consolidação (Amanda) → revisão/envio (Cauã + Amanda). Amanda pode adiantar a estrutura sem esperar resultados. Felipe pode começar com a carga local validada e confirmar a versão final ao receber a reconciliação. Evitar deixar a produção principal para 18/11.

**Revisão cruzada:** Arthur revisa o ETL; Allanis revisa o ELT; Cauã revisa comparativo e números com Allan/Felipe; Felipe revisa legibilidade dos slides e Amanda revisa linguagem e links. Cada integrante continua responsável por seus próprios commits e explicação oral.

## 6. Evidências verificadas nesta revisão

- `venv/bin/python -m unittest tests.test_pipelines`: **6 testes aprovados em 16/11/2026**, incluindo reconciliação da entrada completa, regras de borda, calendário, contrato/DDL/modelos e validade/limpeza dos notebooks.
- CSVs lidos: 2024 com **43.312** linhas, 2025 com **25.764**, 2026 com **13.384**; todos com **38 colunas**. Datas de notificação por arquivo: 01/01/2024–24/02/2025; 29/12/2024–12/02/2026; 04/01/2026–05/10/2026. São intervalos observados, não garantias de completude.
- Reconciliação atual confirmada pelo teste: **82.460 brutas = 56 duplicatas exatas + 0 rejeições + 82.404 válidas**.
- `dbt/target/run_results.json` local registra execução em **13/11/2026**, com **11 modelos bem-sucedidos e 26 testes aprovados**. É evidência histórica local, ignorada pelo Git, não uma nova execução nesta revisão. O tempo ali é do dbt, não do ELT ponta a ponta.
- `docs/validacao_pipelines.md` relata integração MySQL e equivalência integral em 13/11; a integração MySQL e a execução Colab **não foram repetidas nesta revisão**.
- Três notebooks inspecionados: todos sem outputs salvos; três PNGs de análises presentes localmente, mas não versionados.
- Diagrama de fluxo inspecionado visualmente: representa fontes, ETL com Pandas e ELT com staging/SQL/dbt; não é o desenho relacional das seis tabelas.
- Histórico local: Cauã aparece com variação de capitalização do nome e mesmo e-mail; também aparecem identidades associadas a Allan, Allanis e Arthur. Não foram encontradas contribuições identificáveis de Felipe ou Amanda no histórico local consultado; isso não prova ausência de trabalho fora desse histórico.
- Já existia alteração local em `notebooks/pipeline_ETL.ipynb`; ela foi preservada. A auditoria inicial adicionou este plano; a execução posterior da frente de Cauã está documentada na seção 4.

## 7. Checklist para liberar a entrega

- [ ] Relatório cobre as sete seções do template, com capa correta, dicionário acessível e nenhuma instrução de preenchimento restante.
- [ ] Três análises contêm resultados, gráficos e insights da mesma versão dos dados.
- [ ] Comparativo corresponde aos pipelines atuais; documento histórico não causa contradições.
- [ ] ETL e ELT demonstrados em Colab com resultado final no MySQL e evidências versionadas.
- [ ] SQLs dbt, DDL e consultas analíticas acessíveis a partir do README/notebooks.
- [ ] Evidências e figuras não dependem de arquivos apenas locais/ignorados.
- [ ] Slides disponíveis e alinhados com o relatório e com o tempo informado pela professora.
- [ ] Cada integrante tem contribuição real e rastreável em sua própria autoria; todos ensaiaram e confirmaram presença.
- [ ] Clone/links do repositório público conferidos por outro integrante; alterações locais revisadas antes do envio.
- [ ] Canal e horário oficial de entrega confirmados e envio realizado antes do limite de 18/11.
