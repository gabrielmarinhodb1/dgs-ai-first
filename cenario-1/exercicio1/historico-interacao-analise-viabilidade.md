# Histórico de Interação — Análise de Viabilidade RAG NovaTech

**Exercício:** 1.1 — Análise de viabilidade técnica com fundamentos de LLM e engenharia de contexto  
**Papel:** Desenvolvedor  
**Data:** 2026-06-03  
**Ferramenta utilizada:** Claude (Claude Code / Opus 4.6)

---

## Iteração 1 — Análise Técnica Inicial

### Prompt do Usuário

> Atue como Engenheiro de IA sênior e produza uma análise técnica de viabilidade para um assistente RAG da NovaTech. A análise deve cobrir obrigatoriamente:
> - desafios por tipo de fonte: PDFs com tabelas, PDFs escaneados com OCR, wiki com links/macros, planilhas com fórmulas;
> - impacto de cada desafio na qualidade da resposta;
> - mitigação técnica concreta por desafio;
> - estimativa do tamanho da base em tokens usando 0,75 palavras por token;
> - orçamento de contexto com janela de 128K, 2K reservados para system prompt/instruções, chunks de 500 tokens;
> - estratégia de chunking considerando lost in the middle.
> Formato: relatório técnico estruturado, com tabela de riscos técnicos e recomendações finais.

### Resposta do Claude (Resumo)

O Claude produziu uma análise técnica completa com:

1. **Desafios por tipo de fonte** — 4 seções detalhadas (PDFs com tabelas, OCR, wiki, planilhas), cada uma com desafio, impacto quantificado e mitigação técnica.

2. **Estimativa de tokens:**
   - SharePoint: 800 docs × 10 pgs × 500 palavras = 4M palavras → ~5.3M tokens
   - Confluence: 400 × 1.500 = 600K palavras → ~800K tokens
   - Planilhas: 50 × 200 × 10 = 100K palavras → ~133K tokens
   - **Total estimado: ~6.3M tokens** (com overhead ~7-8M)

3. **Orçamento de contexto:**
   - Disponível para chunks (teórico): ~120.700 tokens = 241 chunks
   - Recomendação prática: **8 chunks (4.000 tokens)** como default
   - Justificativa: lost in the middle degrada qualidade acima de 10 chunks

4. **Estratégia de chunking:**
   - Chunking semântico hierárquico (por seção H2/H3)
   - Tamanho alvo: 300-600 tokens, overlap 50-75 tokens
   - Tabelas nunca divididas
   - Posicionamento U-shaped no contexto

5. **Tabela de 10 riscos técnicos** com probabilidade, impacto e mitigação.

6. **Recomendações finais** com métricas de sucesso e cronograma de PoC de 4 semanas.

---

## Iteração 2 — Revisão Crítica (Devil's Advocate)

### Prompt do Usuário

> Agora revise o relatório acima como revisor cético. Aponte:
> - estimativas otimistas demais;
> - riscos ignorados;
> - contradições técnicas;
> - pontos fracos na estratégia de chunking/retrieval/contexto.
> Em seguida, proponha ajustes específicos e mensuráveis.

### Resposta do Claude (Resumo)

O Claude atuou como revisor cético e identificou:

**Estimativas otimistas demais (4 pontos):**
1. **Tokens/página subestimados:** 500 palavras/página é otimista para docs corporativos com tabelas linearizadas. Ajuste: 700-900 palavras/página → base real de ~9-12M tokens.
2. **Precision@8 ≥ 80% irreal:** Modelos de embedding treinados em inglês perdem 15-30% em português técnico. Ajuste: target inicial de 60-65%.
3. **Latência p95 < 5s inviável:** Cross-encoder reranking + GPT-4o somam ~5-8s realistas. Ajuste: target < 8s.
4. **Faithfulness 95% sem grounding:** GPT-4o complementa com conhecimento paramétrico sem sinalizar. Ajuste: target 90% + validação pós-geração.

**Riscos ignorados (5 pontos):**
1. Controle de acesso (document-level security) ausente
2. Custo operacional mensal não estimado (~$550-700/mês base)
3. Degradação silenciosa (drift sem detecção)
4. Dependência de processo humano não-unificado de atualização
5. UX no Teams (limite de 28KB, latência percebida, ausência de deep links)

**Contradições técnicas (4 pontos):**
1. "Nunca dividir tabelas" vs. tabelas de 2.000-3.000 tokens (excede target de 600)
2. "Máximo 8 chunks" vs. "12 para multi-domínio" (lost in the middle piora com mais chunks)
3. Ordenação U-shaped assume relevância perfeita do reranker (contradiz precision < 80%)
4. "Histórico de 3 turns" vs. "8.000 tokens alocados" (inconsistência de dimensionamento)

