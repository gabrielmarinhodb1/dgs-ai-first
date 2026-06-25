# Code review

- não deve ser tipado com any, pois ficam sem validação
- console.log indevido com dados sensiveis
- database e container estão fixos então poderiamos mover para variáveis de ambiente (COSMOS_DB_NAME, COSMOS_FEEDBACK_CONTAINER)
- import com require, deve ser um import estático
- falta tratamento de erro se falhar parse do JSON ou gravação no Cosmos, a função quebra sem resposta consistente