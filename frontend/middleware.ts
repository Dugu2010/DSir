import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Auth is fully client-side on DSir: access/refresh tokens live in localStorage
// (see src/lib/auth.tsx), and the backend returns them in the JSON response body
// rather than setting an httpOnly cookie. That means the server cannot verify a
// session, so redirecting on a missing cookie would lock authenticated users out
// of every protected route (e.g. /dashboard -> /login).
//
// We therefore pass every request through and let the client-side guard in
// AppShell redirect unauthenticated users with a `?redirect=` param preserved.
export function middleware(_request: NextRequest) {
  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico)$).*)'],
};
