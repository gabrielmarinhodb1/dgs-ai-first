# Prototipo RAG Open-Source (NovaTech)

Este projeto implementa uma pipeline RAG com:
- Python
- ChromaDB (vector store local)
- sentence-transformers (embeddings)
- LangChain + langchain-text-splitters (orquestracao de chunking)

## Estrutura

- src/rag_pipeline/ingest.py: ingestao, chunking, embeddings e indexacao
- src/rag_pipeline/retrieval.py: busca de chunks similares
- src/rag_pipeline/prompt_builder.py: montagem de prompt final
- src/rag_pipeline/cli.py: interface de linha de comando para ingest e query

## Estrategia de chunking

- Splitter: RecursiveCharacterTextSplitter (LangChain)
- chunk_size: 1600 caracteres
- chunk_overlap: 320 caracteres
- Separadores hierarquicos: titulos markdown, paragrafos e frases
- Preservacao de tabelas: linhas de tabela sao tratadas como bloco unico antes de split

Justificativa:
- Os documentos possuem regras em blocos semiestruturados e tabelas de decisao.
- Overlap ajuda a manter contexto em secoes com continuidade de regra.
- Preservar tabela evita quebrar relacoes coluna-valor importantes para retrieval.

## Como executar

1. Criar ambiente virtual e instalar dependencias:

   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

2. Rodar ingestao:

   PYTHONPATH=src python -m rag_pipeline.cli ingest

3. Rodar consulta:

   PYTHONPATH=src python -m rag_pipeline.cli query "Qual o prazo geral de devolucao?"

4. Consulta com filtro de versao de PROC-042 por data de referencia:

   PYTHONPATH=src python -m rag_pipeline.cli query "Como calcular frete especial para o Norte?" --reference-date 2026-01-15

## Saidas esperadas

- Ingestao:
  - total de chunks indexados
  - nome da colecao
  - diretorio persistente do ChromaDB
- Query:
  - top N chunks com score de similaridade
  - metadados de fonte
  - prompt final completo (system + contexto + pergunta)
