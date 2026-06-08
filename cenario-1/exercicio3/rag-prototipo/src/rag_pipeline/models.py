from dataclasses import dataclass
from typing import Dict, List


@dataclass
class SourceDocument:
    doc_id: str
    source_path: str
    content: str
    metadata: Dict[str, str]


@dataclass
class RetrievedChunk:
    chunk_id: str
    content: str
    score: float
    metadata: Dict[str, str]


DocumentList = List[SourceDocument]
RetrievedList = List[RetrievedChunk]
