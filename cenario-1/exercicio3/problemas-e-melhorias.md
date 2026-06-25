# Problemas Identificados e Propostas de Melhoria

## Resumo Executivo

- O principal gargalo atual e o **ranking**: Hit@1 esta em 0%, ou seja, o chunk correto nao aparece em primeiro.
- Ha tambem **contaminacao de dominio**: cerca de 50% dos top-5 recuperados vem de fontes irrelevantes para a pergunta.
- As duas falhas estao ligadas: sem priorizacao semantica por contexto, o sistema mistura documentos parecidos por palavra, mas diferentes por intencao.

---

## 1. Ranking Subotimo (Hit@1 = 0%)

### Sinal do Problema

- **Metrica:** Hit@1 = 0% (a resposta correta nunca aparece na posicao 1).
- **Evidencia:** Na pergunta 4 ("Posso devolver carga perigosa?"), a resposta correta (POL-001, secao 3.2) apareceu apenas na **posicao 4**.

### Impacto

- O LLM recebe contexto desordenado.
- O chunk correto perde prioridade.
- A chance de resposta final incorreta aumenta.

### Causa Raiz

A similaridade por cosseno, isoladamente, nao captura bem:

- especificidade da pergunta em relacao ao documento;
- hierarquia de relevancia semantica;
- contexto de dominio (ex.: "perigosa" em frete vs "perigosa" em devolucao).

### Propostas de Melhoria

#### 1. Curto Prazo: Reranking com Cross-Encoder

- Implementar camada de reranking com um modelo cross-encoder (ex.: `ms-marco-MiniLM-L-12-v2`).
- Pipeline sugerido: Dense Retrieval (top-5) -> Cross-Encoder Reranking -> Top-1.
- **Ganho estimado:** Hit@1 pode subir para 80%+.
- **Esforco:** medio (latencia adicional de ~100 ms).

#### 2. Medio Prazo: Filtragem por Categoria (Pre e Pos-Query)

- **Pre-query:** classificar a pergunta em categoria (devolucao, frete, SLA etc.).
- **Pos-retrieval:** aplicar filtro ou peso por categoria inferida.
- **Ganho estimado:** reducao de ruido em ~50%; Hit@1 pode chegar a 60%+.
- **Esforco:** medio (classificador dedicado ou chamada de LLM).

#### 3. Longo Prazo: Reducao do Tamanho de Chunk

- Estado atual: chunks de 1600 caracteres com overlap de 320.
- Proposta: chunks de 800 caracteres para maior granularidade.
- **Trade-off:** aumento no numero de chunks indexados (~25-30).
- **Ganho estimado:** menos contaminacao e melhor precisao em consultas especificas.

---

## 2. Contaminacao de Dominio (~50% dos Top-5)

### Sinal do Problema

- **Metrica:** ~50% dos top-5 recuperados vem de dominios irrelevantes.
- **Exemplo:** perguntas sobre devolucao (POL-001) recuperam varios chunks de frete (PROC-042).
- **Caso critico:** na pergunta 4, chunks de PROC-042 apareceram nas posicoes 1 e 3, antes do chunk correto de POL-001 (posicao 4).

### Impacto

- O contexto recuperado fica poluido.
- O gerador recebe evidencias conflitantes.
- A confiabilidade da resposta final cai.

### Causa Raiz

Palavras compartilhadas geram similaridade espuria:

- "perigosa" aparece em POL-001 (devolucao proibida) e PROC-042 (frete especial);
- "especial" aparece em PROC-042 (frete) e FAQ (atendimento);
- embeddings capturam sobreposicao lexical sem considerar bem o dominio.

### Propostas de Melhoria

#### 1. Curto Prazo: Filtragem Pos-Retrieval por Confianca

- Definir threshold de score com fallback controlado.
- Rejeitar chunks com score abaixo do limite e mismatch de categoria.
- **Ganho estimado:** reducao de ruido em 30-40%.
- **Risco:** descartar chunk valido se o threshold estiver agressivo demais.

#### 2. Medio Prazo: Inferencia de Categoria Pre-Query

- Usar classificacao zero-shot com LLM para inferir o dominio da pergunta.
- Recuperar ou priorizar apenas categorias relevantes (ex.: "devolucao" -> POL-001).
- **Ganho estimado:** ruido abaixo de 20%; Hit@1 pode chegar a 70%+.
- **Esforco:** medio (chamada adicional de LLM, +50 a 100 ms).

#### 3. Longo Prazo: Embeddings por Dominio

- Manter embeddings e colecoes separados por dominio (devolucao, frete, SLA, FAQ).
- Adicionar um query router para selecionar a colecao/modelo correto antes da busca.
- **Ganho estimado:** minimiza contaminacao e maximiza precisao.
- **Esforco:** alto (dados rotulados, treino e manutencao de multiplos indices).

---

## Priorizacao Recomendada

1. Implementar reranking com cross-encoder (ganho rapido em ranking).
2. Adicionar filtro por categoria com threshold de confianca (reduz ruido).
3. Revisar chunking para 800 caracteres e reavaliar metricas.
4. Evoluir para arquitetura por dominio (router + indices separados), se o volume justificar.
