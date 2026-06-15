# Tasks — Query Endpoint

> Derivado de: `specs/query-endpoint/plan.md`  
> Status: Em decomposição  
> Última atualização: 2026-06-15

---

## T-001 — Setup do endpoint HTTP com validação de input

**Descrição:** Criar o handler da Azure Function para POST /api/query com validação de input usando Zod.

**Critérios de aceite:**
- [ ] Endpoint responde em `POST /api/query`
- [ ] Request body validado com Zod schema: `{ question: string }` (obrigatório, não vazio, max 500 chars)
- [ ] Retorna 400 com mensagem de erro estruturada se body inválido
- [ ] Retorna 400 se campo `question` ausente ou vazio
- [ ] Logger pino configurado (não usa console.log)
- [ ] Arquivo em `/src/functions/query/handler.ts` conforme Anexo C

**Dependências:** Nenhuma (task inicial)

**Estimativa:** P

---

## T-002 — Schema Zod para response do endpoint

**Descrição:** Definir o schema de saída do endpoint garantindo que toda resposta inclua `source_document`.

**Critérios de aceite:**
- [ ] Schema Zod para response: `{ answer: string, source_document: string, confidence: 'high' | 'medium' | 'low' }`
- [ ] Campo `source_document` obrigatório (nunca undefined)
- [ ] Schema exportado de `/src/functions/query/validator.ts`
- [ ] Tipo TypeScript inferido do schema (`z.infer<typeof ResponseSchema>`)

**Dependências:** T-001

**Estimativa:** P

---

## T-003 — Integração com Azure OpenAI para embedding

**Descrição:** Implementar serviço que converte a pergunta do atendente em embedding via Azure OpenAI.

**Critérios de aceite:**
- [ ] Função `generateEmbedding(question: string): Promise<number[]>` em `/src/services/completion.ts`
- [ ] Usa cliente Azure OpenAI (não OpenAI direto)
- [ ] Configuração via variáveis de ambiente (`AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`)
- [ ] Retry com exponential backoff (max 3 tentativas)
- [ ] Log de latência da chamada com pino
- [ ] Erro tratado: retorna erro estruturado se Azure falhar após retries

**Dependências:** T-001

**Estimativa:** M

---

## T-004 — Integração com Azure AI Search para busca de chunks

**Descrição:** Implementar serviço que busca os top-5 chunks mais relevantes no índice.

**Critérios de aceite:**
- [ ] Função `searchChunks(embedding: number[], topK: number): Promise<Chunk[]>` em `/src/services/search.ts`
- [ ] Tipo `Chunk` definido: `{ id: string, content: string, source_document: string, score: number, metadata: { vigencia?: string } }`
- [ ] Busca vetorial no Azure AI Search
- [ ] Retorna chunks ordenados por score (maior primeiro)
- [ ] Inclui metadado de vigência para tratamento de docs contraditórios (ADR-0003)
- [ ] Retry com exponential backoff

**Dependências:** T-003

**Estimativa:** M

---

## T-005 — Montagem do prompt respeitando context budget

**Descrição:** Implementar builder que monta o prompt final respeitando o context budget da ADR-0002.

**Critérios de aceite:**
- [ ] Função `buildPrompt(question: string, chunks: Chunk[], systemPrompt: string): string` em `/src/services/prompt-builder.ts`
- [ ] System prompt carregado de `/prompts/system-prompt.md`
- [ ] Context budget respeitado: ~4K tokens system + ~8K tokens chunks (ADR-0002)
- [ ] Se chunks excedem budget, trunca os de menor score (não os de maior)
- [ ] Chunks com vigência mais recente priorizados quando há contradição (ADR-0003)
- [ ] Log do token count estimado antes de enviar

**Dependências:** T-004

**Estimativa:** M

---

## T-006 — Chamada de completion ao GPT-4o

**Descrição:** Implementar chamada ao GPT-4o com o prompt montado.

**Critérios de aceite:**
- [ ] Função `generateCompletion(prompt: string): Promise<string>` em `/src/services/completion.ts`
- [ ] Usa Azure OpenAI GPT-4o (modelo configurável via env)
- [ ] Temperature = 0 para respostas determinísticas
- [ ] Max tokens de resposta configurável (default 1024)
- [ ] Retry com exponential backoff
- [ ] Log de latência e tokens consumidos

**Dependências:** T-005

**Estimativa:** M

---

## T-007 — Montagem da resposta com source_document

**Descrição:** Implementar builder que estrutura a resposta final incluindo fonte.

**Critérios de aceite:**
- [ ] Função `buildResponse(completion: string, chunks: Chunk[]): QueryResponse` em `/src/functions/query/response-builder.ts`
- [ ] Campo `source_document` sempre presente (usa chunk de maior score)
- [ ] Campo `confidence` derivado do score: high (>0.85), medium (0.7-0.85), low (<0.7)
- [ ] Se nenhum chunk relevante (todos <0.5), resposta padrão de "não encontrado"
- [ ] Response validado contra schema Zod antes de retornar

**Dependências:** T-002, T-006

**Estimativa:** P

---

## T-008 — Validação determinística de respostas (harness)

**Descrição:** Implementar validações determinísticas que o prompt não garante.

**Critérios de aceite:**
- [ ] Função `validateResponse(response: QueryResponse, chunks: Chunk[]): ValidationResult` em `/src/services/response-validator.ts`
- [ ] Verifica: resposta não menciona carga perigosa + devolução juntos (guardrail)
- [ ] Verifica: valores numéricos na resposta existem em algum chunk (anti-alucinação)
- [ ] Verifica: source_document citado existe nos chunks retornados
- [ ] Se validação falha, retorna resposta com aviso de baixa confiança

**Dependências:** T-007

**Estimativa:** M

---

## T-009 — Integração completa do handler

**Descrição:** Conectar todos os serviços no handler principal.

**Critérios de aceite:**
- [ ] Handler orquestra: validar input → embedding → search → build prompt → completion → build response → validate → return
- [ ] Erro em qualquer etapa retorna resposta estruturada (não stack trace)
- [ ] Logging estruturado em cada etapa (correlation ID)
- [ ] Tempo total de resposta logado
- [ ] Endpoint funcional end-to-end

**Dependências:** T-001, T-002, T-003, T-004, T-005, T-006, T-007, T-008

**Estimativa:** M

---

## T-010 — Testes unitários do handler e validadores

**Descrição:** Escrever testes unitários para o handler e schemas de validação.

**Critérios de aceite:**
- [ ] Testes em `/tests/unit/functions/query/`
- [ ] Cobertura: input válido, input inválido (campo ausente, vazio, muito longo)
- [ ] Cobertura: response schema validation
- [ ] Mocks para serviços externos (Azure)
- [ ] Usa Vitest conforme decisão técnica
- [ ] Todos os testes passam

**Dependências:** T-009

**Estimativa:** M

---

## Resumo

| ID | Descrição | Estimativa | Deps |
|----|-----------|------------|------|
| T-001 | Setup endpoint + validação input | P | — |
| T-002 | Schema Zod response | P | T-001 |
| T-003 | Embedding Azure OpenAI | M | T-001 |
| T-004 | Search Azure AI Search | M | T-003 |
| T-005 | Prompt builder (context budget) | M | T-004 |
| T-006 | Completion GPT-4o | M | T-005 |
| T-007 | Response builder | P | T-002, T-006 |
| T-008 | Validação determinística | M | T-007 |
| T-009 | Integração handler | M | T-001–T-008 |
| T-010 | Testes unitários | M | T-009 |

**Caminho crítico:** T-001 → T-003 → T-004 → T-005 → T-006 → T-007 → T-009
