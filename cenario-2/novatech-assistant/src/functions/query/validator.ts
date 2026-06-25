import { z } from "zod";

export const QueryInputSchema = z.object({
  question: z
    .string({
      required_error: "Campo 'question' é obrigatório",
      invalid_type_error: "Campo 'question' deve ser uma string",
    })
    .min(1, "Campo 'question' não pode estar vazio")
    .max(500, "Campo 'question' deve ter no máximo 500 caracteres"),
});

export type QueryInput = z.infer<typeof QueryInputSchema>;

export const QueryResponseSchema = z.object({
  answer: z.string(),
  source_document: z.string().min(1, "source_document é obrigatório"),
  confidence: z.enum(["high", "medium", "low"]),
});

export type QueryResponse = z.infer<typeof QueryResponseSchema>;

export const ErrorResponseSchema = z.object({
  error: z.object({
    code: z.string(),
    message: z.string(),
    details: z.array(z.string()).optional(),
  }),
});

export type ErrorResponse = z.infer<typeof ErrorResponseSchema>;

export function formatZodError(error: z.ZodError): ErrorResponse {
  return {
    error: {
      code: "VALIDATION_ERROR",
      message: "Input inválido",
      details: error.errors.map((e) => `${e.path.join(".")}: ${e.message}`),
    },
  };
}
