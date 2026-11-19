// Requer @oai/artifact-tool no runtime de artefatos; execução documentada no índice.
import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
const require = createRequire(path.join(process.env.ARTIFACT_NODE_MODULES, '../package.json'));
const { Presentation, PresentationFile } = require('@oai/artifact-tool');
process.env.RUNTIME_NODE_MODULES ||= process.env.ARTIFACT_NODE_MODULES;
const root = process.cwd();
const build = path.join(root, 'tmp/revisao/slides');
await fs.mkdir(build, {recursive:true});
await fs.mkdir('docs/apresentacao', {recursive:true});
const presentation = Presentation.create({slideSize:{width:1280,height:720}});
const specs = [
 ['Integração de dados de Zika', 'SINAN • 2024–2026\nBanco de Dados • CIn / UFPE • 2026.2\nETL e ELT sobre um mesmo esquema estrela', null, 'README.md; docs/relatorio_projeto_integracao.md'],
 ['Três extrações, 82.460 linhas brutas', 'Fonte declarada: SINAN / Ministério da Saúde.\n2024: 43.312 • 2025: 25.764 • 2026: 13.384 linhas.\n38 campos comuns: notificações, perfil, localização e investigação.\nTema permite cruzar tempo, gestação e desfecho; 2026 é parcial.', null, 'dados/README_DADOS.md; dados/metadados_fontes.json'],
 ['O layout é igual; a cobertura varia', 'Datas observadas: 2024-01-01 a 2026-10-05 no conjunto.\n69 linhas de ZIKABR24 e 12 de ZIKABR25 têm ano diferente do arquivo.\nCalendário analítico: DT_NOTIFIC, preservando essas linhas.\nCLASSI_FIN vazio: 537 / 433 / 754 linhas por extração.', null, 'dados/metadados_fontes.json. Datas extremas não garantem completude. Não foi registrada a data original de download.'],
 ['Tecnologias e escolhas', 'Python / Pandas: leitura textual, inspeção e transformação ETL.\nMySQL: armazenamento, chaves estrangeiras e publicação transacional.\ndbt: transformação SQL, dependências e testes ELT.\nColab: ambiente de demonstração; GitHub: código e autoria.', null, 'requirements.txt; pipelines/; dbt/; README.md'],
 ['Dois caminhos para a mesma estrela', '', 'docs/diagrama_fluxo_integracao.png', 'ETL transforma em Python antes da carga. ELT carrega staging textual e transforma dentro do MySQL. Fonte: pipelines/run.py.'],
 ['Uma fato e cinco dimensões', 'Fato: uma linha válida distinta nos 38 campos brutos.\nTempo: data de notificação e início dos sintomas (duas FKs).\nLocalidade: residência; unidade notificadora: local de registro.\nPaciente: perfil sociodemográfico, sem identificar pessoa.\nInvestigação/desfecho: classificação, critério e evolução.', null, 'sql/01_script_ddl_do_esquema_estrela.sql; pipelines/contrato.json. SK=0 desconhecido.'],
 ['Regras comuns e resultados intermediários', '82.460 brutas → remover 56 duplicatas exatas → 82.404 válidas.\nData obrigatória inválida: quarentena; zero rejeições nesta entrada.\nIdade 4030 → 30 anos; códigos de gestação 1–4 → flag 1.\nIntervalos fora de 0–365 dias viram NULL; a notificação permanece.', null, 'pipelines/core.py; dbt/models/; docs/evidencias/manifesto_etl.json. Exemplos de transformação ilustram regras, não linhas específicas.'],
 ['ETL e ELT: o que muda na prática', 'ETL facilita depurar registros, mas usa memória do processo Python.\nELT mantém staging auditável e depende de recursos do SGBD e dbt.\nAmbos relêem os CSVs no comando completo e usam o mesmo DDL.\nETL Colab: 31,061 s; sem tempo ELT comparável, não há vencedor.', null, 'docs/relatorio_projeto_integracao.md seção 5. Uma execução ETL ponta a ponta, sem instalação. Não é benchmark.'],
 ['70,8% das notificações entre janeiro e maio', 'Jan–set: 39.373 → 22.942 → 13.384 registros.\nMesmos meses não garantem completude nem medem incidência.', 'docs/analises/01_sazonalidade.png', 'docs/analises/tabelas/01_sazonalidade.csv. 58.307 / 82.404 em jan–mai. Revisão: estrela ETL + consultas SQLite, não execução MySQL.'],
 ['Volume notificado e confirmação diferem por UF', '7.184 notificações em gestantes; 207 confirmadas (2,88%).\nSP: 2.487 / 3; MT: 328 / 109 (notificadas / confirmadas).', 'docs/analises/02_gestantes.png', 'docs/analises/tabelas/02_gestantes.csv. NI: 2 notificações, 1 confirmada. Não são pessoas únicas nem evidência de protocolo de triagem.'],
 ['Encerramento médio: 29,05 dias', 'Notificação: 5,67 dias, 82.404 intervalos válidos.\nEncerramento: 80.481 válidos (97,67%); ausências afetam a média.', 'docs/analises/03_tempos.png', 'docs/analises/tabelas/03_tempos.csv; docs/evidencias/validacao_analises.json. Médias ponderadas por registros. Medianas: 3 e 19 dias. Sem conclusão causal.'],
 ['Validação e limites da demonstração', 'Evidência ETL Colab: 82.404 registros consultados no MySQL.\nRevisão atual: seis testes Python e seis consultas analíticas aprovados.\nEquivalência integral ETL/ELT: documentada em teste local de 13/11.\nPendente: salvar execução ELT em Colab e conferir publicação final.', null, 'docs/evidencias/etl_colab_executado.ipynb; docs/validacao_pipelines.md; docs/revisao_entrega_18-11.md. Revisão atual não repetiu integração MySQL.'],
 ['Contribuições e aprendizados', 'Cauã / Allanis: arquitetura e ETL.\nArthur / Allan: SGBD, ELT, SQL e comparação.\nFelipe / Amanda: análises, documentação e apresentação.\nLições: definir granularidade, compartilhar regras e documentar limites.', null, 'Divisão declarada no README; validar autoria efetiva nos commits. Todos devem explicar os dois fluxos. Slides consolidados na revisão automatizada; não implicam autoria humana adicional.'],
];
function text(slide, value, x, y, w, h, size, bold=false, color='#173B47') {
 const s=slide.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 s.text=value; s.text.style={typeface:'DejaVu Sans',fontSize:size,color,bold};
}
for (let i=0;i<specs.length;i++) {
 const [title,body,img,notes]=specs[i];
 const slide=presentation.slides.add(); slide.background.fill='#F8FAF9';
 text(slide,title,64,40,1152,110,i===0?56:40,true);
 if (img) {
  if(body) text(slide,body,64,151,1152,95,24);
  const bytes=await fs.readFile(path.join(root,img));
  slide.images.add({blob:bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),contentType:'image/png',alt:title,fit:'contain',position:{left:90,top:body?265:160,width:1100,height:body?375:475}});
 } else text(slide,body,64,i===0?260:205,1152,390,i===0?32:28);
 text(slide,`${i+1} / ${specs.length}`,1140,675,95,25,16,false,'#507079');
 slide.speakerNotes.text=notes;
 const png=await presentation.export({slide,format:'png',scale:1});
 await fs.writeFile(path.join(build,`${i+1}.png`),new Uint8Array(await png.arrayBuffer()));
}
const candidate=path.join(build,'candidate.pptx');
await (await PresentationFile.exportPptx(presentation)).save(candidate);
const {finalizePresentation}=await import(path.join(process.env.PRESENTATIONS_SKILL,'container_tools/artifact_tool_utils.mjs'));
await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:path.join(root,'docs/apresentacao/apresentacao_zika.pptx'),pythonExecutable:process.env.ARTIFACT_PYTHON,integrityValidatorPath:path.join(process.env.PRESENTATIONS_SKILL,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(process.env.PRESENTATIONS_SKILL,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],fontPolicy:{basis:'design',families:['DejaVu Sans']},verifyArtifactToolImport:true,receiptPath:path.join(build,'validacao.json')});
await fs.writeFile('docs/apresentacao/roteiro.md', '# Roteiro da apresentação\n\n'+specs.map((s,i)=>`## ${i+1}. ${s[0]}\n\n${s[1]}\n\n${s[2]?`![${s[0]}](../../${s[2]})\n\n`:''}Notas: ${s[3]}\n`).join('\n'));
console.log('Apresentação exportada e validada.');
