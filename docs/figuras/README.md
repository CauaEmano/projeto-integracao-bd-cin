# Figuras da modelagem

- `esquema_estrela.dot`: fonte editável Graphviz, construída a partir das tabelas e tipos de `pipelines/contrato.json`.
- `esquema_estrela.svg`: versão vetorial para ampliar e inserir em documentos.
- `esquema_estrela.png`: versão raster para Markdown e slides.

As setas saem das FKs da fato e apontam para as PKs das dimensões. Cada relação é muitos-para-um; há duas relações com a mesma `dim_tempo`, nos papéis de notificação e sintomas. PK/FK aparecem no desenho; nulabilidade e regras completas estão no [dicionário](../dicionario_de_dados_e_mapeamento_de_divergencias.md).

Após editar a fonte, regenerar na raiz do projeto com Graphviz instalado:

```bash
neato -Tsvg docs/figuras/esquema_estrela.dot -o docs/figuras/esquema_estrela.svg
neato -Tpng -Gdpi=120 docs/figuras/esquema_estrela.dot -o docs/figuras/esquema_estrela.png
```

Mudanças no contrato exigem revisar também a fonte do desenho. Os rótulos de sazonalidade no esquema são convenções do projeto, sem evidência de sazonalidade derivada do diagrama.
