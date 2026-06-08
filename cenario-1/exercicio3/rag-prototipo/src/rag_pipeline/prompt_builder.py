from __future__ import annotations

from typing import List

from .models import RetrievedList


SYSTEM_PROMPT = """Você é um assistente de atendimento da NovaTech.
Responda apenas com base no contexto recuperado.
Se a informação não estiver no contexto, diga claramente que não encontrou evidência.
Sempre cite a fonte no formato [DOC_ID | versao | chunk_id].
Ao usar conteúdo de FAQ, avise que é conhecimento prático não formal.
"""


def build_prompt(question: str, retrieved_chunks: RetrievedList) -> str:
    context_blocks: List[str] = []
    for item in retrieved_chunks:
        doc_id = item.metadata.get("doc_id", "UNKNOWN")
        version = item.metadata.get("version", "unknown")
        confidence = item.metadata.get("confidence", "unknown")
        context_blocks.append(
            "\n".join(
                [
                    f"Fonte: [{doc_id} | {version} | {item.chunk_id}]",
                    f"Confianca: {confidence}",
                    f"Score similaridade: {item.score:.4f}",
                    "Conteudo:",
                    item.content,
                ]
            )
        )

    context = "\n\n---\n\n".join(context_blocks) if context_blocks else "Sem contexto recuperado."

    return (
        f"[SYSTEM]\n{SYSTEM_PROMPT.strip()}\n\n"
        f"[CONTEXTO RECUPERADO]\n{context}\n\n"
        f"[PERGUNTA]\n{question}\n\n"
        "[INSTRUCAO DE RESPOSTA]\n"
        "Responda em portugues brasileiro, objetivo e com citacao de fonte."
    )
