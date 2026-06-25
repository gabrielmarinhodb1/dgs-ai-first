import { z } from 'zod';

export const FeedbackInputSchema = z.object({
  queryId: z.string().min(1),
  rating: z.number().int().min(1).max(5),
  comment: z.string().optional(),
  attendantEmail: z.string().email(),
});

export type FeedbackInput = z.infer<typeof FeedbackInputSchema>;

export interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: unknown;
  };
}

export function formatZodError(error: z.ZodError): ErrorResponse {
  return {
    error: {
      code: 'VALIDATION_ERROR',
      message: 'Dados de entrada inválidos',
      details: error.errors,
    },
  };
}
