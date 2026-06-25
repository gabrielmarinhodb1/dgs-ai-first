from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

from .config import RagConfig
from .models import DocumentList, SourceDocument


DOC_FILE_MAP: Dict[str, Dict[str, str]] = {
    "POL-001-politica-devolucao.md": {
        "doc_id": "POL-001",
        "category": "politica",
        "version": "3.1",
        "status": "current",
        "confidence": "high",
        "updated_at": "2024-01-15",
    },
    "PROC-042-frete-especial-v1.md": {
        "doc_id": "PROC-042",
        "category": "procedimento",
        "version": "1.0",
        "status": "deprecated",
        "confidence": "high",
        "updated_at": "2023-03-03",
    },
    "PROC-042-v2-frete-especial-revisado.md": {
        "doc_id": "PROC-042",
        "category": "procedimento",
        "version": "2.0",
        "status": "current",
        "confidence": "high",
        "updated_at": "2023-11-10",
    },
    "SLA-2024-tabela-sla-clientes.md": {
        "doc_id": "SLA-2024",
        "category": "sla",
        "version": "2024.1",
        "status": "current",
        "confidence": "high",
        "updated_at": "2024-01-02",
    },
    "FAQ-atendimento.md": {
        "doc_id": "FAQ-ATENDIMENTO",
        "category": "faq",
        "version": "unversioned",
        "status": "current",
        "confidence": "low",
        "updated_at": "unknown",
    },
}


def _normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def load_source_documents(config: RagConfig) -> DocumentList:
    documents: List[SourceDocument] = []
    for filename, base_meta in DOC_FILE_MAP.items():
        file_path = config.docs_dir / filename
        content = _normalize_whitespace(file_path.read_text(encoding="utf-8"))
        metadata = dict(base_meta)
        metadata["source"] = str(file_path)
        documents.append(
            SourceDocument(
                doc_id=base_meta["doc_id"],
                source_path=str(file_path),
                content=content,
                metadata=metadata,
            )
        )
    return documents


def _split_document_preserving_tables(
    splitter: RecursiveCharacterTextSplitter, text: str
) -> List[str]:
    lines = text.split("\n")
    chunks: List[str] = []
    current: List[str] = []
    in_table = False

    for line in lines:
        striped = line.strip()
        is_table_line = striped.startswith("|") and striped.endswith("|")

        if is_table_line:
            in_table = True
            current.append(line)
            continue

        if in_table and not striped:
            current.append(line)
            continue

        if in_table and not is_table_line:
            table_block = "\n".join(current).strip()
            if table_block:
                chunks.extend(splitter.split_text(table_block))
            current = []
            in_table = False

        current.append(line)

    if current:
        chunks.extend(splitter.split_text("\n".join(current).strip()))

    return [chunk for chunk in chunks if chunk.strip()]


def chunk_documents(documents: DocumentList, config: RagConfig) -> List[Dict[str, str]]:
    splitter = RecursiveCharacterTextSplitter(
        separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " "],
        chunk_size=config.chunk_size,
        chunk_overlap=config.chunk_overlap,
        length_function=len,
    )

    chunk_payloads: List[Dict[str, str]] = []
    for document in documents:
        chunks = _split_document_preserving_tables(splitter, document.content)
        for index, chunk in enumerate(chunks):
            chunk_id = f"{Path(document.source_path).stem}:{index:04d}"
            payload = {
                "chunk_id": chunk_id,
                "text": chunk,
                "source_path": document.source_path,
                **document.metadata,
            }
            chunk_payloads.append(payload)
    return chunk_payloads


def ingest_documents(config: RagConfig) -> int:
    documents = load_source_documents(config)
    chunks = chunk_documents(documents, config)

    embedder = SentenceTransformer(config.embedding_model_name)
    texts = [chunk["text"] for chunk in chunks]
    embeddings = embedder.encode(texts, normalize_embeddings=True).tolist()

    config.chroma_dir.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(config.chroma_dir))
    collection = client.get_or_create_collection(name=config.collection_name)

    collection.upsert(
        ids=[chunk["chunk_id"] for chunk in chunks],
        embeddings=embeddings,
        documents=texts,
        metadatas=[
            {
                key: value
                for key, value in chunk.items()
                if key not in {"chunk_id", "text"}
            }
            for chunk in chunks
        ],
    )
    return len(chunks)
