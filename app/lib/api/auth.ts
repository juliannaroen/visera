import { apiRequest } from "./client";
import type { LoginRequest, LoginResponse, User } from "../types/auth";

export const authApi = {
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    return apiRequest<LoginResponse>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify(credentials),
    });
  },

  getCurrentUser: async (): Promise<User> => {
    return apiRequest<User>("/api/v1/auth/me");
  },

  sendVerificationEmail: async (
    email?: string
  ): Promise<{ message: string }> => {
    const body = email ? JSON.stringify({ email }) : undefined;
    return apiRequest<{ message: string }>(
      "/api/v1/auth/send-verification-email",
      {
        method: "POST",
        body,
      }
    );
  },

  verifyEmail: async (token: string): Promise<User> => {
    return apiRequest<User>("/api/v1/auth/verify-email", {
      method: "POST",
      body: JSON.stringify({ token }),
    });
  },
};
