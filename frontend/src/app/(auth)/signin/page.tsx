import { SigninForm } from '@/components/auth/SigninForm';

export default function SigninPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">
            Sign in to your account
          </h1>
          <p className="mt-2 text-sm text-gray-600">
            Welcome back! Please sign in to continue
          </p>
        </div>
        <div className="mt-8 bg-white py-8 px-6 shadow-md rounded-lg sm:px-10">
          <SigninForm />
        </div>
      </div>
    </div>
  );
}
