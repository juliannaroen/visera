"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { authApi } from "@/lib/api/auth";
import { useAuth } from "@/lib/auth/hooks";

export default function VerifyOtpPage() {
  const [otp, setOtp] = useState(["", "", "", "", "", ""]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [email, setEmail] = useState<string>("");
  const [isResending, setIsResending] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user, refreshUser } = useAuth();
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  useEffect(() => {
    // Get email from query param or from authenticated user
    const emailParam = searchParams.get("email");
    if (emailParam) {
      setEmail(emailParam);
    } else if (user?.email) {
      setEmail(user.email);
    }
  }, [searchParams, user]);

  const handleOtpChange = (index: number, value: string) => {
    // Only allow alphanumeric characters
    const sanitized = value
      .replace(/[^A-Z0-9]/gi, "")
      .toUpperCase()
      .slice(0, 1);

    const newOtp = [...otp];
    newOtp[index] = sanitized;
    setOtp(newOtp);
    setError(null);

    // Auto-focus next input
    if (sanitized && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (
    index: number,
    e: React.KeyboardEvent<HTMLInputElement>
  ) => {
    // Handle backspace
    if (e.key === "Backspace" && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
    // Handle paste
    if (e.key === "v" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      navigator.clipboard.readText().then((text) => {
        const sanitized = text
          .replace(/[^A-Z0-9]/gi, "")
          .toUpperCase()
          .slice(0, 6);
        const newOtp = [...otp];
        for (let i = 0; i < 6; i++) {
          newOtp[i] = sanitized[i] || "";
        }
        setOtp(newOtp);
        if (sanitized.length === 6) {
          inputRefs.current[5]?.focus();
        }
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    const code = otp.join("");
    if (code.length !== 6) {
      setError("Please enter the complete 6-digit code");
      setIsSubmitting(false);
      return;
    }

    if (!email) {
      setError("Email is required");
      setIsSubmitting(false);
      return;
    }

    try {
      // Verify OTP - backend will create session and verify email
      await authApi.verifyOtp(email, code);

      // Refresh user data to get updated verification status
      await refreshUser();

      // Redirect to dashboard
      router.push("/dashboard");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Invalid verification code"
      );
      // Clear OTP inputs on error
      setOtp(["", "", "", "", "", ""]);
      inputRefs.current[0]?.focus();
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleResend = async () => {
    if (!email) {
      setError("Email is required");
      return;
    }

    setIsResending(true);
    setError(null);

    try {
      await authApi.sendVerificationEmail(email);
      // Clear OTP inputs
      setOtp(["", "", "", "", "", ""]);
      inputRefs.current[0]?.focus();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to resend code");
    } finally {
      setIsResending(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-pink-200 via-rose-200 to-orange-200 font-sans">
      <main className="w-full max-w-md px-6">
        <div className="rounded-2xl bg-white p-8 shadow-lg">
          <div className="mb-4 flex justify-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-blue-100">
              <svg
                className="h-8 w-8 text-blue-600"
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
            Enter the 6-digit code sent to{" "}
            <span className="font-semibold">{email || "your email"}</span>
          </p>

          {error && (
            <div className="mb-4 rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-800">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="flex justify-center gap-2">
              {otp.map((digit, index) => (
                <input
                  key={index}
                  ref={(el) => (inputRefs.current[index] = el)}
                  type="text"
                  inputMode="text"
                  maxLength={1}
                  value={digit}
                  onChange={(e) => handleOtpChange(index, e.target.value)}
                  onKeyDown={(e) => handleKeyDown(index, e)}
                  disabled={isSubmitting}
                  className="h-14 w-14 rounded-lg border-2 border-gray-300 text-center text-2xl font-bold text-gray-900 focus:border-rose-500 focus:outline-none focus:ring-2 focus:ring-rose-400 disabled:bg-gray-100 disabled:cursor-not-allowed"
                  style={{ textTransform: "uppercase" }}
                />
              ))}
            </div>

            <button
              type="submit"
              disabled={isSubmitting || otp.join("").length !== 6}
              className="w-full rounded-lg bg-rose-500 px-4 py-3 font-semibold text-white transition-colors duration-300 ease-in-out hover:bg-rose-600 focus:outline-none focus:ring-2 focus:ring-rose-400 focus:ring-offset-2 disabled:bg-rose-300 disabled:cursor-not-allowed"
            >
              {isSubmitting ? "Verifying..." : "Verify Email"}
            </button>

            <div className="text-center">
              <button
                type="button"
                onClick={handleResend}
                disabled={isResending}
                className="text-sm font-medium text-rose-500 hover:text-rose-600 disabled:text-gray-400"
              >
                {isResending ? "Sending..." : "Resend Code"}
              </button>
            </div>

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
