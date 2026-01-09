/**
 * TodoItem component for displaying individual todo.
 */

import { useState } from 'react';
import { Todo } from '@/types/todo';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { validateTodoTitle } from '@/lib/validators';

interface TodoItemProps {
  todo: Todo;
  onToggle?: (id: string) => void;
  onDelete?: (id: string) => void;
  onUpdate?: (id: string, title: string) => Promise<void>;
}

export function TodoItem({ todo, onToggle, onDelete, onUpdate }: TodoItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(todo.title);
  const [titleError, setTitleError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleStartEdit = () => {
    setIsEditing(true);
    setEditTitle(todo.title);
    setTitleError('');
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditTitle(todo.title);
    setTitleError('');
  };

  const handleSaveEdit = async () => {
    // Validate title
    const validation = validateTodoTitle(editTitle);
    if (!validation.isValid) {
      setTitleError(validation.error || 'Invalid title');
      return;
    }

    if (editTitle === todo.title) {
      // No changes, just exit edit mode
      setIsEditing(false);
      return;
    }

    try {
      setIsLoading(true);
      setTitleError('');
      await onUpdate?.(todo.id, editTitle);
      setIsEditing(false);
    } catch (error) {
      if (error instanceof Error) {
        setTitleError(error.message);
      } else {
        setTitleError('Failed to update todo');
      }
    } finally {
      setIsLoading(false);
    }
  };

  if (isEditing) {
    return (
      <div className="p-4 bg-white border border-gray-200 rounded-lg">
        <div className="space-y-2">
          <Input
            type="text"
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            error={titleError}
            disabled={isLoading}
            autoFocus
          />
          <div className="flex gap-2">
            <Button
              size="sm"
              onClick={handleSaveEdit}
              isLoading={isLoading}
              disabled={isLoading}
            >
              Save
            </Button>
            <Button
              size="sm"
              variant="secondary"
              onClick={handleCancelEdit}
              disabled={isLoading}
            >
              Cancel
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-between p-4 bg-white border border-gray-200 rounded-lg hover:shadow-sm transition-shadow">
      <div className="flex items-center flex-1 min-w-0">
        <input
          type="checkbox"
          checked={todo.is_complete}
          onChange={() => onToggle?.(todo.id)}
          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded cursor-pointer"
        />
        <span
          className={`ml-3 text-sm ${
            todo.is_complete
              ? 'line-through text-gray-500'
              : 'text-gray-900'
          } truncate`}
        >
          {todo.title}
        </span>
      </div>
      <div className="flex items-center gap-2 ml-4">
        {onUpdate && (
          <button
            onClick={handleStartEdit}
            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
            aria-label="Edit todo"
          >
            Edit
          </button>
        )}
        {onDelete && (
          <button
            onClick={() => onDelete(todo.id)}
            className="text-sm text-red-600 hover:text-red-800 font-medium"
            aria-label="Delete todo"
          >
            Delete
          </button>
        )}
      </div>
    </div>
  );
}
