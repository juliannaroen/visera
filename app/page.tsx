"use client";

import { useState, useEffect, useRef } from "react";

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [mounted, setMounted] = useState(false);
  const formRef = useRef<HTMLFormElement>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setSuccess(false);

    const formData = new FormData(e.currentTarget);
    const email = formData.get("email") as string;
    const password = formData.get("password") as string;

    try {
      const apiUrl = (
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001"
      ).replace(/\/$/, "");
      const response = await fetch(`${apiUrl}/api/v1/users`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to create account");
      }

      const userData = await response.json();
      setSuccess(true);
      console.log("User created:", userData);

      // Reset form using ref
      if (formRef.current) {
        formRef.current.reset();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  if (!mounted) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-pink-200 via-rose-200 to-orange-200 font-sans">
        <main className="w-full max-w-md px-6">
          <div className="rounded-2xl bg-white p-8 shadow-lg">
            <h1 className="mb-2 text-3xl font-bold text-gray-900">Sign Up</h1>
            <p className="mb-8 text-sm text-gray-600">
              Create a new account to get started.
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
          <h1 className="mb-2 text-3xl font-bold text-gray-900">Sign Up</h1>
          <p className="mb-8 text-sm text-gray-600">
            Create a new account to get started.
          </p>
          <form ref={formRef} onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-800">
                {error}
              </div>
            )}
            {success && (
              <div className="rounded-lg bg-green-50 border border-green-200 p-3 text-sm text-green-800">
                Account created successfully! You can now sign in.
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
            <a
              href="#"
              className="font-medium text-rose-500 hover:text-rose-600"
            >
              Sign in
            </a>
          </p>
        </div>
      </main>
    </div>
  );
}
