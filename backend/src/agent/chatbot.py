"""
Todo AI Chatbot Agent.

This module implements the stateless chatbot agent that:
1. Receives natural language messages from users
2. Detects intent using Cohere AI
3. Calls appropriate MCP tools
4. Returns user-friendly responses

The agent is COMPLETELY STATELESS per FR-003 - no conversation history is retained.
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
import cohere
from uuid import UUID

from ..mcp.tools import (
    add_task, list_tasks, complete_task, delete_task, update_task
)
from ..mcp.schemas import (
    AddTaskInput, ListTasksInput, CompleteTaskInput,
    DeleteTaskInput, UpdateTaskInput, TaskStatus
)
from ..utils.errors import (
    AgentError, ValidationError, NotFoundError, DatabaseError,
    agent_error_response
)
from ..config import settings, get_logger

logger = get_logger("agent.chatbot")


class TodoChatbot:
    """
    Stateless AI chatbot for natural language todo management.

    This chatbot uses Cohere's Command-R model for intent recognition and
    natural language understanding. Each message is processed independently
    without conversation history (stateless architecture).

    Constitutional requirements:
    - Stateless: No memory between requests (FR-003)
    - Tool delegation: All database operations via MCP tools (FR-005)
    - User isolation: All operations scoped to authenticated user (FR-008)
    - User-friendly errors: No technical jargon or stack traces (FR-010)
    """

    def __init__(self, user_id: UUID, db: Session):
        """
        Initialize chatbot for a single request.

        Args:
            user_id: Authenticated user's ID
            db: Database session for this request
        """
        self.user_id = str(user_id)
        self.db = db

        # Initialize Cohere client
        if not settings.COHERE_API_KEY:
            raise ValueError("COHERE_API_KEY not configured in environment")

        self.cohere_client = cohere.Client(api_key=settings.COHERE_API_KEY)

    async def process_message(self, user_message: str) -> Dict[str, Any]:
        """
        Process user message and return response.

        This is the main entry point for the chatbot. It:
        1. Detects intent from natural language
        2. Extracts parameters (task title, description, id, etc.)
        3. Calls appropriate MCP tool
        4. Returns user-friendly response

        Args:
            user_message: Natural language message from user

        Returns:
            Dict with 'message' (str) and optional 'metadata' (dict)

        Raises:
            AgentError: If intent detection or processing fails
        """
        try:
            logger.info("Processing user message", extra={
                "user_id": self.user_id,
                "message_length": len(user_message)
            })

            # Detect intent and extract parameters
            intent_result = await self._detect_intent(user_message)
            intent = intent_result["intent"]
            params = intent_result["params"]

            logger.info("Intent detected", extra={
                "user_id": self.user_id,
                "intent": intent,
                "params": params
            })

            # Route to appropriate handler
            if intent == "add_task":
                return await self._handle_add_task(params)
            elif intent == "list_tasks":
                return await self._handle_list_tasks(params)
            elif intent == "complete_task":
                return await self._handle_complete_task(params)
            elif intent == "delete_task":
                return await self._handle_delete_task(params)
            elif intent == "update_task":
                return await self._handle_update_task(params)
            elif intent == "query":
                return await self._handle_query(params)
            else:
                # Unknown intent
                return {
                    "message": "I'm not sure what you want to do. You can add, list, complete, delete, or update tasks.",
                    "metadata": {
                        "intent": "unknown",
                        "tool_called": None
                    }
                }

        except (ValidationError, NotFoundError, DatabaseError) as e:
            # These are expected errors with user-friendly messages
            logger.warning(f"Chatbot error: {e.message}", extra={
                "user_id": self.user_id,
                "error_type": type(e).__name__,
                "context": e.context
            })
            return {
                "message": e.user_message,
                "metadata": {
                    "error": type(e).__name__
                }
            }
        except Exception as e:
            # Unexpected error - log details but return generic message
            logger.error(f"Unexpected chatbot error: {str(e)}", extra={
                "user_id": self.user_id,
                "error": str(e)
            })
            return {
                "message": agent_error_response(),
                "metadata": {
                    "error": "AgentError"
                }
            }

    async def _detect_intent(self, user_message: str) -> Dict[str, Any]:
        """
        Detect user intent and extract parameters using Cohere.

        Uses Cohere's command-r model to classify intent and extract
        relevant parameters (task title, description, id, etc.).

        Args:
            user_message: Natural language message

        Returns:
            Dict with 'intent' (str) and 'params' (dict)
        """
        # Build prompt for intent classification
        system_prompt = """You are an intent classifier for a todo task manager. Classify the user's intent into one of these categories:
