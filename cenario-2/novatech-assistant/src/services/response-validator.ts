import { z } from "zod";
import { logger } from "../shared/logger.js";

export const StructuredOutputSchema = z
	.object({
		answer: z.string().min(1, "answer é obrigatório"),
		source_document: z.string().trim().min(1, "source_document é obrigatório"),
		confidence_score: z.number().min(0).max(1),
	})
	.strict();

export type StructuredOutput = z.infer<typeof StructuredOutputSchema>;

export const SAFE_FALLBACK_RESPONSE: StructuredOutput = {
	answer:
		"Não foi possível responder com segurança com base na documentação disponível. Encaminhe para revisão humana.",
	source_document: "N/A",
	confidence_score: 0,
};

type ValidationFailureReason =
	| "SCHEMA_VALIDATION_FAILED"
	| "DANGEROUS_CARGO_RETURN_RULE_VIOLATION";

export type ResponseValidationResult =
	| {
			ok: true;
			response: StructuredOutput;
		}
	| {
			ok: false;
			reason: ValidationFailureReason;
			response: StructuredOutput;
			details?: string[];
		};

function normalizeText(text: string): string {
	return text
		.normalize("NFD")
		.replace(/[\u0300-\u036f]/g, "")
		.toLowerCase();
}

function shouldBlockDangerousCargoReturn(answer: string): boolean {
	const normalizedAnswer = normalizeText(answer);

	const mentionsDangerousCargo =
		normalizedAnswer.includes("carga perigosa") ||
		normalizedAnswer.includes("cargas perigosas");
	const mentionsReturn =
		normalizedAnswer.includes("devolucao") ||
		normalizedAnswer.includes("devolucoes") ||
		normalizedAnswer.includes("devolva") ||
		normalizedAnswer.includes("devolver") ||
		normalizedAnswer.includes("retorno") ||
		normalizedAnswer.includes("retornar");

	if (!mentionsDangerousCargo || !mentionsReturn) {
		return false;
	}

	const hasNegativeSignal =
		/(nao|não)\s+(pode|permit|autoriz|possivel)/.test(normalizedAnswer) ||
		/impossivel|proibid|vedad/.test(normalizedAnswer);

	const hasAffirmativeSignal =
		/\b(sim|pode|permitid|autorizad|possivel)\b/.test(normalizedAnswer);

	if (hasAffirmativeSignal && !hasNegativeSignal) {
		return true;
	}

	return false;
}

function parseUnknownResponse(input: unknown): unknown {
	if (typeof input !== "string") {
		return input;
	}

	try {
		return JSON.parse(input);
	} catch {
		return input;
	}
}

export function validateResponseWithGuardrails(input: unknown): ResponseValidationResult {
	const parsedInput = parseUnknownResponse(input);
	const parseResult = StructuredOutputSchema.safeParse(parsedInput);

	if (!parseResult.success) {
		const details = parseResult.error.errors.map((issue) => {
			const path = issue.path.length > 0 ? issue.path.join(".") : "root";
			return `${path}: ${issue.message}`;
		});

		logger.warn(
			{
				reason: "SCHEMA_VALIDATION_FAILED",
				details,
			},
			"Model response rejected by structured output schema"
		);

		return {
			ok: false,
			reason: "SCHEMA_VALIDATION_FAILED",
			details,
			response: SAFE_FALLBACK_RESPONSE,
		};
	}

	const response = parseResult.data;

	if (shouldBlockDangerousCargoReturn(response.answer)) {
		logger.warn(
			{
				reason: "DANGEROUS_CARGO_RETURN_RULE_VIOLATION",
				source_document: response.source_document,
			},
			"Model response blocked by dangerous cargo return guardrail"
		);

		return {
			ok: false,
			reason: "DANGEROUS_CARGO_RETURN_RULE_VIOLATION",
			response: SAFE_FALLBACK_RESPONSE,
		};
	}

	return {
		ok: true,
		response,
	};
}
