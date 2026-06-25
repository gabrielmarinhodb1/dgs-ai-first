# Análise Detalhada por Pergunta
#### Pergunta 1: Qual o prazo geral de devolução?
**Pergunta original:** "Qual o prazo geral de devolucao?"
**Chunks no top-5:**
- POL-001 3.3 (procedimento)
- POL-001 3.1 (prazo geral: 7 dias úteis) ✅
- PROC-042-v1 (ruído: prazo de frete)

**Acerto:** Sim. Chunk com a resposta exata no top 2.
**Score:** 0.0848 (baixo, mas ainda recupera correto)

#### Pergunta 2: Como calcular frete especial para o Norte, 2000kg?
**Pergunta original:** "Como calcular frete especial para o Norte, 2000kg?" (com referência: 2026-01-15)
**Chunks no top-5:**
- PROC-042-v2 (seção 3: prazo)
- PROC-042-v2 (seção 2: fórmula + multiplicadores, Norte 1.8 + fator 1.15) ✅
- FAQ (ruído: frete expresso)

**Acerto:** Sim. Todos os valores corretos da v2 recuperados no top 2.
**Score:** 0.0898 e 0.0832 (baixo, mas versão correta priorizada)
**Evidência de versionamento:** Filtro temporal funcionou, v1 não apareceu como principal.
#### Pergunta 3: Existe tier Platinum?
**Pergunta original:** "Existe tier Platinum?"
**Chunks no top-5:**
- SLA-2024 (classificação de clientes)
- SLA-2024 (negação: "Não existem outros tiers além dos três") ✅
- PROC-042-v2 (ruído)

**Acerto:** Sim. Negação explícita no top 2.
**Score:** -0.0624 e -0.1610 (negativos, mas semântica correta)
#### Pergunta 4: Posso devolver carga perigosa?
**Pergunta original:** "Posso devolver carga perigosa?"
**Chunks no top-5:**
- PROC-042-v1 (ruído: frete para carga perigosa)
- FAQ (ruído: rastreamento)
- PROC-042-v2 (ruído: frete para carga perigosa)
- POL-001 3.2 (exceções: NÃO elegível) ✅ no top 4
- FAQ (ruído: desconto)

**Acerto:** Sim, mas degradado. Resposta correta presente no top 4, não top 2.
**Score:** -0.0203 (negativo, ranking subótimo)
**Problema identificado:** Domínio de frete contaminando pergunta de devolução.
#### Pergunta 5: Qual o SLA de resolução do cliente Gold?
**Pergunta original:** "Qual o SLA de resolução do cliente Gold?"
**Chunks no top-5:**
- SLA-2024 (classificação de clientes com tabela de tiers)
- SLA-2024 (tabela completa com SLA: Gold = 24h úteis) ✅
- FAQ (ruído: rastreamento)
- FAQ (ruído: devolução)
- POL-001 (ruído: procedimento)

**Acerto:** Sim. Valor exato (até 24h úteis) no top 2.
**Score:** 0.3177 (score mais alto na amostra)