**Pontos fracos na estratégia (4 pontos):**
1. Chunking semântico depende de estrutura que 30% da base não tem
2. Hybrid search mencionada na tabela de riscos mas ausente da arquitetura
3. Nenhuma estratégia para queries vagas/ambíguas
4. Ausência de golden dataset para validação antes de produção

**Ajustes propostos:** 10 ações específicas com métrica de validação e deadline.

---

## Iteração 3 — Versão Final Consolidada

### Prompt do Usuário

> Com base na revisão, gere a versão final da análise em formato de entregável, com:
> - resumo executivo;
> - seção de premissas de cálculo;
> - tabela de desafios por fonte (desafio, impacto, mitigação);
> - análise de orçamento de contexto (teórico vs prático);
> - estratégia final de chunking/retrieval;
> - riscos residuais e próximos passos.

### Resposta do Claude (Resumo)

Documento final consolidado com todas as correções da revisão incorporadas:

**Principais ajustes incorporados da revisão:**

| Aspecto | Versão 1 (original) | Versão final (corrigida) |
|:---|:---|:---|
| Palavras/página PDF | 500 | 700 |
| Total estimado tokens | ~6.3M | ~11.3M (cenário realista) |
| Target Precision@8 (PoC) | ≥ 80% | ≥ 65% |
| Target Faithfulness (PoC) | ≥ 95% | ≥ 85% |
| Target latência p95 | < 5s | < 8s |
| Chunks default | 8 (expandir para 12 multi-domínio) | 8 fixo (multi-domínio via decomposition 4+4) |
| Estratégia para tabelas >1000 tokens | "Nunca dividir" | Dividir por bloco lógico com cabeçalho repetido |
| Busca | Vetorial pura + reranker | Híbrida (BM25 60%/40% + reranking condicional) |
| Queries vagas | Não tratadas | Threshold 0.70 → pedir reformulação |
| Fallback de chunking | Não definido | 3 rotas por tipo de conteúdo |
| Custo | Não estimado | TCO como critério de Go/No-Go |
| Validação pré-produção | Não definida | Golden dataset 100 perguntas + critérios Go/No-Go |

**Estrutura do entregável final:**
1. Resumo executivo com targets conservadores (PoC) e de produção
2. Premissas de cálculo com limitações explícitas
3. Estimativa de tamanho (cenário realista + pessimista)
4. Tabela de desafios por fonte (4 tipos × 3 colunas)
5. Orçamento de contexto (teórico 240 chunks vs. prático 8 chunks = 3.3% utilização)
6. Estratégia de retrieval em dois estágios com reranking condicional
7. Tratamentos específicos (multi-domínio, queries vagas, contradições)
8. 7 riscos residuais com monitoramento definido
9. Plano de 3 fases com critérios de Go/No-Go

---

## Reflexão sobre o Processo de Iteração

### O que a revisão cética melhorou

1. **Honestidade nas estimativas:** Targets irreais (80% precision, 95% faithfulness, <5s latência) foram substituídos por metas conservadoras validáveis empiricamente.
2. **Contradições resolvidas:** A tensão entre "nunca dividir tabelas" e o target de 600 tokens foi resolvida com regra explícita de threshold (1.000 tokens) e fallback.
3. **Gaps preenchidos:** Queries vagas, controle de acesso, custo operacional e degradação silenciosa eram riscos reais não endereçados.
4. **Coerência arquitetural:** A estratégia de "expandir para 12 chunks em multi-domínio" foi substituída por query decomposition (4+4), que respeita a própria premissa de lost in the middle.

### O que teria acontecido sem a revisão

A análise v1 teria sido apresentada com targets que provavelmente falhariam na PoC (80% precision em português técnico, 5s de latência com cross-encoder), gerando retrabalho e perda de credibilidade. A contradição sobre tabelas e chunks teria sido descoberta apenas durante a implementação.

### Lição para o projeto

A análise técnica de viabilidade deve ser tratada como hipótese, não como fato. Os números só têm valor se houver processo de validação (golden dataset, PoC, métricas de regressão) antes de se tornarem compromissos arquiteturais.

---

## Evidências de Uso da Ferramenta

- **Ferramenta:** Claude Code (Opus 4.6) via terminal
- **Abordagem:** 3 iterações progressivas (análise → revisão cética → consolidação)
- **Refinamento demonstrado:** A versão final é verificavelmente superior à v1 em honestidade de estimativas, coerência interna e completude de riscos
- **Engenharia de contexto aplicada:** O cenário completo + informações técnicas adicionais foram fornecidos no primeiro prompt; a revisão usou o output anterior como input (progressive disclosure na própria interação com a ferramenta)
