"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth/hooks";
import type { LoginRequest } from "@/lib/types/auth";

export default function LoginPage() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);
  const formRef = useRef<HTMLFormElement>(null);
  const { login, isAuthenticated, user, isLoading, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    setMounted(true);
  }, []);

  // Redirect if already authenticated and verified
  // If authenticated but not verified, log them out so they can log in fresh
  useEffect(() => {
    // Wait for auth to finish loading
    if (isLoading) {
      return;
    }

    if (isAuthenticated) {
      // Check if email is verified
      if (user && user.is_email_verified) {
        router.push("/dashboard");
      } else if (user && !user.is_email_verified) {
        // User is authenticated but not verified, log them out so they can log in again
        logout();
      }
    }
  }, [isAuthenticated, user, isLoading, router, logout]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    const formData = new FormData(e.currentTarget);
    const credentials: LoginRequest = {
      email: formData.get("email") as string,
      password: formData.get("password") as string,
    };

    try {
      const response = await login(credentials);

      // Check if email is verified
      if (!response.user.is_email_verified) {
        // Log out the user since they're not verified
        logout();
        // Redirect to resend verification page
        router.push("/send-verification-email");
      } else {
        // Email is verified, proceed to dashboard
        router.push("/dashboard");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!mounted) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-pink-200 via-rose-200 to-orange-200 font-sans">
        <main className="w-full max-w-md px-6">
          <div className="rounded-2xl bg-white p-8 shadow-lg">
            <h1 className="mb-2 text-3xl font-bold text-gray-900">Sign In</h1>
            <p className="mb-8 text-sm text-gray-600">
              Sign in to your account to continue.
            </p>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-pink-200 via-rose-200 to-orange-200 font-sans">
      <main className="w-full max-w-md px-6">
        <div className="rounded-2xl bg-white p-8 shadow-lg">
          <h1 className="mb-2 text-3xl font-bold text-gray-900">Sign In</h1>
          <p className="mb-8 text-sm text-gray-600">
            Sign in to your account to continue.
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
                disabled={isSubmitting}
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
                disabled={isSubmitting}
                suppressHydrationWarning
                className="w-full rounded-lg border border-gray-300 px-4 py-3 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-rose-400 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
                placeholder="••••••••"
              />
            </div>
            <button
              type="submit"
              disabled={isLoading}
              className="w-full rounded-lg bg-rose-500 px-4 py-3 font-semibold text-white transition-colors duration-300 ease-in-out hover:bg-rose-600 focus:outline-none focus:ring-2 focus:ring-rose-400 focus:ring-offset-2 disabled:bg-rose-300 disabled:cursor-not-allowed"
            >
              {isSubmitting ? "Signing In..." : "Sign In"}
            </button>
          </form>
          <p className="mt-6 text-center text-sm text-gray-600">
            Don&apos;t have an account?{" "}
            <Link
              href="/signup"
              className="font-medium text-rose-500 hover:text-rose-600"
            >
              Sign up
            </Link>
          </p>
        </div>
      </main>
    </div>
  );
}
