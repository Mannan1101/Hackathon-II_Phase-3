# Frontend Integration Guide - Todo AI Chatbot

This guide explains how to integrate the Todo AI Chatbot backend with your Next.js frontend.

## API Endpoint

### POST /api/chat

Process natural language chat messages for todo management.

**Authentication**: Required (session cookie)

**Rate Limiting**: 30 requests per 60 seconds per user

**Request**

```typescript
interface ChatRequest {
  text: string; // 1-1000 characters
}
```

**Response**

```typescript
interface ChatResponse {
  message: string; // Conversational response
  metadata?: {
    intent?: string; // add_task, list_tasks, complete_task, delete_task, update_task, query
    tool_called?: string;
    success?: boolean;
    task_id?: string;
    [key: string]: any;
  };
}
```

**Example Request**

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Cookie: session_id=YOUR_SESSION_TOKEN" \
  -d '{"text": "Add a task to buy groceries"}'
```

**Example Response**

```json
{
  "message": "I've added 'buy groceries' to your tasks!",
  "metadata": {
    "intent": "add_task",
    "tool_called": "add_task",
    "success": true,
    "task_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Title must be between 1 and 200 characters."
}
```

### 401 Unauthorized
```json
{
  "detail": "You must be logged in to access this resource"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Too many requests. Please wait 45 seconds and try again."
}
```

Headers:
- `Retry-After`: Seconds until rate limit resets
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Seconds until rate limit resets

### 500 Internal Server Error
```json
{
  "detail": "Something went wrong. Please try again in a moment."
}
```

### 503 Service Unavailable
```json
{
  "detail": "The chatbot is temporarily unavailable. Please try again later."
}
```

## Frontend Implementation

### React/Next.js Service

```typescript
// src/services/chatService.ts
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  metadata?: Record<string, any>;
  timestamp: Date;
}

export class ChatService {
  private apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
    withCredentials: true, // Important: Include session cookies
  });

  /**
   * Send a message to the chatbot
   */
  async sendMessage(text: string): Promise<ChatMessage> {
    try {
      const response = await this.apiClient.post<{
        message: string;
        metadata?: Record<string, any>;
      }>('/api/chat', { text });

      return {
        role: 'assistant',
        content: response.data.message,
        metadata: response.data.metadata,
        timestamp: new Date(),
      };
    } catch (error) {
      if (axios.isAxiosError(error)) {
        if (error.response?.status === 401) {
          throw new Error('Please log in to use the chatbot');
        } else if (error.response?.status === 429) {
          const retryAfter = error.response.headers['retry-after'];
          throw new Error(
            `Too many requests. Please wait ${retryAfter} seconds and try again.`
          );
        } else if (error.response?.status === 503) {
          throw new Error('The chatbot is temporarily unavailable. Please try again later.');
        }
      }
      throw new Error('Failed to send message. Please try again.');
    }
  }

  /**
   * Check chatbot health status
   */
  async checkHealth(): Promise<boolean> {
    try {
      await this.apiClient.get('/api/chat/health');
      return true;
    } catch {
      return false;
    }
  }
}

export const chatService = new ChatService();
```

### React Component Example

```typescript
// src/components/TodoChatbot.tsx
import { useState } from 'react';
import { chatService, ChatMessage } from '@/services/chatService';

