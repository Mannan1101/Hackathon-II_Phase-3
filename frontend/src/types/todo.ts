/**
 * Todo type definitions matching backend API schemas.
 */

export interface Todo {
  id: string;
  user_id: string;
  title: string;
  is_complete: boolean;
  created_at: string;
  updated_at: string;
}

export interface TodoCreate {
  title: string;
}

export interface TodoUpdate {
  title?: string;
  is_complete?: boolean;
}

export interface TodoResponse extends Todo {}

export interface TodoListResponse {
  todos: Todo[];
  total: number;
}
