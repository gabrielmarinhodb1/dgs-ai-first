import { app, HttpRequest, HttpResponseInit, InvocationContext } from '@azure/functions';
import { CosmosClient } from '@azure/cosmos';
import { v4 as uuidv4 } from 'uuid';
import { FeedbackInputSchema, formatZodError, ErrorResponse } from './validator.js';
import { createRequestLogger } from '../../shared/logger.js';

const client = new CosmosClient(process.env.COSMOS_CONNECTION_STRING ?? '');
const container = client
  .database(process.env.COSMOS_DB_NAME ?? 'novatech')
  .container(process.env.COSMOS_FEEDBACK_CONTAINER ?? 'feedbacks');

export async function feedbackHandler(
  request: HttpRequest,
  _context: InvocationContext
): Promise<HttpResponseInit> {
  const correlationId = request.headers.get('x-correlation-id') || uuidv4();
  const log = createRequestLogger(correlationId);

  log.info({ method: request.method, url: request.url }, 'Feedback request received');

  try {
    let body: unknown;
    try {
      body = await request.json();
    } catch {
      log.warn('Invalid JSON in request body');
      const errorResponse: ErrorResponse = {
        error: { code: 'INVALID_JSON', message: 'Request body deve ser um JSON válido' },
      };
      return {
        status: 400,
        jsonBody: errorResponse,
        headers: { 'x-correlation-id': correlationId },
      };
    }

    const parseResult = FeedbackInputSchema.safeParse(body);
    if (!parseResult.success) {
      log.warn({ errors: parseResult.error.errors }, 'Validation failed');
      return {
        status: 400,
        jsonBody: formatZodError(parseResult.error),
        headers: { 'x-correlation-id': correlationId },
      };
    }

    const { queryId, rating, comment, attendantEmail } = parseResult.data;

    const feedback = {
      id: uuidv4(),
      queryId,
      rating,
      comment,
      attendantEmail,
      timestamp: new Date().toISOString(),
    };

    log.info({ queryId, rating }, 'Saving feedback');
    await container.items.create(feedback);
    log.info({ queryId }, 'Feedback saved successfully');

    return {
      status: 200,
      jsonBody: { success: true },
      headers: { 'x-correlation-id': correlationId },
    };
  } catch (error) {
    log.error({ error }, 'Unexpected error in feedback handler');
    const errorResponse: ErrorResponse = {
      error: { code: 'INTERNAL_ERROR', message: 'Erro interno do servidor' },
    };
    return {
      status: 500,
      jsonBody: errorResponse,
      headers: { 'x-correlation-id': correlationId },
    };
  }
}

app.http('feedback', {
  methods: ['POST'],
  route: 'feedback',
  authLevel: 'anonymous',
  handler: feedbackHandler,
});
