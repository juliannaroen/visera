"use client";

import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
} from "react";
import { useRouter } from "next/navigation";
import { authApi } from "../api/auth";
import { tokenStorage, userStorage, clearAuthStorage } from "./storage";
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
  // Initialize state from storage using lazy initialization
  const [user, setUser] = useState<User | null>(() => {
    try {
      const storedUser = userStorage.getUser();
      return storedUser ? JSON.parse(storedUser) : null;
    } catch {
      return null;
    }
  });
  const [token, setToken] = useState<string | null>(() => {
    return tokenStorage.getToken();
  });
  // Initialize loading to false since we're using lazy initialization
  // If we have a token but no user, we'll fetch the user in useEffect
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
    clearAuthStorage();
    router.push("/login");
  }, [router]);

  const refreshUser = useCallback(async () => {
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
  }, [token, logout]);

  const login = async (credentials: LoginRequest): Promise<LoginResponse> => {
    try {
      const response = await authApi.login(credentials);
      setToken(response.access_token);
      setUser(response.user);
      tokenStorage.setToken(response.access_token);
      userStorage.setUser(JSON.stringify(response.user));
      return response;
    } catch (error) {
      throw error;
    }
  };

  // Verify token and fetch user on mount if token exists
  useEffect(() => {
    if (token && !user) {
      // Use a separate async function to avoid calling setState directly in effect
      const fetchUser = async () => {
        setIsLoading(true);
        try {
          await refreshUser();
        } catch {
          // Token is invalid, clear auth
          logout();
        } finally {
          setIsLoading(false);
        }
      };
      fetchUser();
    }
  }, [token, user, refreshUser, logout]);

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
