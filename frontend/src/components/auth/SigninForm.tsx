'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { validateEmail } from '@/lib/validators';
import { signin } from '@/lib/auth';
import { APIError } from '@/lib/api';

export function SigninForm() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [emailError, setEmailError] = useState('');
  const [formError, setFormError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Reset errors
    setEmailError('');
    setFormError('');

    // Validate email
    const emailValidation = validateEmail(email);
    if (!emailValidation.isValid) {
      setEmailError(emailValidation.error || '');
      return;
    }

    // Basic password check (not empty)
    if (!password) {
      setFormError('Password is required');
      return;
    }

    // Submit signin
    setIsLoading(true);

    try {
      await signin(email, password);
      // Redirect to todos page on success
      router.push('/todos');
    } catch (error) {
      if (error instanceof APIError) {
        if (error.status === 401) {
          setFormError('Invalid email or password');
        } else {
          setFormError(error.message);
        }
      } else {
        setFormError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 w-full max-w-md">
      <div>
        <Input
          type="email"
          label="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          error={emailError}
          placeholder="user@example.com"
          required
          disabled={isLoading}
        />
      </div>

      <div>
        <Input
          type="password"
          label="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Enter your password"
          required
          disabled={isLoading}
        />
      </div>

      {formError && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-600">{formError}</p>
        </div>
      )}

      <Button type="submit" variant="primary" className="w-full" isLoading={isLoading}>
        Sign In
      </Button>

      <div className="text-center">
        <p className="text-sm text-gray-600">
          Don&apos;t have an account?{' '}
          <a href="/signup" className="text-primary-600 hover:text-primary-700 font-medium">
            Sign Up
          </a>
        </p>
      </div>
    </form>
  );
}
