"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth/hooks";
import { apiRequest } from "@/lib/api/client";

export default function SettingsPage() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [isDeleting, setIsDeleting] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDeleteAccount = async () => {
    setIsDeleting(true);
    setError(null);

    try {
      await apiRequest("/api/v1/users/me", {
        method: "DELETE",
      });

      // Account deleted, logout and redirect
      logout();
      router.push("/login?deleted=true");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete account");
      setIsDeleting(false);
    }
  };

  return (
    <div className="max-w-2xl">
      <div className="mb-6 rounded-2xl bg-white p-6 shadow-lg">
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="mt-2 text-gray-600">Manage your account settings</p>
      </div>

      <div className="rounded-2xl bg-white p-6 shadow-lg">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Account Information
        </h2>
        <dl className="space-y-2">
          <div>
            <dt className="text-sm font-medium text-gray-500">Email</dt>
            <dd className="text-gray-900">{user?.email}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">User ID</dt>
            <dd className="text-gray-900">{user?.id}</dd>
          </div>
        </dl>
      </div>

      <div className="mt-6 rounded-2xl bg-white p-6 shadow-lg border-2 border-red-200">
        <h2 className="text-xl font-semibold text-red-900 mb-2">Danger Zone</h2>
        <p className="text-sm text-gray-600 mb-4">
          Once you delete your account, there is no going back. Your account
          will be soft-deleted and data will be retained for legal compliance
          purposes per GDPR requirements.
        </p>

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-800">
            {error}
          </div>
        )}

        {!showConfirm ? (
          <button
            onClick={() => setShowConfirm(true)}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Delete Account
          </button>
        ) : (
          <div className="space-y-4">
            <p className="text-sm font-semibold text-red-900">
              Are you absolutely sure? This action cannot be undone.
            </p>
            <div className="flex gap-3">
              <button
                onClick={handleDeleteAccount}
                disabled={isDeleting}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:bg-red-300 disabled:cursor-not-allowed"
              >
                {isDeleting ? "Deleting..." : "Yes, delete my account"}
              </button>
              <button
                onClick={() => {
                  setShowConfirm(false);
                  setError(null);
                }}
                disabled={isDeleting}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
