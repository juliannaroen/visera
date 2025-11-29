"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { authApi } from "@/lib/api/auth";
import { useAuth } from "@/lib/auth/hooks";

export default function SendVerificationEmailPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [email, setEmail] = useState("");
  const { user, isAuthenticated } = useAuth();
  const router = useRouter();

  // Only redirect if authenticated and verified
  useEffect(() => {
    if (isAuthenticated && user?.is_email_verified) {
      router.push("/dashboard");
    }
  }, [isAuthenticated, user, router]);

  // Pre-fill email if user is logged in
  useEffect(() => {
    if (isAuthenticated && user?.email && !email) {
      setEmail(user.email);
    }
  }, [isAuthenticated, user, email]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setSuccess(false);

    try {
      // Send verification email (with email parameter if not authenticated)
      await authApi.sendVerificationEmail(
        isAuthenticated && user ? undefined : email
      );
      setSuccess(true);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to send verification email"
      );
    } finally {
      setIsLoading(false);
    }
  };

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
                  d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                />
              </svg>
            </div>
          </div>
          <h1 className="mb-2 text-center text-3xl font-bold text-gray-900">
            Verify Your Email
          </h1>
          <p className="mb-6 text-center text-sm text-gray-600">
            {isAuthenticated && user
              ? "Please verify your email address to access the dashboard."
              : "Enter your email address to receive a verification email."}
          </p>

          {isAuthenticated && user && (
            <div className="mb-6 rounded-lg bg-blue-50 border border-blue-200 p-4">
              <p className="text-sm text-blue-800">
                We sent a verification email to{" "}
                <span className="font-semibold">{user.email}</span>
              </p>
            </div>
          )}

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

          <form onSubmit={handleSubmit} className="space-y-3">
            {!isAuthenticated && (
              <div>
                <label
                  htmlFor="email"
                  className="mb-2 block text-sm font-medium text-gray-700"
                >
                  Email
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={isLoading}
                  className="w-full rounded-lg border border-gray-300 px-4 py-3 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-rose-400 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
                  placeholder="you@example.com"
                />
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full rounded-lg bg-rose-500 px-4 py-3 font-semibold text-white transition-colors duration-300 ease-in-out hover:bg-rose-600 focus:outline-none focus:ring-2 focus:ring-rose-400 focus:ring-offset-2 disabled:bg-rose-300 disabled:cursor-not-allowed"
            >
              {isLoading
                ? "Sending..."
                : success
                ? "Email Sent! Click to Send Again"
                : "Send Verification Email"}
            </button>

            <Link
              href="/login"
              className="block w-full text-center text-sm font-medium text-gray-600 hover:text-gray-900"
            >
              Back to Login
            </Link>
          </form>
        </div>
      </main>
    </div>
  );
}
