# Mapeamento de contexto estático/dinâmico

### Estático:

- identidade do assistente
- guardrails
- prioridade entre fontes
- formato de saída
- política de “não inventar”
- política para insuficiência de contexto

___

### Dinâmico por query:

- chunks recuperados
- pergunta do atendente
- eventuais metadados do cliente

___

### Estimativa:

~350 a 500 tokens, dependendo do texto final


# Análise crítica

A v1 passou nos testes propostos, mas isso não garante robustez em produção. Os testes cobriram casos relativamente controlados, com poucos chunks e baixo conflito contextual. A revisão para v2 teve caráter preventivo, com foco em reduzir ambiguidade, aumentar rastreabilidade e melhorar a resposta em cenários de conflito, exceção e informação incompleta.

#### Por que evoluir para v2 se a v1 já acertou?

- Porque acertar 3 casos de teste não prova robustez diante de contradições documentais.
- Porque a v2 transforma comportamentos desejáveis em regras mais explícitas.
- Porque a v2 melhora auditabilidade, especialmente em respostas parciais ou com conflito de fontes.