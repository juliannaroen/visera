const getApiUrl = (): string => {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";
  return apiUrl.replace(/\/$/, "");
};

export interface ApiError {
  detail: string;
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

    try {
      const errorData: ApiError = await response.json();
      errorMessage = errorData.detail || errorMessage;
    } catch {
      errorMessage = `HTTP ${response.status}: ${response.statusText}`;
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
