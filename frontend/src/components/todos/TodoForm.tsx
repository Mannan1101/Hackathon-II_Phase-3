/**
 * TodoForm component for creating and editing todos.
 */

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { validateTodoTitle } from '@/lib/validators';

interface TodoFormProps {
  initialValue?: string;
  onSubmit: (title: string) => Promise<void>;
  onCancel?: () => void;
  submitLabel?: string;
  isEditing?: boolean;
}

export function TodoForm({
  initialValue = '',
  onSubmit,
  onCancel,
  submitLabel = 'Add Todo',
  isEditing = false,
}: TodoFormProps) {
  const [title, setTitle] = useState(initialValue);
  const [titleError, setTitleError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setTitleError('');

    // Validate title
    const validation = validateTodoTitle(title);
    if (!validation.isValid) {
      setTitleError(validation.error || 'Invalid title');
      return;
    }

    try {
      setIsLoading(true);
      await onSubmit(title);
      // Clear form after successful creation (not for editing)
      if (!isEditing) {
        setTitle('');
      }
    } catch (error) {
      if (error instanceof Error) {
        setTitleError(error.message);
      } else {
        setTitleError('Failed to save todo. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        type="text"
        label={isEditing ? 'Edit Todo' : 'New Todo'}
        placeholder="Enter todo title..."
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        error={titleError}
        disabled={isLoading}
        autoFocus
      />

      <div className="flex gap-2">
        <Button type="submit" isLoading={isLoading} className="flex-1">
          {submitLabel}
        </Button>
        {onCancel && (
          <Button
            type="button"
            variant="secondary"
            onClick={onCancel}
            disabled={isLoading}
          >
            Cancel
          </Button>
        )}
      </div>
    </form>
  );
}
