# Frontend Directory Structure

This document explains the organization of the frontend codebase using Next.js App Router.

## Overview

The frontend uses a feature-based structure with Next.js route groups to organize routes logically without affecting URL paths. This structure promotes maintainability and scalability as the application grows.

## Directory Structure

```
app/
├── (auth)/                    # Route group for authentication pages
│   └── login/
│       └── page.tsx          # Login page → /login
├── (dashboard)/               # Route group for protected pages
│   ├── layout.tsx            # Protected layout (requires auth)
│   └── dashboard/
│       └── page.tsx          # Dashboard page → /dashboard
├── lib/                       # Shared utilities and business logic
│   ├── api/                  # API client functions
│   │   ├── auth.ts          # Authentication API calls
│   │   └── client.ts        # Base API client with token handling
│   ├── auth/                 # Authentication utilities
│   │   ├── context.tsx      # Auth context provider
│   │   ├── hooks.ts         # Auth hooks (useAuth)
│   │   └── storage.ts       # Token and user storage utilities
│   └── types/                # TypeScript type definitions
│       └── auth.ts          # Authentication-related types
├── globals.css               # Global styles
├── layout.tsx                # Root layout (includes AuthProvider)
└── page.tsx                  # Home/landing page → /
```

## Route Groups

Route groups are folders wrapped in parentheses like `(auth)` and `(dashboard)`. They are a Next.js App Router feature that allows you to:

- **Organize routes** without affecting the URL structure
- **Apply shared layouts** to groups of routes
- **Keep URLs clean** - `(auth)/login/page.tsx` creates `/login`, not `/auth/login`

### Example

- `app/(auth)/login/page.tsx` → URL: `/login`
- `app/(dashboard)/dashboard/page.tsx` → URL: `/dashboard`

Without route groups, you would need:

- `app/auth/login/page.tsx` → URL: `/auth/login` (longer URL)
- `app/dashboard/page.tsx` → URL: `/dashboard` (no grouping)

## Key Directories

### `app/`

Contains all Next.js pages and layouts. The App Router uses the file system for routing:

- `page.tsx` - Creates a route
- `layout.tsx` - Creates a shared layout for nested routes
- Route groups `(name)` - Organize routes without affecting URLs

### `lib/`

Contains shared utilities, API clients, and business logic:

- **`api/`** - API client functions that handle HTTP requests to the backend

  - `client.ts` - Base API client with automatic token injection
  - `auth.ts` - Authentication-specific API calls

- **`auth/`** - Authentication system

  - `context.tsx` - React context provider for global auth state
  - `hooks.ts` - Custom hooks (e.g., `useAuth()`)
  - `storage.ts` - localStorage utilities for tokens and user data

- **`types/`** - TypeScript type definitions shared across the app

## Authentication Flow

1. **Login** (`/login`) - User enters credentials
2. **API Call** - `authApi.login()` sends credentials to backend
3. **Token Storage** - JWT token stored in localStorage
4. **Context Update** - Auth context updates with user and token
5. **Redirect** - User redirected to `/dashboard`
6. **Protected Routes** - Dashboard layout checks authentication
7. **API Requests** - All API calls automatically include Bearer token

## Protected Routes

The `(dashboard)/layout.tsx` file protects all routes under the dashboard group:

- Checks if user is authenticated
- Redirects to `/login` if not authenticated
- Shows loading state while checking authentication
- Only renders children if authenticated

## Adding New Features

### Adding a New Protected Page

1. Create a new folder under `app/(dashboard)/`
2. Add a `page.tsx` file
3. The route is automatically protected by the dashboard layout

Example:

```
app/(dashboard)/settings/page.tsx → /settings (protected)
```

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
  getProfile: async () => {
    return apiRequest<User>("/api/v1/users/profile");
  },
};
```

## TypeScript Path Aliases

The project uses path aliases configured in `tsconfig.json`:

- `@/lib/*` → `app/lib/*` (e.g., `@/lib/auth/hooks` → `app/lib/auth/hooks`)
- `@/*` → root directory (e.g., `@/app/page` → `app/page`)

This allows you to import from `@/lib/...` even though the folder is at `app/lib/...`.

## Best Practices

1. **Keep route groups focused** - Each group should represent a logical feature area
2. **Use layouts for shared UI** - Don't repeat header/footer code
3. **Centralize API calls** - Keep all API logic in `app/lib/api/`
4. **Type everything** - Use TypeScript types from `app/lib/types/`
5. **Reuse auth context** - Use `useAuth()` hook instead of managing auth state manually
6. **Keep frontend code in `app/`** - All frontend-related code (routes, utilities, components) lives under `app/` for better organization
