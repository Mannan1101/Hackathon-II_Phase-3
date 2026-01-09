'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { validateEmail, validatePassword } from '@/lib/validators';
import { signup } from '@/lib/auth';
import { APIError } from '@/lib/api';

export function SignupForm() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [formError, setFormError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Reset errors
    setEmailError('');
    setPasswordError('');
    setFormError('');

    // Validate email
    const emailValidation = validateEmail(email);
    if (!emailValidation.isValid) {
      setEmailError(emailValidation.error || '');
      return;
    }

    // Validate password
    const passwordValidation = validatePassword(password);
    if (!passwordValidation.isValid) {
      setPasswordError(passwordValidation.error || '');
      return;
    }

    // Submit signup
    setIsLoading(true);

    try {
      await signup(email, password);
      // Redirect to todos page on success
      router.push('/todos');
    } catch (error) {
      if (error instanceof APIError) {
        if (error.status === 409) {
          setFormError('An account with this email already exists');
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
          error={passwordError}
          helperText="Minimum 8 characters"
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
        Sign Up
      </Button>

      <div className="text-center">
        <p className="text-sm text-gray-600">
          Already have an account?{' '}
          <a href="/signin" className="text-primary-600 hover:text-primary-700 font-medium">
            Sign In
          </a>
        </p>
      </div>
    </form>
  );
}
