const TOKEN_KEY = "visera_auth_token";
const USER_KEY = "visera_user";

export const tokenStorage = {
  getToken: (): string | null => {
    if (typeof window === "undefined") return null;
    return localStorage.getItem(TOKEN_KEY);
  },

  setToken: (token: string): void => {
    if (typeof window === "undefined") return;
    localStorage.setItem(TOKEN_KEY, token);
  },

  removeToken: (): void => {
    if (typeof window === "undefined") return;
    localStorage.removeItem(TOKEN_KEY);
  },
};

export const userStorage = {
  getUser: (): string | null => {
    if (typeof window === "undefined") return null;
    return localStorage.getItem(USER_KEY);
  },

  setUser: (user: string): void => {
    if (typeof window === "undefined") return;
    localStorage.setItem(USER_KEY, user);
  },

  removeUser: (): void => {
    if (typeof window === "undefined") return;
    localStorage.removeItem(USER_KEY);
  },
};

export const clearAuthStorage = (): void => {
  tokenStorage.removeToken();
  userStorage.removeUser();
};
