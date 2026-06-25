---
name: typescript-conventions
level: foundation
description: >-
  Acione SEMPRE que for criar ou editar qualquer arquivo .ts/.tsx do NovaTech
  Assistant. Define strict mode, imports ESM com extensão .js, proibição de any,
  validação Zod nas bordas e convenções de nomenclatura. É a skill BASE — toda
  outra skill (Domain e Artifact) que gere código a pressupõe.
owner: Tech Lead
inherits: []
references:
  - tsconfig.json (strict: true, module ESNext)
  - AGENTS.md › Coding Standards
  - ADR-0001 (Azure OpenAI / GPT-4o), ADR-0002 (context budget)
  - src/functions/query/ (código de referência do projeto)
---

# Skill Foundation — TypeScript Conventions (NovaTech Assistant)

## Contexto — quando usar

Esta é a skill **raiz** do projeto. Aplique-a em **todo** arquivo TypeScript do repositório `novatech-assistant`: handlers de Azure Functions, services, pipeline de ingestão, bot do Teams, componentes React e testes. As skills `error-handling`, `project-structure`, `azure-functions-endpoint`, `testing-patterns` e todas as receitas `artifact/*` **herdam** estas regras — não as repita lá, referencie esta skill.

O projeto roda em **ESM** (`package.json` → `"type": "module"`), **TypeScript 5.4 strict** e **Node 20** (`tsconfig.json` → `strict: true`, `target: ES2022`, `module: ESNext`). Validação de fronteira é feita com **Zod 3**; logging com **pino**. Essas escolhas vêm das ADRs e do scaffold do cenário 1 — não as renegocie ao gerar código.

---

## Regras prescritivas

Use os verbos no imperativo. Cada regra é uma instrução acionável por um agente.

### R1 — `strict` é inviolável. Nunca contorne o type checker.
- **DEVE** tipar explicitamente parâmetros e retornos de funções exportadas.
- **NÃO DEVE** usar `any`, `as any`, `// @ts-ignore` ou `// @ts-expect-error` para silenciar erros. Dado externo entra como `unknown` e é estreitado com Zod.

### R2 — Imports locais SEMPRE com extensão `.js` (ESM).
Como o projeto é ESM, módulos locais são importados com a extensão `.js` mesmo que o arquivo-fonte seja `.ts` (é assim que o `src/functions/query/handler.ts` já importa). Pacotes de `node_modules` não levam extensão.

### R3 — Valide toda entrada externa com Zod, na borda.
Body de request, variáveis de ambiente, payload de fila, resposta do GPT-4o: tudo que cruza a fronteira do processo é validado com um schema Zod antes de ser usado. Derive os tipos do schema com `z.infer` — **não** declare a `interface` em paralelo (vira fonte dupla de verdade).

### R4 — Nomenclatura.
- `PascalCase` para tipos, schemas Zod (`QueryInputSchema`), classes e componentes React.
- `camelCase` para variáveis e funções (`createRequestLogger`, `queryHandler`).
- `UPPER_SNAKE_CASE` para constantes de módulo (`MAX_QUESTION_LENGTH`).
- Nomes de **identificadores, tipos e comentários em inglês** (AGENTS.md › Coding Standards). Mensagens voltadas ao atendente, em português.

### R5 — Sempre exports nomeados. Nunca `export default`.
Exports nomeados são refatoráveis e auto-importáveis pelo Copilot sem ambiguidade. `export default` quebra renomeações e gera imports inconsistentes.

### R6 — `catch` é tipado e nunca engole o erro.
`catch (error)` recebe `unknown` (default do strict). Estreite antes de acessar propriedades e logue com **pino** (`error-handling`). Proibido `console.log`/`console.error` em código de produção — o painel e o CI consomem log estruturado.

### R7 — Imutabilidade por padrão.
`const` por padrão; `let` só quando há reatribuição real. Marque dados que não mudam como `readonly`/`as const`. Não mute parâmetros recebidos.

### R8 — Nada de números/strings mágicos de domínio no meio do código.
Limites do domínio (budget de contexto da ADR-0002, top-5 chunks, 500 chars de pergunta) vivem em constantes nomeadas ou em `src/shared/config.ts`, não espalhados.

---

## Exemplos (DO / DON'T) — código real do projeto

### Validação de borda com Zod (R1, R3)

