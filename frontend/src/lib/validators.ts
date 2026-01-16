/**
 * Frontend validation utilities.
 *
 * This module provides client-side validation functions matching
 * backend validation rules.
 */

export interface ValidationResult {
  isValid: boolean;
  error?: string;
}

/**
 * Validate email format.
 *
 * @param email - Email address to validate
 * @returns Validation result with error message if invalid
 *
 * @example
 * ```typescript
 * const result = validateEmail("user@example.com");
 * if (!result.isValid) {
 *   console.error(result.error);
 * }
 * ```
 */
export function validateEmail(email: string): ValidationResult {
  if (!email || !email.trim()) {
    return { isValid: false, error: 'Email is required' };
  }

  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  if (!emailRegex.test(email)) {
    return { isValid: false, error: 'Invalid email format' };
  }

  if (email.length > 255) {
    return { isValid: false, error: 'Email must be at most 255 characters' };
  }

  return { isValid: true };
}

/**
 * Validate password strength.
 *
 * Requirements:
 * - Minimum 8 characters
 * - Maximum 100 characters
 *
 * @param password - Password to validate
 * @returns Validation result with error message if invalid
 *
 * @example
 * ```typescript
 * const result = validatePassword("SecurePass123");
 * ```
 */
export function validatePassword(password: string): ValidationResult {
  if (!password) {
    return { isValid: false, error: 'Password is required' };
  }

  if (password.length < 8) {
    return { isValid: false, error: 'Password must be at least 8 characters' };
  }

  if (password.length > 100) {
    return { isValid: false, error: 'Password must be at most 100 characters' };
  }

  return { isValid: true };
}

/**
 * Validate todo title.
 *
 * Requirements:
 * - Not empty or whitespace only
 * - Maximum 200 characters
 *
 * @param title - Todo title to validate
 * @returns Validation result with error message if invalid
 *
 * @example
 * ```typescript
 * const result = validateTodoTitle("Buy groceries");
 * ```
 */
export function validateTodoTitle(title: string): ValidationResult {
  if (!title || !title.trim()) {
    return { isValid: false, error: 'Title is required' };
  }

  if (title.length > 200) {
    return { isValid: false, error: 'Title must be at most 200 characters' };
  }

  return { isValid: true };
}
