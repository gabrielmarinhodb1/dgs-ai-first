from __future__ import annotations

import argparse
from datetime import date

from .config import RagConfig
from .ingest import ingest_documents
from .prompt_builder import build_prompt
from .retrieval import search_similar_chunks


def _parse_date(value: str) -> date:
    parts = value.split("-")
    if len(parts) != 3:
        raise ValueError("Use formato YYYY-MM-DD para --reference-date")
    return date(int(parts[0]), int(parts[1]), int(parts[2]))


def run() -> None:
    parser = argparse.ArgumentParser(description="Prototipo de pipeline RAG NovaTech")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest", help="Executa ingestao e indexacao")
    ingest_parser.add_argument(
        "--chunk-size",
        type=int,
        default=None,
        help="Tamanho de chunk em caracteres",
    )
    ingest_parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=None,
        help="Sobreposicao entre chunks em caracteres",
    )

    query_parser = subparsers.add_parser("query", help="Busca chunks similares")
    query_parser.add_argument("question", type=str, help="Pergunta do usuario")
    query_parser.add_argument("--top-k", type=int, default=None, help="Numero de chunks")
    query_parser.add_argument(
        "--reference-date",
        type=str,
        default=None,
        help="Data de referencia para filtro PROC-042 (YYYY-MM-DD)",
    )

    args = parser.parse_args()
    config = RagConfig()

    if args.command == "ingest":
        if args.chunk_size:
            config.chunk_size = args.chunk_size
        if args.chunk_overlap:
            config.chunk_overlap = args.chunk_overlap
        total_chunks = ingest_documents(config)
        print(f"Ingestao concluida. Total de chunks indexados: {total_chunks}")
        print(f"Colecao: {config.collection_name}")
        print(f"Diretorio Chroma: {config.chroma_dir}")
        return

    if args.command == "query":
        top_k = args.top_k or config.top_k
        reference_date = _parse_date(args.reference_date) if args.reference_date else None

        results = search_similar_chunks(
            question=args.question,
            config=config,
            n_results=top_k,
            reference_date=reference_date,
        )

        print(f"Top {len(results)} chunks recuperados:\n")
        for index, item in enumerate(results, start=1):
            source = item.metadata.get("source", "n/a")
            doc = item.metadata.get("doc_id", "n/a")
            version = item.metadata.get("version", "n/a")
            print(f"{index}. {item.chunk_id}")
            print(f"   score={item.score:.4f} | doc={doc} | versao={version}")
            print(f"   source={source}")
            print(f"   preview={item.content[:220].replace(chr(10), ' ')}")
            print()

        prompt = build_prompt(args.question, results)
        print("PROMPT MONTADO:\n")
        print(prompt)


if __name__ == "__main__":
    run()
