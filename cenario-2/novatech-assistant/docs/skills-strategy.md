# Estratégia de Skills — NovaTech Assistant

> **Papel:** Desenvolvedor (Sênior) · **Exercício:** 2.3 — Definição de estratégia de skills do projeto
> **Ferramentas:** Claude (chat) — desenho da árvore e da governança · GitHub Copilot — geração do SKILL.md Foundation
> **Referências:** Anexo C (estrutura `/skills/`), ADR-0001/0002/0003/0004 (cenário 1), guardrails de produto, Testing Standards.

Este documento define **quais skills o projeto precisa, quem as cria e como são mantidas**. Skills não são documentação solta: são artefatos prescritivos lidos por agentes (Copilot, Claude Code) **antes de gerar código ou artefatos**, para que o output saia consistente com os padrões do NovaTech sem revisão manual repetitiva.

---

## 1. Princípio da hierarquia

As skills seguem a hierarquia obrigatória do Anexo C (`/skills/foundation/`, `/skills/domain/`, `/skills/artifact/`). A regra de composição é **de baixo para cima — cada nível herda o anterior**:

```
Foundation  → convenções globais, válidas para TODO arquivo do repo (linguagem, erros, estrutura).
   ▲ herdada por
Domain      → padrões de UMA camada (endpoint, busca, React, testes, spec).
   ▲ herdada por
Artifact    → receita ponta-a-ponta de UM entregável concreto ("gere o endpoint X").
```

Uma skill Artifact **nunca repete** o que está numa Foundation/Domain — ela referencia (`ver skills/foundation/typescript-conventions.md`). Assim, mudar uma convenção global se faz em **um** arquivo, não em dez receitas.

> **Skill Foundation base:** `typescript-conventions` é a raiz da árvore — toda outra skill (Foundation, Domain ou Artifact) que gere ou edite código `.ts` a pressupõe. Por isso é a skill cujo SKILL.md foi escrito primeiro (entregável 3, abaixo).

---

## 2. Árvore de skills

A árvore estende a proposta inicial para cobrir **as 5 famílias de artefato repetitivo** do projeto (endpoints RAG, testes de integração, componentes React, documentação técnica/ADRs, specs SDD). Caminhos batem 1:1 com o Anexo C.

```
skills/
├── foundation/                         # convenções globais — herdadas por TUDO
│   ├── typescript-conventions.md       # [BASE] strict mode, ESM .js, no-any, naming, Zod nas bordas
│   ├── error-handling.md               # custom errors, retry c/ backoff (Azure), pino, correlation-id
│   ├── project-structure.md            # layout do Anexo C, fronteiras de módulo, exports nomeados
│   └── documentation-conventions.md    # PT-BR em status/docs, EN em código/comments, formato ADR/README
│
├── domain/                             # padrões por camada — herdam Foundation
│   ├── azure-functions-endpoint.md     # padrão HTTP trigger v4, validação, formato de erro
│   ├── azure-ai-search-integration.md  # query top-5, context budget (ADR-0002), vigência (ADR-0003)
│   ├── react-components.md             # padrões do painel web (cards, formulários de feedback)
│   ├── testing-patterns.md             # Vitest, msw, fixtures, AAA (consistente c/ Testing Standards)
│   └── sdd-spec-format.md              # estrutura requirements/plan/tasks, verification criteria
│
└── artifact/                           # receitas de geração — herdam Foundation + Domain
    ├── create-rag-endpoint.md          # endpoint Azure Function com pipeline RAG completo
    ├── create-integration-test.md      # teste de integração de endpoint (msw + fixtures)
    ├── create-react-card.md            # card de resposta / formulário de feedback
    ├── create-adr.md                   # ADR em /docs/adr/ + README de módulo
    └── write-requirements-spec.md      # requirements.md SDD a partir de bounded context
```

**Cobertura da lista de artefatos repetitivos (input do exercício):**

| Artefato que se repete no projeto | Skill Artifact | Skills Domain/Foundation que herda |
|---|---|---|
| Endpoints Azure Functions com padrão RAG | `create-rag-endpoint` | `azure-functions-endpoint`, `azure-ai-search-integration` + base |
| Testes de integração para endpoints | `create-integration-test` | `testing-patterns` + base |
| Componentes React do painel | `create-react-card` | `react-components` + base |
| Documentação técnica (ADRs, README de módulo) | `create-adr` | `documentation-conventions` + base |
| Specs de produto (template SDD) | `write-requirements-spec` | `sdd-spec-format` + `documentation-conventions` |

---

## 3. Mapa de criação e consumo

Para cada skill: **frase-ativação** (o que um agente reconhece para acionar a skill), **quem cria** (papel responsável pela autoria/manutenção), **quem consome** (papel + agente) e **frequência de uso estimada**.

Escala de frequência: **Alta** = aplicada em quase toda geração de código · **Média** = a cada novo módulo/feature (semanal) · **Baixa** = pontual (a cada decisão/marco).

### Foundation

| Skill | Frase-ativação | Cria | Consome (papel + agente) | Frequência |
|---|---|---|---|---|
| `typescript-conventions` | "escrevendo ou editando qualquer arquivo `.ts`/`.tsx`" | Tech Lead | Devs (pleno/sênior), QA, PS · Copilot + Claude Code | **Alta** (toda geração de código) |
| `error-handling` | "tratando falhas, chamando Azure, ou logando algo" | Dev Sênior | Devs · Copilot + Claude Code | **Alta** |
| `project-structure` | "criando um arquivo novo e decidindo onde ele vai" | Tech Lead | Todos os devs · Copilot + Claude Code | **Média** |
| `documentation-conventions` | "escrevendo um documento, ADR, README ou comentário" | Delivery Manager (idioma) + Tech Lead (formato) | Todos os papéis · Claude + Cowork | **Média** |

