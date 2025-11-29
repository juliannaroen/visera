"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { authApi } from "@/lib/api/auth";

export default function VerifyEmailPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();
  const hasVerified = useRef(false);

  useEffect(() => {
    // Prevent multiple verification attempts
    if (hasVerified.current) {
      return;
    }

    const token = searchParams.get("token");

    if (!token) {
      setError("Verification token is missing");
      setIsLoading(false);
      return;
    }

    hasVerified.current = true;

    const verifyEmail = async () => {
      try {
        await authApi.verifyEmail(token);
        setSuccess(true);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to verify email");
        // Redirect to resend verification page on error
        setTimeout(() => {
          router.push("/send-verification-email");
        }, 3000);
      } finally {
        setIsLoading(false);
      }
    };

    verifyEmail();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-pink-200 via-rose-200 to-orange-200 font-sans">
        <main className="w-full max-w-md px-6">
          <div className="rounded-2xl bg-white p-8 shadow-lg">
            <div className="mb-4 flex justify-center">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-rose-500 border-t-transparent"></div>
            </div>
            <h1 className="mb-2 text-center text-3xl font-bold text-gray-900">
              Verifying Email...
            </h1>
            <p className="text-center text-sm text-gray-600">
              Please wait while we verify your email address.
            </p>
          </div>
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-pink-200 via-rose-200 to-orange-200 font-sans">
        <main className="w-full max-w-md px-6">
          <div className="rounded-2xl bg-white p-8 shadow-lg">
            <div className="mb-4 flex justify-center">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-red-100">
                <svg
                  className="h-6 w-6 text-red-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </div>
            </div>
            <h1 className="mb-2 text-center text-3xl font-bold text-gray-900">
              Verification Failed
            </h1>
            <p className="mb-6 text-center text-sm text-gray-600">{error}</p>
            <p className="mb-6 text-center text-sm text-gray-500">
              Redirecting to verification page...
            </p>
            <Link
              href="/send-verification-email"
              className="block w-full rounded-lg bg-rose-500 px-4 py-3 text-center font-semibold text-white transition-colors duration-300 ease-in-out hover:bg-rose-600"
            >
              Go to Verification Page
            </Link>
          </div>
        </main>
      </div>
    );
  }

  if (success) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-pink-200 via-rose-200 to-orange-200 font-sans">
        <main className="w-full max-w-md px-6">
          <div className="rounded-2xl bg-white p-8 shadow-lg">
            <div className="mb-4 flex justify-center">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-green-100">
                <svg
                  className="h-6 w-6 text-green-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
            </div>
            <h1 className="mb-2 text-center text-3xl font-bold text-gray-900">
              Email Verified!
            </h1>
            <p className="mb-6 text-center text-sm text-gray-600">
              Your email address has been successfully verified. Please log in
              to continue.
            </p>
            <Link
              href="/login"
              className="block w-full rounded-lg bg-rose-500 px-4 py-3 text-center font-semibold text-white transition-colors duration-300 ease-in-out hover:bg-rose-600"
            >
              Go to Login
            </Link>
          </div>
        </main>
      </div>
    );
  }

  return null;
}
