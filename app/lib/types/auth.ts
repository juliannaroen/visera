export interface User {
  id: number;
  email: string;
  created_at: string;
  is_email_verified: boolean;
}

export type UserResponse = User;

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
