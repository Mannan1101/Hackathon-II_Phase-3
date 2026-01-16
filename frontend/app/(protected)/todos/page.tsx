'use client';

import { useState, useEffect } from 'react';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { Button } from '@/components/ui/Button';
import { TodoList } from '@/components/todos/TodoList';
import { TodoForm } from '@/components/todos/TodoForm';
import { ChatWidget } from '@/components/chat/ChatWidget';
import { useRouter } from 'next/navigation';
import { signout } from '@/lib/auth';
import { api, APIError } from '@/lib/api';
import { TodoListResponse, TodoResponse } from '@/types/todo';

export default function TodosPage() {
  const router = useRouter();
  const [todos, setTodos] = useState<TodoListResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [showAddForm, setShowAddForm] = useState(false);

  useEffect(() => {
    fetchTodos();
  }, []);

  const fetchTodos = async () => {
    try {
      setIsLoading(true);
      setError('');
      const response = await api.get<TodoListResponse>('/todos');
      setTodos(response);
    } catch (err) {
      if (err instanceof APIError) {
        if (err.status === 401) {
          // Session expired, redirect to signin
          router.push('/signin');
          return;
        }
        setError(err.message);
      } else {
        setError('Failed to load todos. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateTodo = async (title: string) => {
    try {
      const newTodo = await api.post<TodoResponse>('/todos', { title });

      // Update the todos list with the new todo
      setTodos((prev) => {
        if (!prev) return { todos: [newTodo], total: 1 };
        return {
          todos: [newTodo, ...prev.todos],
          total: prev.total + 1,
        };
      });

      // Hide the form after successful creation
      setShowAddForm(false);
    } catch (err) {
      if (err instanceof APIError) {
        throw new Error(err.message);
      }
      throw new Error('Failed to create todo. Please try again.');
    }
  };

  const handleToggleTodo = async (id: string) => {
    try {
      const updatedTodo = await api.patch<TodoResponse>(`/todos/${id}/toggle`, {});

      // Update the todo in the list
      setTodos((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          todos: prev.todos.map((todo) =>
            todo.id === id ? updatedTodo : todo
          ),
        };
      });
    } catch (err) {
      if (err instanceof APIError) {
        if (err.status === 401) {
          router.push('/signin');
          return;
        }
        setError(err.message);
      } else {
        setError('Failed to update todo. Please try again.');
      }
    }
  };

  const handleUpdateTodo = async (id: string, title: string) => {
    try {
      const updatedTodo = await api.patch<TodoResponse>(`/todos/${id}`, { title });

      // Update the todo in the list
      setTodos((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          todos: prev.todos.map((todo) =>
            todo.id === id ? updatedTodo : todo
          ),
        };
      });
    } catch (err) {
      if (err instanceof APIError) {
        if (err.status === 401) {
          router.push('/signin');
          return;
        }
        throw new Error(err.message);
      }
      throw new Error('Failed to update todo. Please try again.');
    }
  };

  const handleDeleteTodo = async (id: string) => {
    // Confirm deletion
    if (!window.confirm('Are you sure you want to delete this todo?')) {
      return;
    }

    try {
      await api.delete(`/todos/${id}`);

      // Remove the todo from the list
      setTodos((prev) => {
        if (!prev) return prev;
        return {
          todos: prev.todos.filter((todo) => todo.id !== id),
          total: prev.total - 1,
        };
      });
    } catch (err) {
      if (err instanceof APIError) {
        if (err.status === 401) {
          router.push('/signin');
          return;
        }
        setError(err.message);
      } else {
        setError('Failed to delete todo. Please try again.');
      }
    }
  };

  const handleSignout = async () => {
    await signout();
    router.push('/signin');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">My Todos</h1>
          <Button variant="secondary" onClick={handleSignout}>
            Sign Out
          </Button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
            {error}
          </div>
        )}

        {/* Add Todo Form */}
        {showAddForm && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-4">
            <TodoForm
              onSubmit={handleCreateTodo}
              onCancel={() => setShowAddForm(false)}
              submitLabel="Add Todo"
            />
          </div>
        )}

        {/* Add Todo Button */}
        {!showAddForm && (
          <div className="mb-4">
            <Button onClick={() => setShowAddForm(true)} className="w-full">
              + Add Todo
            </Button>
          </div>
        )}

        {/* Todos List */}
        <div className="bg-white rounded-lg shadow-md p-6">
          {isLoading ? (
            <div className="flex justify-center py-8">
              <LoadingSpinner size="lg" />
            </div>
          ) : (
            <TodoList
              todos={todos?.todos || []}
              isLoading={false}
              onToggle={handleToggleTodo}
              onUpdate={handleUpdateTodo}
              onDelete={handleDeleteTodo}
            />
          )}
        </div>

        {!isLoading && todos && (
          <div className="mt-4 text-sm text-gray-500 text-center">
            {todos.total === 0 ? (
              'No todos yet'
            ) : (
              `${todos.total} ${todos.total === 1 ? 'todo' : 'todos'}`
            )}
          </div>
        )}
      </div>

      {/* AI Chatbot Widget */}
      <ChatWidget onTodoChange={fetchTodos} />
    </div>
  );
}
