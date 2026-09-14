import axios from "axios";

interface ApiErrorPayload {
  code?: string;
  message?: string;
  details?: Record<string, unknown>;
  request_id?: string;
}

export interface AppError {
  kind:
    | "validation"
    | "credentials"
    | "session"
    | "csrf"
    | "permission"
    | "rate"
    | "network"
    | "server";
  message: string;
  fields: Record<string, string>;
  retryable: boolean;
  status?: number;
  code?: string;
}

function fieldErrors(details: Record<string, unknown> | undefined): Record<string, string> {
  if (!details) return {};
  return Object.fromEntries(
    Object.entries(details)
      .map(([key, value]) => {
        const first: unknown = Array.isArray(value) ? (value as unknown[])[0] : value;
        return [key, typeof first === "string" ? first : ""] as const;
      })
      .filter(([, value]) => Boolean(value)),
  );
}

export function toAppError(error: unknown): AppError {
  if (!axios.isAxiosError<ApiErrorPayload>(error)) {
    return {
      kind: "server",
      message: "Đã xảy ra lỗi không xác định.",
      fields: {},
      retryable: false,
    };
  }
  if (!error.response) {
    return {
      kind: "network",
      message: "Không thể kết nối máy chủ. Vui lòng kiểm tra mạng và thử lại.",
      fields: {},
      retryable: true,
    };
  }

  const { status, data } = error.response;
  const code = data.code;
  const common = { status, code, fields: fieldErrors(data.details), retryable: false };
  if (code === "invalid_credentials") {
    return { ...common, kind: "credentials", message: "Email hoặc mật khẩu không đúng." };
  }
  if (code === "csrf_failed") {
    return { ...common, kind: "csrf", message: "Phiên bảo mật đã hết hạn. Vui lòng thử lại." };
  }
  if (status === 401 || code === "session_missing" || code === "token_not_valid") {
    return { ...common, kind: "session", message: "Phiên đăng nhập đã hết hạn." };
  }
  if (status === 403) {
    return { ...common, kind: "permission", message: "Bạn không có quyền thực hiện thao tác này." };
  }
  if (status === 429) {
    return { ...common, kind: "rate", message: "Bạn thao tác quá nhanh. Vui lòng thử lại sau." };
  }
  if (status === 400) {
    return { ...common, kind: "validation", message: data.message || "Dữ liệu chưa hợp lệ." };
  }
  return {
    ...common,
    kind: "server",
    message: "Máy chủ đang gặp sự cố. Vui lòng thử lại sau.",
    retryable: status >= 500,
  };
}

export function isSessionRejection(error: unknown): boolean {
  const appError = toAppError(error);
  return appError.kind === "session" || appError.kind === "validation";
}
