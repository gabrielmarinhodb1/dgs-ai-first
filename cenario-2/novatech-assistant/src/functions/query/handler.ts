import { app, HttpRequest, HttpResponseInit, InvocationContext } from "@azure/functions";
import { v4 as uuidv4 } from "uuid";
import { QueryInputSchema, formatZodError, ErrorResponse } from "./validator.js";
import { createRequestLogger } from "../../shared/logger.js";

async function queryHandler(
  request: HttpRequest,
  context: InvocationContext
): Promise<HttpResponseInit> {
  const correlationId = request.headers.get("x-correlation-id") || uuidv4();
  const log = createRequestLogger(correlationId);
  const startTime = Date.now();

  log.info({ method: request.method, url: request.url }, "Query request received");

  try {
    let body: unknown;
    try {
      body = await request.json();
    } catch {
      log.warn("Invalid JSON in request body");
      const errorResponse: ErrorResponse = {
        error: {
          code: "INVALID_JSON",
          message: "Request body deve ser um JSON válido",
        },
      };
      return {
        status: 400,
        jsonBody: errorResponse,
        headers: { "x-correlation-id": correlationId },
      };
    }

    const parseResult = QueryInputSchema.safeParse(body);

    if (!parseResult.success) {
      log.warn({ errors: parseResult.error.errors }, "Validation failed");
      return {
        status: 400,
        jsonBody: formatZodError(parseResult.error),
        headers: { "x-correlation-id": correlationId },
      };
    }

    const { question } = parseResult.data;
    log.info({ questionLength: question.length }, "Input validated successfully");

    const response = {
      answer: "Implementação pendente — tasks T-003 a T-009",
      source_document: "N/A",
      confidence: "low" as const,
    };

    const duration = Date.now() - startTime;
    log.info({ duration, status: 200 }, "Query request completed");

    return {
      status: 200,
      jsonBody: response,
      headers: { "x-correlation-id": correlationId },
    };
  } catch (error) {
    const duration = Date.now() - startTime;
    log.error({ error, duration }, "Unexpected error in query handler");

    const errorResponse: ErrorResponse = {
      error: {
        code: "INTERNAL_ERROR",
        message: "Erro interno do servidor",
      },
    };

    return {
      status: 500,
      jsonBody: errorResponse,
      headers: { "x-correlation-id": correlationId },
    };
  }
}

app.http("query", {
  methods: ["POST"],
  route: "query",
  authLevel: "anonymous",
  handler: queryHandler,
});

export { queryHandler };
