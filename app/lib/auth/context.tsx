"use client";

import React, { createContext, useContext, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { authApi } from "../api/auth";
import type {
  User,
  LoginRequest,
  LoginResponse,
  AuthState,
} from "../types/auth";

interface AuthContextType extends AuthState {
  login: (credentials: LoginRequest) => Promise<LoginResponse>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const router = useRouter();

  const logout = useCallback(async () => {
    try {
      // Call backend logout endpoint to clear cookie
      await authApi.logout();
    } catch (error) {
      // Even if logout API call fails, clear local state
      console.error("Logout error:", error);
    } finally {
      setUser(null);
      router.push("/login");
    }
  }, [router]);

  const refreshUser = useCallback(async () => {
    try {
      const userData = await authApi.getCurrentUser();
      setUser(userData);
    } catch (error) {
      // Cookie is invalid/expired, API client will handle redirect
      setUser(null);
      throw error;
    }
  }, []);

  const login = async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response = await authApi.login(credentials);
    setUser(response.user);
    return response;
  };

  const value: AuthContextType = {
    user,
    token: null, // Token is in httpOnly cookie, not accessible to JavaScript
    isAuthenticated: !!user, // User presence indicates auth (validated by backend)
    login,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext)!;
}
