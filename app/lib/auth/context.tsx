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
import { userStorage, clearAuthStorage } from "./storage";
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
  // No token state needed - authentication handled via httpOnly cookies
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const logout = useCallback(async () => {
    try {
      // Call backend logout endpoint to clear cookie
      await authApi.logout();
    } catch (error) {
      // Even if logout API call fails, clear local state
      console.error("Logout error:", error);
    } finally {
      // Clear local user state
      setUser(null);
      clearAuthStorage();
      router.push("/login");
    }
  }, [router]);

  const refreshUser = useCallback(async () => {
    try {
      // Cookie is automatically sent by browser
      const userData = await authApi.getCurrentUser();
      setUser(userData);
      userStorage.setUser(JSON.stringify(userData));
    } catch (error) {
      // Cookie is invalid/expired, clear auth
      // API client will handle redirect
      setUser(null);
      clearAuthStorage();
      throw error;
    }
  }, []);

  const login = async (credentials: LoginRequest): Promise<LoginResponse> => {
    try {
      // Backend sets httpOnly cookie on successful login
      const response = await authApi.login(credentials);
      // Update local user state (cookie is handled by backend)
      setUser(response.user);
      userStorage.setUser(JSON.stringify(response.user));
      return response;
    } catch (error) {
      throw error;
    }
  };

  // Fetch user on mount if we have stored user data but want to refresh
  // Cookie is automatically sent by browser
  useEffect(() => {
    // If we have stored user data, try to refresh it
    // This validates the cookie is still valid
    const storedUser = userStorage.getUser();
    if (storedUser && !user) {
      const fetchUser = async () => {
        setIsLoading(true);
        try {
          await refreshUser();
        } catch {
          // Cookie is invalid/expired, clear auth
          // API client will handle redirect
          setUser(null);
          clearAuthStorage();
        } finally {
          setIsLoading(false);
        }
      };
      fetchUser();
    }
  }, [user, refreshUser]);

  const value: AuthContextType = {
    user,
    token: null, // Token is in httpOnly cookie, not accessible to JavaScript
    isAuthenticated: !!user, // User presence indicates auth (validated by backend)
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
