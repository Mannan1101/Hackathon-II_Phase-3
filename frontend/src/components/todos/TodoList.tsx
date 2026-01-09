/**
 * TodoList component for displaying a list of todos.
 */

import { Todo } from '@/types/todo';
import { TodoItem } from './TodoItem';
import { EmptyState } from './EmptyState';

interface TodoListProps {
  todos: Todo[];
  isLoading?: boolean;
  onToggle?: (id: string) => void;
  onDelete?: (id: string) => void;
  onUpdate?: (id: string, title: string) => Promise<void>;
}

export function TodoList({
  todos,
  isLoading,
  onToggle,
  onDelete,
  onUpdate,
}: TodoListProps) {
  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (todos.length === 0) {
    return <EmptyState />;
  }

  return (
    <div className="space-y-2">
      {todos.map((todo) => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onToggle={onToggle}
          onDelete={onDelete}
          onUpdate={onUpdate}
        />
      ))}
    </div>
  );
}
