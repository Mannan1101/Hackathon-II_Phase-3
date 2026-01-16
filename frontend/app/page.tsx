'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';

/**
 * Landing page with redirect logic.
 *
 * Redirects authenticated users to /todos, unauthenticated users to /signin.
 * For now, we redirect everyone to /signin until authentication is implemented.
 */
export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    // TODO: Check authentication status
    // For now, redirect to signin
    router.push('/signin');
  }, [router]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <LoadingSpinner size="lg" />
    </div>
  );
}
