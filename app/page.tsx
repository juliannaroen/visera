"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth/hooks";

export default function Home() {
  const { isAuthenticated } = useAuth();
  const router = useRouter();

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      router.push("/dashboard");
    }
  }, [isAuthenticated, router]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-pink-200 via-rose-200 to-orange-200 font-sans">
      <main className="w-full max-w-4xl px-6 py-12">
        <div className="text-center mb-12">
          <h1 className="mb-4 text-5xl font-bold text-gray-900">
            Welcome to Visera
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Your platform for managing and organizing your digital life.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 max-w-2xl mx-auto">
          <Link
            href="/signup"
            className="group rounded-2xl bg-white p-8 shadow-lg transition-all duration-300 hover:shadow-xl hover:scale-105"
          >
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-rose-100 group-hover:bg-rose-200 transition-colors">
              <svg
                className="h-6 w-6 text-rose-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"
                />
              </svg>
            </div>
            <h2 className="mb-2 text-2xl font-bold text-gray-900">
              Get Started
            </h2>
            <p className="text-gray-600">
              Create a new account and start your journey with us today.
            </p>
          </Link>

          <Link
            href="/login"
            className="group rounded-2xl bg-white p-8 shadow-lg transition-all duration-300 hover:shadow-xl hover:scale-105"
          >
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-rose-100 group-hover:bg-rose-200 transition-colors">
              <svg
                className="h-6 w-6 text-rose-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"
                />
              </svg>
            </div>
            <h2 className="mb-2 text-2xl font-bold text-gray-900">Sign In</h2>
            <p className="text-gray-600">
              Already have an account? Sign in to continue where you left off.
            </p>
          </Link>
        </div>

        <div className="mt-12 text-center">
          <p className="text-sm text-gray-500">
            By continuing, you agree to our Terms of Service and Privacy Policy
          </p>
        </div>
      </main>
    </div>
  );
}
