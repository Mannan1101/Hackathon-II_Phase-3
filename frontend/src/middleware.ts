import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

/**
 * Next.js middleware for authentication-based redirects.
 *
 * Protected routes require authentication (session cookie).
 * Auth routes (signin, signup) redirect authenticated users to /todos.
 */
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const sessionCookie = request.cookies.get('session_id');
  const isAuthenticated = !!sessionCookie;

  // Protected routes that require authentication
  const isProtectedRoute = pathname.startsWith('/todos');

  // Auth routes (signin, signup)
  const isAuthRoute = pathname === '/signin' || pathname === '/signup';

  // Redirect unauthenticated users to signin
  if (isProtectedRoute && !isAuthenticated) {
    const signinUrl = new URL('/signin', request.url);
    return NextResponse.redirect(signinUrl);
  }

  // Redirect authenticated users from auth pages to todos
  if (isAuthRoute && isAuthenticated) {
    const todosUrl = new URL('/todos', request.url);
    return NextResponse.redirect(todosUrl);
  }

  return NextResponse.next();
}

/**
 * Configure which routes this middleware should run on.
 */
export const config = {
  matcher: [
    /*
     * Match all request paths except for:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
