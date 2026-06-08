from __future__ import annotations

from datetime import date
from typing import Dict, List, Optional

import chromadb
from sentence_transformers import SentenceTransformer

from .config import RagConfig
from .models import RetrievedChunk, RetrievedList


def _base_where_filter() -> Dict[str, object]:
    return {
        "$or": [
            {"doc_id": "POL-001"},
            {"doc_id": "PROC-042"},
            {"doc_id": "SLA-2024"},
            {"doc_id": "FAQ-ATENDIMENTO"},
        ]
    }


def _proc_version_filter(reference_date: Optional[date]) -> Optional[Dict[str, str]]:
    if reference_date is None:
        return None
    transition = date(2023, 12, 1)
    if reference_date >= transition:
        return {"version": "2.0"}
    return {"version": "1.0"}


def search_similar_chunks(
    question: str,
    config: RagConfig,
    n_results: Optional[int] = None,
    reference_date: Optional[date] = None,
) -> RetrievedList:
    embedder = SentenceTransformer(config.embedding_model_name)
    query_embedding = embedder.encode([question], normalize_embeddings=True)[0].tolist()

    client = chromadb.PersistentClient(path=str(config.chroma_dir))
    collection = client.get_or_create_collection(name=config.collection_name)

    # Keep filter simple and deterministic for this prototype.
    where_filter = _base_where_filter()
    query_result = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results or config.top_k,
        where=where_filter,
        include=["documents", "metadatas", "distances"],
    )

    version_hint = _proc_version_filter(reference_date)
    chunks: List[RetrievedChunk] = []
    for chunk_id, content, metadata, distance in zip(
        query_result["ids"][0],
        query_result["documents"][0],
        query_result["metadatas"][0],
        query_result["distances"][0],
    ):
        metadata = metadata or {}
        if version_hint and metadata.get("doc_id") == "PROC-042":
            if metadata.get("version") != version_hint["version"]:
                continue

        score = 1.0 - float(distance)
        chunks.append(
            RetrievedChunk(
                chunk_id=str(chunk_id),
                content=str(content),
                score=score,
                metadata={str(k): str(v) for k, v in metadata.items()},
            )
        )

    return chunks
