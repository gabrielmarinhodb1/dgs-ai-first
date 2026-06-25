from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class RagConfig:
    project_root: Path = field(
        default_factory=lambda: Path(__file__).resolve().parents[3]
    )
    docs_dir: Path = field(init=False)
    chroma_dir: Path = field(init=False)
    collection_name: str = "novatech_docs"
    embedding_model_name: str = "all-MiniLM-L6-v2"
    chunk_size: int = 1600
    chunk_overlap: int = 320
    top_k: int = 5

    def __post_init__(self) -> None:
        self.docs_dir = self.project_root / "arquivos-pratica"
        self.chroma_dir = self.project_root / "rag-prototipo" / "chroma_db"
