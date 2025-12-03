"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth/hooks";

export function Sidebar() {
  const pathname = usePathname();
  const { logout } = useAuth();

  const navItems = [
    { href: "/home", label: "Home", icon: "🏠" },
    { href: "/settings", label: "Settings", icon: "⚙️" },
  ];

  return (
    <aside className="w-64 bg-white shadow-lg min-h-screen">
      <div className="p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-8">Visera</h2>

        <nav className="space-y-2">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive
                    ? "bg-rose-100 text-rose-700 font-semibold"
                    : "text-gray-700 hover:bg-gray-100"
                }`}
              >
                <span className="text-xl">{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="mt-8 pt-8 border-t border-gray-200">
          <button
            onClick={logout}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
          >
            Sign Out
          </button>
        </div>
      </div>
    </aside>
  );
}