export default function TodoChatbot() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      const response = await chatService.sendMessage(input);
      setMessages((prev) => [...prev, response]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <p>{msg.content}</p>
            {msg.metadata && (
              <small className="metadata">
                Intent: {msg.metadata.intent || 'unknown'}
              </small>
            )}
          </div>
        ))}
      </div>

      {error && <div className="error">{error}</div>}

      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask me anything about your tasks..."
          maxLength={1000}
          disabled={loading}
        />
        <button onClick={handleSend} disabled={loading || !input.trim()}>
          {loading ? 'Sending...' : 'Send'}
        </button>
      </div>
    </div>
  );
}
```

## Supported Natural Language Commands

The chatbot understands various phrasings for each action:

### Add Task
- "Add a task to buy groceries"
- "Create a new task: call mom"
- "Remind me to finish the report"
- "I need to buy milk"

### List Tasks
- "What are my tasks?"
- "Show me my tasks"
- "List all my todos"
- "What do I need to do?"
- "Show my incomplete tasks"

### Complete Task
- "Mark 'buy groceries' as done"
- "Complete the task about calling mom"
- "Finish the report task"
- "I completed buy groceries"

### Delete Task
- "Delete my task about groceries"
- "Remove the call mom task"
- "Get rid of the report task"

### Update Task
- "Change 'buy groceries' to 'buy groceries and milk'"
- "Update my task: add note about the deadline"
- "Modify the report task title"

### Query (Analytical)
- "How many tasks do I have?"
- "What's my oldest task?"
- "Show me my task statistics"
- "Who am I?" (shows logged-in user)

## Important Notes

### Stateless Architecture
- The chatbot is **completely stateless**
- Each message is processed independently
- No conversation history is maintained
- Users cannot refer to previous messages ("that task", "the one I just mentioned")

### Authentication
- All requests require a valid session cookie
- Use `withCredentials: true` in axios/fetch
- Handle 401 errors by redirecting to login

### Rate Limiting
- 30 requests per 60 seconds per user
- Check `X-RateLimit-Remaining` header
- Handle 429 errors with retry logic using `Retry-After` header

### Error Handling
- Always display user-friendly error messages from the API
- Never expose stack traces or internal error details to users
- Implement retry logic for 503 errors (service temporarily unavailable)

### Performance
- Target response time: <3 seconds (95th percentile)
- Show loading indicators during requests
- Consider implementing request timeouts (5-10 seconds)

### User Experience Tips
1. **Clear Input After Send**: Clear the input field immediately after sending
2. **Loading Indicators**: Show clear loading state while waiting for response
3. **Error Recovery**: Provide clear error messages and retry options
4. **Example Prompts**: Show example commands to help users get started
5. **Metadata Display**: Optionally show detected intent/success status for debugging

## Testing the Integration

### 1. Health Check
```bash
curl http://localhost:8000/api/chat/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "todo-ai-chatbot",
  "model": "command-r"
}
```

### 2. Chat Request (with authentication)
```bash
# First, get a session cookie by logging in
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}' \
  -c cookies.txt

# Then use the session cookie for chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"text": "Add a task to test the chatbot"}'
```

### 3. Rate Limiting Test
```bash
# Send 31 requests rapidly to trigger rate limit
for i in {1..31}; do
  curl -X POST http://localhost:8000/api/chat \
    -H "Content-Type: application/json" \
    -b cookies.txt \
    -d "{\"text\": \"Test message $i\"}" \
    -w "\nStatus: %{http_code}\n"
done
```

## Environment Variables

Required in your frontend `.env.local`:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Or for production
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

## CORS Configuration

The backend is configured to accept requests from:
- `http://localhost:3000`
- `http://127.0.0.1:3000`

For production, update `CORS_ORIGINS` in backend `.env`:

```bash
CORS_ORIGINS=["https://your-frontend-domain.com"]
```

## Troubleshooting

### "401 Unauthorized" on every request
- Verify session cookie is being sent (`withCredentials: true`)
- Check that user is logged in
- Verify backend session management is working

### "429 Too Many Requests" frequently
- Implement client-side request throttling
- Show rate limit info to users (`X-RateLimit-Remaining` header)
- Increase rate limits if needed (backend configuration)

### Slow response times (>3s)
- Check Cohere API latency
- Monitor backend logs for slow database queries
- Consider adding request timeout handling

### "503 Service Unavailable"
- Verify `COHERE_API_KEY` is configured in backend
- Check backend logs for Cohere API errors
- Implement retry logic with exponential backoff

## Next Steps

1. Implement the ChatService in your frontend
2. Create a chat UI component
3. Add error handling and loading states
4. Test authentication flow
5. Test rate limiting behavior
6. Add analytics/logging for chat interactions
7. Consider adding typing indicators
8. Implement message persistence (optional)

## Support

For issues or questions:
- Check backend logs: `docker logs backend` or check application logs
- Verify Cohere API status: https://status.cohere.ai/
- Review API documentation: `/docs` endpoint (FastAPI auto-generated docs)
