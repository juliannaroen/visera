"use client";

import { useState, useRef } from "react";
import Link from "next/link";
import { apiRequest } from "@/lib/api/client";
import type { User } from "@/lib/types/auth";

export default function SignupPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [emailSent, setEmailSent] = useState(false);
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const formRef = useRef<HTMLFormElement>(null);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    const formData = new FormData(e.currentTarget);
    const email = formData.get("email") as string;
    const password = formData.get("password") as string;

    try {
      // Create the user account (this will automatically send verification email)
      await apiRequest<User>("/api/v1/users", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });

      setEmailSent(true);
      setUserEmail(email);

      // Reset form
      if (formRef.current) {
        formRef.current.reset();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
      setIsLoading(false);
    }
  };

  if (emailSent) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-pink-200 via-rose-200 to-orange-200 font-sans">
        <main className="w-full max-w-md px-6">
          <div className="rounded-2xl bg-white p-8 shadow-lg">
            <div className="mb-4 flex justify-center">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-rose-100">
                <svg
                  className="h-8 w-8 text-rose-500"
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
              Check Your Email
            </h1>
            <p className="mb-6 text-center text-sm text-gray-600">
              We&apos;ve sent a verification email to{" "}
              <span className="font-semibold text-gray-900">{userEmail}</span>
            </p>
            <div className="mb-6 rounded-lg bg-blue-50 border border-blue-200 p-4">
              <p className="text-sm text-blue-800">
                Please click the verification link in the email to activate your
                account. The link will expire in 24 hours.
              </p>
            </div>
            <div className="space-y-3">
              <p className="text-center text-sm text-gray-600">
                Didn&apos;t receive the email? Check your spam folder or{" "}
                <button
                  onClick={() => setEmailSent(false)}
                  className="font-medium text-rose-500 hover:text-rose-600"
                >
                  try again
                </button>
              </p>
              <Link
                href="/login"
                className="block w-full rounded-lg bg-rose-500 px-4 py-3 text-center font-semibold text-white transition-colors duration-300 ease-in-out hover:bg-rose-600"
              >
                Back to Login
              </Link>
            </div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-pink-200 via-rose-200 to-orange-200 font-sans">
      <main className="w-full max-w-md px-6">
        <div className="rounded-2xl bg-white p-8 shadow-lg">
          <h1 className="mb-2 text-3xl font-bold text-gray-900">Sign Up</h1>
          <p className="mb-8 text-sm text-gray-600">
            Create a new account to get started.
          </p>
          <form
            ref={formRef}
            onSubmit={handleSubmit}
            className="space-y-6"
            suppressHydrationWarning
          >
            {error && (
              <div className="rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-800">
                {error}
              </div>
            )}
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
                disabled={isLoading}
                suppressHydrationWarning
                className="w-full rounded-lg border border-gray-300 px-4 py-3 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-rose-400 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
                placeholder="you@example.com"
              />
            </div>
            <div>
              <label
                htmlFor="password"
                className="mb-2 block text-sm font-medium text-gray-700"
              >
                Password
              </label>
              <input
                type="password"
                id="password"
                name="password"
                required
                minLength={8}
                disabled={isLoading}
                suppressHydrationWarning
                className="w-full rounded-lg border border-gray-300 px-4 py-3 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-rose-400 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
                placeholder="•••••••• (min 8 characters)"
              />
              <p className="mt-1 text-xs text-gray-500">
                Password must be at least 8 characters
              </p>
            </div>
            <button
              type="submit"
              disabled={isLoading}
              className="w-full rounded-lg bg-rose-500 px-4 py-3 font-semibold text-white transition-colors duration-300 ease-in-out hover:bg-rose-600 focus:outline-none focus:ring-2 focus:ring-rose-400 focus:ring-offset-2 disabled:bg-rose-300 disabled:cursor-not-allowed"
            >
              {isLoading ? "Creating Account..." : "Sign Up"}
            </button>
          </form>
          <p className="mt-6 text-center text-sm text-gray-600">
            Already have an account?{" "}
            <Link
              href="/login"
              className="font-medium text-rose-500 hover:text-rose-600"
            >
              Sign in
            </Link>
          </p>
        </div>
      </main>
    </div>
  );
}
