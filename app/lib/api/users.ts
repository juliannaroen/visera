import { apiRequest } from "./client";

export const usersApi = {
  deleteAccount: async (): Promise<void> => {
    return apiRequest<void>("/api/v1/users/me", {
      method: "DELETE",
    });
  },
};
