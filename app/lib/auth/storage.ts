const USER_KEY = "visera_user";

/**
 * User storage for client-side UI state only.
 * Authentication is handled via httpOnly cookies set by the backend.
 */
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
  userStorage.removeUser();
};