- add_task: User wants to create a new task
- list_tasks: User wants to see their tasks
- complete_task: User wants to mark a task as done
- delete_task: User wants to remove a task
- update_task: User wants to modify a task
- query: User has a question about their tasks or account
- unknown: Intent is unclear

Extract relevant parameters:
- For add_task: title (required), description (optional)
- For complete_task/delete_task/update_task: task_identifier (title or keywords)
- For update_task: new_title or new_description
- For list_tasks: status_filter ("pending", "completed", or null)

Return JSON format: {"intent": "...", "params": {...}}"""

        try:
            # Call Cohere API
            response = self.cohere_client.chat(
                message=user_message,
                model=settings.CHATBOT_MODEL,
                temperature=settings.CHATBOT_TEMPERATURE,
                max_tokens=200,  # Intent detection needs shorter response
                preamble=system_prompt
            )

            # Parse response (simplified - in production, use structured output)
            response_text = response.text.strip()

            # Simple intent detection (in production, use Cohere's classify endpoint)
            intent, params = self._parse_intent_simple(user_message)

            return {
                "intent": intent,
                "params": params
            }

        except Exception as e:
            logger.error(f"Cohere API error: {str(e)}", extra={
                "user_id": self.user_id,
                "error": str(e)
            })
            # Fallback to simple pattern matching
            intent, params = self._parse_intent_simple(user_message)
            return {
                "intent": intent,
                "params": params
            }

    def _parse_intent_simple(self, message: str) -> tuple[str, Dict[str, Any]]:
        """
        Simple rule-based intent detection (fallback).

        This is a simplified implementation for MVP. In production,
        use Cohere's classify endpoint or fine-tuned model.
        """
        message_lower = message.lower()

        # Add task patterns
        if any(word in message_lower for word in ["add", "create", "new task", "remind me"]):
            # Extract title (everything after trigger word)
            title = message.replace("add ", "").replace("create ", "").replace("remind me to ", "")
            title = title.replace("a task to ", "").replace("task: ", "").strip()
            return "add_task", {"title": title, "description": None}

        # List tasks patterns
        elif any(word in message_lower for word in ["list", "show", "what are my", "my tasks"]):
            status_filter = None
            if "incomplete" in message_lower or "pending" in message_lower:
                status_filter = "pending"
            elif "complete" in message_lower or "finished" in message_lower or "done" in message_lower:
                status_filter = "completed"
            return "list_tasks", {"status_filter": status_filter}

        # Complete task patterns
        elif any(word in message_lower for word in ["complete", "finish", "done", "mark as done"]):
            # Extract task identifier
            task_id = message.replace("complete ", "").replace("finish ", "").replace("mark as done ", "").strip()
            return "complete_task", {"task_identifier": task_id}

        # Delete task patterns
        elif any(word in message_lower for word in ["delete", "remove", "get rid of"]):
            task_id = message.replace("delete ", "").replace("remove ", "").replace("get rid of ", "").strip()
            return "delete_task", {"task_identifier": task_id}

        # Update task patterns
        elif any(word in message_lower for word in ["update", "change", "modify", "edit"]):
            # Simplified: assume everything after "to" is new title
            if " to " in message_lower:
                parts = message.split(" to ", 1)
                task_id = parts[0].replace("change ", "").replace("update ", "").strip()
                new_title = parts[1].strip()
                return "update_task", {"task_identifier": task_id, "new_title": new_title}
            return "update_task", {"task_identifier": message}

        # Query patterns
        elif any(word in message_lower for word in ["how many", "count", "who am i", "oldest"]):
            return "query", {"question": message}

        # Unknown
        else:
            return "unknown", {}

    async def _handle_add_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle add_task intent."""
        input_data = AddTaskInput(
            user_id=self.user_id,
            title=params.get("title", ""),
            description=params.get("description")
        )
        result = add_task(self.db, input_data)
        return {
            "message": result.message,
            "metadata": {
                "intent": "add_task",
                "tool_called": "add_task",
                "success": result.success,
                "task_id": result.task_id
            }
        }

    async def _handle_list_tasks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list_tasks intent."""
        status_filter = params.get("status_filter")
        if status_filter:
            status_filter = TaskStatus(status_filter)

        input_data = ListTasksInput(
            user_id=self.user_id,
            status=status_filter
        )
        result = list_tasks(self.db, input_data)

        # Format response message
        if result.count == 0:
            message = "You don't have any tasks yet. Would you like to add one?"
        else:
            task_list = "\n".join([
                f"{i+1}. {task.title} ({task.status})"
                for i, task in enumerate(result.tasks)
            ])
            message = f"You have {result.count} task{'s' if result.count > 1 else ''}:\n{task_list}"

        return {
            "message": message,
            "metadata": {
                "intent": "list_tasks",
                "tool_called": "list_tasks",
                "count": result.count
            }
        }

    async def _handle_complete_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle complete_task intent."""
        # First, find task by identifier (title or keywords)
        task_id = await self._resolve_task_identifier(params.get("task_identifier", ""))

        input_data = CompleteTaskInput(
            user_id=self.user_id,
            task_id=task_id
        )
        result = complete_task(self.db, input_data)
        return {
            "message": result.message,
            "metadata": {
                "intent": "complete_task",
                "tool_called": "complete_task",
                "success": result.success
            }
        }

    async def _handle_delete_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle delete_task intent."""
        task_id = await self._resolve_task_identifier(params.get("task_identifier", ""))

        input_data = DeleteTaskInput(
            user_id=self.user_id,
            task_id=task_id
        )
        result = delete_task(self.db, input_data)
        return {
            "message": result.message,
            "metadata": {
                "intent": "delete_task",
                "tool_called": "delete_task",
                "success": result.success
            }
        }

    async def _handle_update_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle update_task intent."""
        task_id = await self._resolve_task_identifier(params.get("task_identifier", ""))

        input_data = UpdateTaskInput(
            user_id=self.user_id,
            task_id=task_id,
            title=params.get("new_title"),
            description=params.get("new_description")
        )
        result = update_task(self.db, input_data)
        return {
            "message": result.message,
            "metadata": {
                "intent": "update_task",
                "tool_called": "update_task",
                "success": result.success
            }
        }

    async def _handle_query(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle analytical queries about tasks and user info.

        Supports queries like:
        - "How many tasks do I have?"
        - "What's my oldest task?"
        - "What's my newest task?"
        - "How many completed tasks?"
        - "Who am I?"
        - "When did I create my first task?"
        """
        question = params.get("question", "").lower()

        # Handle "who am I" queries
        if "who am i" in question or "my email" in question or "my account" in question:
            # Get user info from database
            from ..models.user import User
            user = self.db.query(User).filter(User.id == UUID(self.user_id)).first()
            if user:
                message = f"You're logged in as {user.email}."
            else:
                message = "I couldn't find your account information."

            return {
                "message": message,
                "metadata": {
                    "intent": "query",
                    "query_type": "user_info"
                }
            }

        # Get all user's tasks for analysis
        input_data = ListTasksInput(user_id=self.user_id, status=None)
        result = list_tasks(self.db, input_data)

        # Count queries
        if "how many" in question or "count" in question:
            if "complete" in question or "done" in question or "finished" in question:
                # Count completed tasks only
                completed = sum(1 for t in result.tasks if t.status == "completed")
                message = f"You have {completed} completed task{'s' if completed != 1 else ''}."
            elif "incomplete" in question or "pending" in question or "todo" in question:
                # Count pending tasks only
                pending = sum(1 for t in result.tasks if t.status == "pending")
                message = f"You have {pending} pending task{'s' if pending != 1 else ''}."
            else:
                # Count all tasks
                pending = sum(1 for t in result.tasks if t.status == "pending")
                completed = sum(1 for t in result.tasks if t.status == "completed")
                if result.count == 0:
                    message = "You don't have any tasks yet."
                else:
                    message = f"You have {result.count} task{'s' if result.count != 1 else ''} total: {pending} pending and {completed} completed."

        # Oldest task queries
        elif "oldest" in question or "first" in question:
            if result.tasks:
                # Filter to pending tasks if specified
                if "pending" in question or "incomplete" in question:
                    pending_tasks = [t for t in result.tasks if t.status == "pending"]
                    if pending_tasks:
                        oldest = min(pending_tasks, key=lambda t: t.created_at)
                        message = f"Your oldest pending task is '{oldest.title}' from {oldest.created_at[:10]}."
                    else:
                        message = "You don't have any pending tasks."
                else:
                    oldest = min(result.tasks, key=lambda t: t.created_at)
                    message = f"Your oldest task is '{oldest.title}' (created {oldest.created_at[:10]})."
            else:
                message = "You don't have any tasks yet."

        # Newest task queries
        elif "newest" in question or "latest" in question or "recent" in question:
            if result.tasks:
                newest = max(result.tasks, key=lambda t: t.created_at)
                message = f"Your most recent task is '{newest.title}' (created {newest.created_at[:10]})."
            else:
                message = "You don't have any tasks yet."

        # Empty list check
        elif "do i have" in question or "any tasks" in question:
            if result.count == 0:
                message = "You don't have any tasks yet. Would you like to add one?"
            else:
                message = f"Yes, you have {result.count} task{'s' if result.count != 1 else ''}."

        # Default response
        else:
            if result.count == 0:
                message = "You don't have any tasks yet."
            else:
                pending = sum(1 for t in result.tasks if t.status == "pending")
                completed = sum(1 for t in result.tasks if t.status == "completed")
                message = f"You have {result.count} task{'s' if result.count != 1 else ''} total: {pending} pending and {completed} completed."

        return {
            "message": message,
            "metadata": {
                "intent": "query",
                "tool_called": "list_tasks",
                "query_type": "analytical"
            }
        }

    async def _resolve_task_identifier(self, identifier: str) -> str:
        """
        Resolve task identifier (title keywords) to task UUID.

        Args:
            identifier: Task title or keywords

        Returns:
            str: Task UUID

        Raises:
            NotFoundError: If no matching task found
        """
        # List all user's tasks
        input_data = ListTasksInput(user_id=self.user_id, status=None)
        result = list_tasks(self.db, input_data)

        if not result.tasks:
            raise NotFoundError(
                message=f"No tasks found for user {self.user_id}",
                user_message="You don't have any tasks yet.",
                context={"user_id": self.user_id}
            )

        # Search for matching task by title
        identifier_lower = identifier.lower()
        for task in result.tasks:
            if identifier_lower in task.title.lower():
                return task.id

        # No match found
        raise NotFoundError(
            message=f"No task matching identifier: {identifier}",
            user_message=f"I couldn't find a task matching '{identifier}'. Would you like to see your current tasks?",
            context={"user_id": self.user_id, "identifier": identifier}
        )
