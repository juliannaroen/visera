"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { authApi } from "@/lib/api/auth";
import { useAuth } from "@/lib/auth/hooks";

export default function ResendVerificationPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const { user, isAuthenticated, refreshUser, logout } = useAuth();
  const router = useRouter();

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
    } else if (user?.is_email_verified) {
      router.push("/dashboard");
    }
  }, [isAuthenticated, user, router]);

  const handleResend = async () => {
    setIsLoading(true);
    setError(null);
    setSuccess(false);

    try {
      await authApi.sendVerificationEmail();
      setSuccess(true);
      // Refresh user data after a short delay to check if they verified
      setTimeout(async () => {
        await refreshUser();
      }, 2000);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to send verification email"
      );
    } finally {
      setIsLoading(false);
    }
  };

  // Show loading while checking auth state
  if (!isAuthenticated || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-pink-200 via-rose-200 to-orange-200 font-sans">
        <div className="text-center">
          <div className="mb-4 h-8 w-8 animate-spin rounded-full border-4 border-rose-500 border-t-transparent mx-auto"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // If already verified, redirect (handled by useEffect)
  if (user.is_email_verified) {
    return null;
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-pink-200 via-rose-200 to-orange-200 font-sans">
      <main className="w-full max-w-md px-6">
        <div className="rounded-2xl bg-white p-8 shadow-lg">
          <div className="mb-4 flex justify-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-yellow-100">
              <svg
                className="h-8 w-8 text-yellow-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>
          </div>
          <h1 className="mb-2 text-center text-3xl font-bold text-gray-900">
            Verify Your Email
          </h1>
          <p className="mb-6 text-center text-sm text-gray-600">
            Please verify your email address to access the dashboard.
          </p>

          <div className="mb-6 rounded-lg bg-blue-50 border border-blue-200 p-4">
            <p className="text-sm text-blue-800">
              We sent a verification email to{" "}
              <span className="font-semibold">{user.email}</span>
            </p>
          </div>

          {error && (
            <div className="mb-4 rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-800">
              {error}
            </div>
          )}

          {success && (
            <div className="mb-4 rounded-lg bg-green-50 border border-green-200 p-3 text-sm text-green-800">
              Verification email sent! Please check your inbox.
            </div>
          )}

          <div className="space-y-3">
            <button
              onClick={handleResend}
              disabled={isLoading || success}
              className="w-full rounded-lg bg-rose-500 px-4 py-3 font-semibold text-white transition-colors duration-300 ease-in-out hover:bg-rose-600 focus:outline-none focus:ring-2 focus:ring-rose-400 focus:ring-offset-2 disabled:bg-rose-300 disabled:cursor-not-allowed"
            >
              {isLoading
                ? "Sending..."
                : success
                ? "Email Sent!"
                : "Resend Verification Email"}
            </button>

            <button
              onClick={() => {
                logout();
              }}
              className="block w-full text-center text-sm font-medium text-gray-600 hover:text-gray-900"
            >
              Back to Login
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