✅ **DO** — dado externo entra como `unknown`, Zod estreita, tipo derivado do schema:
```ts
import { z } from "zod";

export const QueryInputSchema = z.object({
  question: z.string().min(1).max(500),
});

// Single source of truth: the type is derived from the schema.
export type QueryInput = z.infer<typeof QueryInputSchema>;

export function parseQuery(body: unknown): QueryInput {
  return QueryInputSchema.parse(body); // throws ZodError on invalid input
}
```

❌ **DON'T** — `any` na borda + interface paralela que diverge do schema:
```ts
interface QueryInput {        // duplicates the schema, drifts over time
  question: string;
}

export function parseQuery(body: any): QueryInput {  // <-- `any` disables strict
  return body as QueryInput;   // <-- no validation: garbage flows downstream
}
```

### Imports ESM (R2)

✅ **DO**:
```ts
import { app, HttpRequest } from "@azure/functions";          // package: no extension
import { QueryInputSchema } from "./validator.js";            // local: .js extension
import { createRequestLogger } from "../../shared/logger.js"; // local: .js extension
```

❌ **DON'T**:
```ts
import { QueryInputSchema } from "./validator";   // ERR_MODULE_NOT_FOUND at runtime (ESM)
import { createRequestLogger } from "../../shared/logger.ts"; // .ts não resolve em ESM
```

### Tratamento de erro tipado (R6)

✅ **DO**:
```ts
import { createRequestLogger } from "../../shared/logger.js";

try {
  await indexer.upsert(chunk);
} catch (error: unknown) {
  const message = error instanceof Error ? error.message : "unknown error";
  log.error({ error: message, chunkId: chunk.id }, "Failed to index chunk");
  throw error;
}
```

❌ **DON'T**:
```ts
try {
  await indexer.upsert(chunk);
} catch (e: any) {              // `any` no catch
  console.log("erro", e);      // console.log + sem correlation id + texto não estruturado
}
```

### Exports e constantes de domínio (R5, R8)

✅ **DO**:
```ts
// Domain limits from ADR-0002 (context budget). Named, not magic.
export const MAX_QUESTION_LENGTH = 500;
export const TOP_K_CHUNKS = 5;

export function buildQuery(question: string): SearchQuery { /* ... */ }
```

❌ **DON'T**:
```ts
export default function (q: string) {        // default export + parâmetro anônimo
  return search(q, 5);                       // 5 mágico: nem rastreia a ADR-0002
}
```

---

## Anti-padrões (o que o Copilot gera de errado sem esta skill)

Estes são erros **observados em geração assistida** — corrija-os no review e, se recorrerem, reforce a regra correspondente:

| Anti-padrão | Por que o Copilot faz | Regra violada | Correção |
|---|---|---|---|
| `as any` / `: any` para "destravar" o build | É o caminho de menor resistência contra o strict | R1 | `unknown` + estreitamento Zod |
| `import "./x"` sem `.js` | Hábito de CommonJS/bundler | R2 | adicionar `.js` |
| `console.log` para debug/erro | Default da maioria dos exemplos da web | R6 | `logger`/`createRequestLogger` (pino) |
| `interface Foo` declarada ao lado de um schema Zod | Reflexo de "tipar tudo à mão" | R3 | `type Foo = z.infer<typeof FooSchema>` |
| `export default` em handler/service | Padrão comum em exemplos React/Express | R5 | export nomeado |
| `catch (e)` e acesso direto a `e.message` | Pré-TS 4.4, quando `catch` era `any` | R6 | `catch (error: unknown)` + `instanceof Error` |
| `require(...)` dinâmico ou `module.exports` | Mistura CommonJS em projeto ESM | R2/R5 | `import`/`export` estáticos |
| Números de budget/top-K inline | Não conhece as ADRs | R8 | constantes nomeadas / `config.ts` |
| Mensagens de erro de domínio em inglês para o atendente | Não sabe da regra de idioma | R4 | texto ao usuário em PT-BR, código/identificadores em EN |

---

## Dependências

- **Herda de:** nenhuma (esta é a base).
- **É herdada por:** `foundation/error-handling`, `foundation/project-structure`, `domain/azure-functions-endpoint`, `domain/azure-ai-search-integration`, `domain/react-components`, `domain/testing-patterns`, e todas as receitas em `artifact/`.
- **Lida em conjunto com:** `AGENTS.md › Coding Standards` (fonte das decisões), `tsconfig.json` (enforcement automático do strict).
