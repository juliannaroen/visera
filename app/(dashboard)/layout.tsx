"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth/hooks";
import { Sidebar } from "./common/Sidebar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { refreshUser } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        await refreshUser();
      } catch {
        router.push(`/login?redirect=${encodeURIComponent(pathname)}`);
      } finally {
        setIsLoading(false);
      }
    };
    checkAuth();
  }, [refreshUser, router, pathname]);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-pink-200 via-rose-200 to-orange-200">
        <div className="rounded-2xl bg-white p-8 shadow-lg">
          <div className="text-center">
            <div className="mb-2 text-lg font-semibold text-gray-900">
              Loading...
            </div>
            <div className="text-sm text-gray-600">Please wait</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-gradient-to-br from-pink-200 via-rose-200 to-orange-200">
      <Sidebar />
      <main className="flex-1 overflow-auto">
        <div className="container mx-auto px-6 py-8">{children}</div>
      </main>
    </div>
  );
}
