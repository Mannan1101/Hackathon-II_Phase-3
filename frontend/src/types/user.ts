/**
 * User type definitions.
 *
 * This module defines TypeScript types for user-related data.
 */

export interface User {
  id: string;
  email: string;
  created_at: string;
}

export interface SignupRequest {
  email: string;
  password: string;
}

export interface SigninRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  id: string;
  email: string;
  created_at: string;
}
