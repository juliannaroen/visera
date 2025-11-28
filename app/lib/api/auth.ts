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
};
