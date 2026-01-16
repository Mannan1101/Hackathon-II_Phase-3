import { SignupForm } from '@/components/auth/SignupForm';

export default function SignupPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">
            Create your account
          </h1>
          <p className="mt-2 text-sm text-gray-600">
            Sign up to start managing your todos
          </p>
        </div>
        <div className="mt-8 bg-white py-8 px-6 shadow-md rounded-lg sm:px-10">
          <SignupForm />
        </div>
      </div>
    </div>
  );
}
