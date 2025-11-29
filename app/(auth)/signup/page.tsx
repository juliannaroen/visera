"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { apiRequest } from "@/lib/api/client";
import { useAuth } from "@/lib/auth/hooks";
import type { User } from "@/lib/types/auth";

export default function SignupPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const formRef = useRef<HTMLFormElement>(null);
  const router = useRouter();
  const { logout } = useAuth();

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

      // Log out the user since they're not verified
      logout();

      // Redirect to resend verification page
      router.push("/send-verification-email");
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
      setIsLoading(false);
    }
  };

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
