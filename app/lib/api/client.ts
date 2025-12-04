const getApiUrl = (): string => {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";
  return apiUrl.replace(/\/$/, "");
};

export interface ApiError {
  detail: string;
}

/**
 * Handle authentication/authorization errors from API responses
 * This is the server-side source of truth for auth state
 */
function handleAuthError(status: number, errorDetail: string): void {
  // Handle 401 Unauthorized - invalid or expired token
  if (status === 401) {
    // Redirect to login
    if (typeof window !== "undefined") {
      const currentPath = window.location.pathname;
      const loginUrl = `/login${
        currentPath !== "/login"
          ? `?redirect=${encodeURIComponent(currentPath)}`
          : ""
      }`;
      window.location.href = loginUrl;
    }
    return;
  }

  // Handle 403 Forbidden - typically email verification required
  if (status === 403) {
    // Check if it's an email verification issue
    const isEmailVerificationIssue =
      errorDetail.toLowerCase().includes("email verification") ||
      errorDetail.toLowerCase().includes("verification required");

    if (isEmailVerificationIssue && typeof window !== "undefined") {
      // Redirect to OTP verification page
      // If we have user email from response, include it in the URL
      window.location.href = "/verify-otp";
      return;
    }

    // Other 403 errors - redirect to login
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
    return;
  }
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${getApiUrl()}${endpoint}`;

  // Cookies are automatically sent by the browser
  // No need to manually add Authorization header
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  const response = await fetch(url, {
    ...options,
    headers,
    credentials: "include", // Important: send cookies with request
  });

  if (!response.ok) {
    let errorMessage = "An error occurred";
    let errorDetail = "";

    try {
      const errorData: ApiError = await response.json();
      errorMessage = errorData.detail || errorMessage;
      errorDetail = errorData.detail || "";
    } catch {
      errorMessage = `HTTP ${response.status}: ${response.statusText}`;
    }

    // Handle auth errors (401/403) - server is source of truth
    if (response.status === 401 || response.status === 403) {
      handleAuthError(response.status, errorDetail);
      // Throw error so calling code knows the request failed
      // The redirect will happen via handleAuthError
      throw new Error(errorMessage);
    }

    // For other errors, just throw
    throw new Error(errorMessage);
  }

  // Handle 204 No Content - no body to parse
  if (response.status === 204) {
    return undefined as T;
  }

  // Handle empty responses
  const contentType = response.headers.get("content-type");
  if (contentType && contentType.includes("application/json")) {
    return response.json();
  }

  return {} as T;
}