### Domain

| Skill | Frase-ativação | Cria | Consome (papel + agente) | Frequência |
|---|---|---|---|---|
| `azure-functions-endpoint` | "criando um endpoint HTTP em Azure Functions" | Tech Lead | Devs · Copilot + Claude Code | **Média** |
| `azure-ai-search-integration` | "buscando chunks ou montando contexto de RAG" | Dev Sênior | Dev Sênior · Copilot + Claude Code | **Média** |
| `react-components` | "criando um componente do painel web" | Dev Pleno | Dev Pleno + PS · Copilot | **Baixa/Média** |
| `testing-patterns` | "escrevendo testes (unit/integration) com Vitest" | QA | Devs + QA · Copilot + Claude Code | **Alta** |
| `sdd-spec-format` | "estruturando requirements/plan/tasks de um módulo" | Product Specialist (req) + Tech Lead (plan) | PS, TL, Dev · Claude + Cowork | **Média** |

### Artifact

| Skill | Frase-ativação | Cria | Consome (papel + agente) | Frequência |
|---|---|---|---|---|
| `create-rag-endpoint` | "gere o endpoint completo do módulo X com padrão RAG" | Dev Sênior | Dev pleno/sênior · Copilot + Claude Code | **Média** |
| `create-integration-test` | "gere o teste de integração para o endpoint X" | QA | Devs + QA · Copilot + Claude Code | **Média/Alta** |
| `create-react-card` | "gere o card de resposta / formulário de feedback" | Dev Pleno | Dev Pleno · Copilot | **Baixa** |
| `create-adr` | "registre esta decisão como ADR" / "gere o README do módulo" | Tech Lead | TL + Devs · Claude | **Baixa** |
| `write-requirements-spec` | "escreva o requirements.md do módulo X" | Product Specialist | PS · Claude + Claude Design | **Média** |

**Visão de time (não é só para devs):** a propriedade das skills é distribuída deliberadamente —
- **Product Specialist** é dono de `write-requirements-spec` e co-autor de `sdd-spec-format` (specs e linguagem ubíqua nascem de produto).
- **QA** é dono de `testing-patterns` e `create-integration-test` (o padrão de teste pertence a quem revisa teste).
- **Delivery Manager** governa o idioma em `documentation-conventions` (PT-BR em status, EN em código).
- **Tech Lead** mantém as Foundation técnicas e `create-adr`.
- **Devs** consomem quase tudo e mantêm as receitas Artifact de código.

---

## 4. Manutenção e ciclo de vida ("skill madura")

Skills são **artefatos vivos**, versionados via Git em `/skills/` (Conventional Commits, ex.: `docs(skills): refina anti-padrões de typescript-conventions`).

**Quando criar uma skill nova:** quando um mesmo tipo de artefato for gerado **3+ vezes** e o agente repetir o mesmo erro corrigido em code review. Antes disso, a regra mora no AGENTS.md.

**Critérios de "skill madura"** (pronta para o time depender dela sem revisão pesada):
1. Tem exemplos de código **reais** do repo (DO/DON'T), não pseudocódigo.
2. Foi **testada com Copilot**: gerou ≥1 artefato que passou no validation gate sem retrabalho de convenção.
3. Os anti-padrões cobrem os erros observados em code review (não são genéricos).
4. Declara dependências de outras skills (`herda foundation/...`).
5. Tem um dono (papel) responsável por atualizá-la quando uma ADR mudar.

**Mudança de uma convenção global:** edita-se a Foundation; as Domain/Artifact que a herdam não mudam (só referenciam). Um diff em `typescript-conventions.md` deve ser comunicado no canal do time porque propaga para toda geração de código.

---

## 5. Evidência de uso das ferramentas

**Claude (chat) — desenho da árvore e governança.** Prompt inicial: *"Dada a lista de artefatos repetitivos do NovaTech e a hierarquia Foundation→Domain→Artifact do Anexo C, proponha a árvore de skills mínima que cobre os 5 tipos de artefato, sem skill que ninguém consumiria."* Iteração: a primeira árvore só cobria 3 famílias (endpoint, teste, React); pedi a cobertura de **documentação** e **specs**, o que adicionou `documentation-conventions`, `sdd-spec-format`, `create-adr` e `write-requirements-spec`. Segunda iteração ajustou a **propriedade multi-papel** (mover `testing-patterns` para QA e `write-requirements-spec` para o PS), atendendo ao critério de "visão de time".

**GitHub Copilot — geração do SKILL.md Foundation.** Com o `AGENTS.md` e o código já existente (`src/functions/query/`) no contexto, pedi ao Copilot que gerasse `skills/foundation/typescript-conventions.md`. O rascunho inicial trouxe regras corretas mas **abstratas** ("use tipos fortes"); a revisão crítica substituiu cada regra abstrata por um par **DO/DON'T com código real** e adicionou os anti-padrões que o próprio Copilot tende a gerar sem guidance (`as any`, `console.log`, import sem extensão `.js`, `catch (e)` sem tipo, `export default`). Resultado em [skills/foundation/typescript-conventions.md](../skills/foundation/typescript-conventions.md).
