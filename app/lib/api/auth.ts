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

  verifyOtp: async (email: string, code: string): Promise<LoginResponse> => {
    return apiRequest<LoginResponse>("/api/v1/auth/verify-otp", {
      method: "POST",
      body: JSON.stringify({ email, code }),
    });
  },

  logout: async (): Promise<{ message: string }> => {
    return apiRequest<{ message: string }>("/api/v1/auth/logout", {
      method: "POST",
    });
  },
};
