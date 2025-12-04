# Visera Frontend

The frontend uses a feature-based structure with Next.js route groups to organize routes logically without affecting URL paths.

## Directory Structure

```
app/
├── (auth)/                   # Route group for authentication pages
│   ├── login/
│   │   └── page.tsx          # Login page → /login
│   ├── signup/
│   │   └── page.tsx          # Signup page → /signup
│   ├── verify-otp/
│   │   └── page.tsx          # OTP verification page → /verify-otp
├── (dashboard)/              # Route group for protected pages
│   ├── layout.tsx            # Protected layout with sidebar (requires auth)
│   ├── common/
│   │   └── Sidebar.tsx       # Sidebar navigation component
│   ├── home/
│   │   └── page.tsx          # Home page → /home
│   └── settings/
│       └── page.tsx          # Settings page → /settings
├── lib/                      # Shared utilities and business logic
│   ├── api/                  # API client functions
│   │   ├── auth.ts           # Authentication API calls
│   │   ├── users.ts          # User API calls (account deletion)
│   │   └── client.ts         # Base API client with token handling
│   ├── auth/                 # Authentication utilities
│   │   ├── context.tsx       # Auth context provider
│   │   ├── hooks.ts          # Auth hooks (useAuth)
│   │   └── storage.ts        # Token and user storage utilities
│   └── types/                # TypeScript type definitions
│       └── auth.ts           # Authentication-related types
├── globals.css               # Global styles
├── layout.tsx                # Root layout (includes AuthProvider)
└── page.tsx                  # Home/landing page → /
```

## Adding New Features

### Adding a New Protected Page

Pages that require an authenticated user.

1. Create a new folder under `app/(dashboard)/`
2. Add a `page.tsx` file
3. The route is automatically protected by the dashboard layout

Example:

```
app/(dashboard)/settings/page.tsx → /settings (protected)
```

The settings page includes:

- Account information display
- Account deletion with confirmation dialog
- Automatic logout and redirect after deletion

### Adding a New Public Page

1. Create a new folder under `app/` (or a new route group)
2. Add a `page.tsx` file

Example:

```
app/about/page.tsx → /about (public)
```

### Adding a New API Endpoint

1. Add a function to `app/lib/api/` (or create a new file)
2. Use the `apiRequest` helper from `app/lib/api/client.ts`
3. The client automatically includes the auth token if available

Example:

```typescript
// app/lib/api/users.ts
import { apiRequest } from "./client";

export const usersApi = {
  deleteAccount: async (): Promise<void> => {
    return apiRequest<void>("/api/v1/users/me", {
      method: "DELETE",
    });
  },
};
```
