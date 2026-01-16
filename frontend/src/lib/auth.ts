/**
 * Authentication state management and API calls.
 *
 * This module provides functions for signup, signin, and auth state management.
 */

import { api } from './api';
import { User, SignupRequest, SigninRequest, AuthResponse } from '@/types/user';

/**
 * Sign up a new user.
 *
 * @param email - User email
 * @param password - User password
 * @returns Promise with user data
 */
export async function signup(email: string, password: string): Promise<AuthResponse> {
  const request: SignupRequest = { email, password };
  return await api.post<AuthResponse>('/auth/signup', request);
}

/**
 * Sign in existing user.
 *
 * @param email - User email
 * @param password - User password
 * @returns Promise with user data
 */
export async function signin(email: string, password: string): Promise<AuthResponse> {
  const request: SigninRequest = { email, password };
  return await api.post<AuthResponse>('/auth/signin', request);
}

/**
 * Get current authenticated user.
 *
 * This function checks if the user is authenticated by attempting
 * to fetch a protected resource. For now, we'll implement this
 * when we have protected endpoints.
 *
 * @returns Promise with user data or null if not authenticated
 */
export async function getCurrentUser(): Promise<User | null> {
  try {
    // TODO: Implement when we have a /auth/me endpoint
    // For now, return null
    return null;
  } catch (error) {
    return null;
  }
}

/**
 * Sign out current user.
 *
 * Clears the session cookie by making a request to the backend.
 */
export async function signout(): Promise<void> {
  try {
    await api.post<{ message: string }>('/auth/signout', {});
  } catch (error) {
    // Even if the request fails, we should still clear the cookie client-side
    console.error('Signout error:', error);
  }
}
