# Revisão Crítica — Código Gerado para T-001

> Exercício Dev 2.2 — Análise do código gerado com assistência de IA  
> Data: 2026-06-15

---

## Resumo da implementação

Arquivos criados/modificados:
- `src/functions/query/validator.ts` — Schemas Zod para input e output
- `src/functions/query/handler.ts` — Azure Function v4 HTTP trigger
- `src/shared/logger.ts` — Logger pino configurado
- `package.json` — Dependências atualizadas

---

## Pontos que precisam de ajuste antes do code review

### 1. **Ausência de validação de variáveis de ambiente**

**Problema:** O logger usa `process.env.LOG_LEVEL` sem validação. Se a variável não existir ou tiver valor inválido, o comportamento é undefined.

**Código atual (logger.ts:6):**
```typescript
level: process.env.LOG_LEVEL || "info",
```

**Risco:** Em produção, se `LOG_LEVEL=debug` por engano, logs sensíveis podem ser expostos. Se `LOG_LEVEL=invalid`, pino pode falhar silenciosamente.

**Correção proposta:**
```typescript
import { z } from "zod";

const LogLevelSchema = z.enum(["fatal", "error", "warn", "info", "debug", "trace"]).default("info");

const logLevel = LogLevelSchema.parse(process.env.LOG_LEVEL);
```

**Padrão violado:** O `plan.md` define Zod para validação de input/output, mas não mencionou config — porém a convenção deveria se estender a todas as entradas externas.

---

### 2. **Mensagens de erro em português no código, mas comments em inglês**

**Problema:** Inconsistência de idioma nos artefatos de código.

**Código atual (validator.ts:6-8):**
```typescript
.string({
  required_error: "Campo 'question' é obrigatório",  // português
  invalid_type_error: "Campo 'question' deve ser uma string",  // português
})
```

**Código atual (handler.ts:27):**
```typescript
message: "Request body deve ser um JSON válido",  // português
```

**Mas:**
```typescript
// Handler HTTP para POST /api/query  // inglês
log.info({ method: request.method, url: request.url }, "Query request received");  // inglês
```

**Risco:** Viola o padrão definido no cenário (comments em inglês). Mensagens de erro para o usuário final podem ser em português (OK), mas precisam ser consistentes e vir de um arquivo de i18n ou constantes, não hardcoded.

**Correção proposta:**
- Criar `/src/shared/messages.ts` com constantes de mensagens
- Ou usar uma lib de i18n se internacionalização for requisito futuro

---

### 3. **Handler não implementa circuit breaker para falhas em cascata**

**Problema:** O `plan.md` menciona "retry com exponential backoff", mas o handler atual não tem proteção contra falhas repetidas. Se o Azure OpenAI estiver fora, o endpoint vai continuar tentando e falhando, consumindo recursos.

**Código atual:** Não há circuit breaker — cada request tenta independentemente.

**Risco:** Em cenário de falha do Azure, todas as requests falham lentamente em vez de falhar rápido (fail-fast).

**Correção proposta:** Adicionar circuit breaker pattern no serviço de completion (task T-003), mas o handler deveria já ter a estrutura para detectar estado "aberto" do circuit e retornar 503 imediatamente.

---

### 4. **Import de uuid pode falhar em ESM strict**

**Problema:** O import `import { v4 as uuidv4 } from "uuid"` pode ter problemas de compatibilidade com ESM dependendo da versão do uuid e configuração do TypeScript.

**Código atual (handler.ts:2):**
```typescript
import { v4 as uuidv4 } from "uuid";
```

**Risco:** Em runtime, pode dar erro `Named export 'v4' not found`.

**Correção proposta:**
```typescript
import { randomUUID } from "node:crypto";
// usar randomUUID() em vez de uuidv4()
```

O Node.js 16+ tem `crypto.randomUUID()` nativo — remove dependência externa e garante compatibilidade ESM.

---

## Pontos positivos do código gerado

1. **Estrutura correta de Azure Functions v4:** Usa `app.http()` em vez do modelo v3 deprecated.
2. **Zod safeParse:** Usa `safeParse` em vez de `parse`, evitando throw em validação.
3. **Correlation ID:** Implementa rastreabilidade de requests via header.
4. **Separação de concerns:** Validator separado do handler, logger em shared.
5. **Logging estruturado:** Usa pino com objetos em vez de strings concatenadas.

---

## Conclusão

O código atende aos critérios de aceite da T-001, mas **não está pronto para merge** sem os ajustes acima. Os pontos 1 (validação de env) e 4 (compatibilidade ESM) são blockers; os pontos 2 e 3 são melhorias que deveriam entrar antes de produção.

**Ação:** Ajustar pontos 1 e 4 antes do PR. Criar tasks de follow-up para pontos 2 e 3.
