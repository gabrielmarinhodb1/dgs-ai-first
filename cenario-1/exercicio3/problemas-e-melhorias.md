# Problemas Identificados e Propostas de Melhoria

## 1. Ranking Subótimo (Hit@1 = 0%)

### Problema
- **Métrica:** Hit@1 = 0% (resposta correta **nunca** aparece em posição 1)
- **Evidência:** Pergunta 4 ("Posso devolver carga perigosa?") teve a resposta correta (POL-001 3.2) apenas em **posição 4**
- **Impacto:** LLM recebe contexto desordenado; chunk correto não é priorizado

### Causa Raiz
Similaridade por cosseno pura não captura:
- Especificidade da pergunta em relação ao documento
- Hierarquia de relevância semântica
- Contexto de domínio (não diferencia "perigosa em frete" vs "perigosa em devolução")

### Propostas de Solução

#### Correção 1 (Curto Prazo): Reranking com Cross-Encoder
- Implementar reranking layer usando modelo cross-encoder (ex: `ms-marco-MiniLM-L-12-v2`)
- Pipeline: Dense Retrieval (5 chunks) → Cross-Encoder Reranking → Top-1
- **Benefício estimado:** Hit@1 pode aumentar para 80%+
- **Complexidade:** Média (adiciona ~100ms latência)

#### Correção 2 (Médio Prazo): Filtragem de Categoria Pré/Pós-Query
- **Pré-query:** Classificar pergunta em categoria (devolução, frete, SLA, etc.)
- **Pós-retrieval:** Filtrar chunks para categoria inferida; aplicar soft weights
- **Benefício estimado:** Reduz ruído em 50%; Hit@1 sobe para 60%+
- **Complexidade:** Média (requer treinamento de classificador ou LLM)

#### Correção 3 (Longo Prazo): Redução de Tamanho de Chunk
- Chunks atuais: 1600 caracteres com 320 overlap
- Proposta: Reduzir para 800 caracteres (mais granular, menos ruído)
- **Trade-off:** Mais chunks indexados (~25-30), mas maior precisão
- **Benefício:** Reduz contamination; melhora Hit@1 em contextos específicos

---

## 2. Contaminação de Domínio (~50% dos Top-5)

### Problema
- **Métrica:** ~50% dos top-5 resultados provêm de domínios **irrelevantes**
- **Exemplo:** Perguntas sobre devolução (POL-001) recuperam muitos chunks de frete (PROC-042)
- **Caso crítico:** Pergunta 4 teve PROC-042 em posições 1, 3 antes do correto POL-001 em 4

### Causa Raiz
Palavras-chave compartilhadas geram similaridade espúria:
- "perigosa" aparece em: POL-001 (devolução proibida) E PROC-042 (frete especial)
- "especial" aparece em: PROC-042 (frete) E FAQ (atendimento)
- Embeddings capturam token overlap sem considerar contexto de domínio

### Propostas de Solução

#### Correção 1 (Curto Prazo): Filtragem Pós-Retrieval por Confiança
- Implementar score threshold com fallback inteligente
- Rejeitar chunks com score < threshold E categoria mismatch
- **Benefício:** Reduz ruído imediato em 30-40%
- **Risco:** Pode rejeitar chunks válidos; requer tuning manual

#### Correção 2 (Médio Prazo): Inferência de Categoria Pré-Query
- Usar zero-shot classification LLM para categorizar pergunta
- Retornar chunks apenas de categorias relevantes (ex: "devolução" → filtro POL-001)
- **Benefício:** Reduz ruído para <20%; melhora Hit@1 para 70%+
- **Complexidade:** Requer LLM call + classificação; +50-100ms latência

#### Correção 3 (Longo Prazo): Embeddings Scoped por Domínio
- Treinar embeddings separados por domínio (devolução, frete, SLA, FAQ)
- Query router: seleciona embedding model + collection conforme categoria
- **Benefício:** Elimina contamination; máxima precisão
- **Complexidade:** Alta (requer dados etiquetados por domínio, re-treinamento)

---
