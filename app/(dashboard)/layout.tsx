/**
 * Dashboard Layout
 *
 * Route protection is handled entirely by the backend.
 * When pages load and make API calls, the backend validates authentication.
 * If unauthenticated, backend returns 401/403, and API client handles redirects.
 * This ensures backend is the single source of truth for all auth logic.
 */
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // No client-side auth checks needed:
  // - Backend validates token on every API call (single source of truth)
  // - API client handles 401/403 responses and redirects automatically
  // - Pages can load normally; auth is enforced when they make API calls
  return <>{children}</>;
}
