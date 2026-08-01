import type { AxiosError } from "axios";

export type ApiErrorKind = "validation" | "unauthorized" | "forbidden" | "server" | "network" | "unknown";

/** Normalized shape every part of the app can rely on, regardless of what
 * the backend actually returned. Nothing outside lib/api should touch
 * AxiosError directly. */
export class ApiError extends Error {
  readonly kind: ApiErrorKind;
  readonly status: number | null;
  readonly fieldErrors: Record<string, string[]>;

  constructor(message: string, kind: ApiErrorKind, status: number | null, fieldErrors: Record<string, string[]> = {}) {
    super(message);
    this.name = "ApiError";
    this.kind = kind;
    this.status = status;
    this.fieldErrors = fieldErrors;
  }
}

export interface DrfErrorBody {
  detail?: string;
  [field: string]: unknown;
}

function kindForStatus(status: number | null): ApiErrorKind {
  if (status === null) return "network";
  if (status === 401) return "unauthorized";
  if (status === 403) return "forbidden";
  if (status === 422 || status === 400) return "validation";
  if (status >= 500) return "server";
  return "unknown";
}

function extractFieldErrors(body: DrfErrorBody | undefined): Record<string, string[]> {
  if (!body) return {};
  const fieldErrors: Record<string, string[]> = {};
  for (const [key, value] of Object.entries(body)) {
    if (key === "detail") continue;
    if (Array.isArray(value)) {
      fieldErrors[key] = value.map(String);
    } else if (typeof value === "string") {
      fieldErrors[key] = [value];
    }
  }
  return fieldErrors;
}

export function normalizeAxiosError(error: AxiosError<DrfErrorBody>): ApiError {
  if (!error.response) {
    return new ApiError("Unable to reach the server. Check your connection and try again.", "network", null);
  }
  const status = error.response.status;
  const kind = kindForStatus(status);
  const body = error.response.data;
  const fieldErrors = extractFieldErrors(body);
  const message =
    body?.detail ??
    (kind === "unauthorized"
      ? "Your session has expired. Please sign in again."
      : kind === "forbidden"
        ? "You don't have permission to do that."
        : kind === "server"
          ? "Something went wrong on our end. Please try again shortly."
          : "That didn't go through — check the highlighted fields.");

  return new ApiError(message, kind, status, fieldErrors);
}
