"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { authApi } from "../api/auth";
import { tokenStorage, userStorage, clearAuthStorage } from "./storage";
import type { User, LoginRequest, AuthState } from "../types/auth";

interface AuthContextType extends AuthState {
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // Initialize auth state from storage
  useEffect(() => {
    const storedToken = tokenStorage.getToken();
    const storedUser = userStorage.getUser();

    if (storedToken && storedUser) {
      try {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));
      } catch (error) {
        // Invalid stored data, clear it
        clearAuthStorage();
      }
    }
    setIsLoading(false);
  }, []);

  // Verify token and fetch user on mount if token exists
  useEffect(() => {
    if (token && !user) {
      refreshUser().catch(() => {
        // Token is invalid, clear auth
        logout();
      });
    }
  }, [token]);

  const login = async (credentials: LoginRequest) => {
    try {
      const response = await authApi.login(credentials);
      setToken(response.access_token);
      setUser(response.user);
      tokenStorage.setToken(response.access_token);
      userStorage.setUser(JSON.stringify(response.user));
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    clearAuthStorage();
    router.push("/login");
  };

  const refreshUser = async () => {
    if (!token) return;
    try {
      const userData = await authApi.getCurrentUser();
      setUser(userData);
      userStorage.setUser(JSON.stringify(userData));
    } catch (error) {
      // Token is invalid, clear auth
      logout();
      throw error;
    }
  };

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated: !!user && !!token,
    isLoading,
    login,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
