import threading
from typing import Dict, List, Any, Optional


def _estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token on average."""
    return max(1, len(text) // 4)


class ChatHistoryManager:
    """Manages chat history with configurable compaction strategies."""

    VALID_STRATEGIES = ("accumulate", "window", "token_budget", "summarize")

    def __init__(
        self,
        strategy: str = "accumulate",
        window_size: int = 20,
        token_budget: int = 8000,
    ):
        if strategy not in self.VALID_STRATEGIES:
            raise ValueError(
                f"Invalid strategy '{strategy}'. Must be one of {self.VALID_STRATEGIES}"
            )

        self._strategy = strategy
        self._window_size = window_size
        self._token_budget = token_budget
        self._messages: List[Dict[str, Any]] = []
        self._summary: Optional[str] = None
        self._lock = threading.Lock()

    def add_message(self, role: str, content: str):
        """Add a message and apply compaction strategy."""
        with self._lock:
            self._messages.append({"role": role, "content": content})
            self._compact()

    def get_messages(self) -> List[Dict[str, Any]]:
        """Get current messages, including summary if present."""
        with self._lock:
            if self._summary:
                return [{"role": "system", "content": f"Summary: {self._summary}"}] + self._messages
            return list(self._messages)

    def clear(self):
        """Clear all messages and summary."""
        with self._lock:
            self._messages = []
            self._summary = None

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the chat history."""
        with self._lock:
            total_chars = sum(len(m["content"]) for m in self._messages)
            estimated_tokens = sum(_estimate_tokens(m["content"]) for m in self._messages)
            return {
                "message_count": len(self._messages),
                "strategy": self._strategy,
                "total_chars": total_chars,
                "estimated_tokens": estimated_tokens,
                "has_summary": self._summary is not None,
            }

    def _compact(self):
        """Apply the configured compaction strategy."""
        if self._strategy == "accumulate":
            return
        elif self._strategy == "window":
            self._compact_window()
        elif self._strategy == "token_budget":
            self._compact_token_budget()
        elif self._strategy == "summarize":
            self._compact_summarize()

    def _compact_window(self):
        """Keep only the last N message pairs."""
        max_messages = self._window_size * 2
        if len(self._messages) > max_messages:
            self._messages = self._messages[-max_messages:]

    def _compact_token_budget(self):
        """Drop oldest messages to stay under token budget."""
        while True:
            total = sum(_estimate_tokens(m["content"]) for m in self._messages)
            if total <= self._token_budget or len(self._messages) <= 2:
                break
            # Remove oldest message
            self._messages.pop(0)

    def _compact_summarize(self):
        """Summarize old messages, keep recent window."""
        max_messages = self._window_size
        if len(self._messages) > max_messages:
            # Move old messages to summary (simplified: just concatenate)
            old_messages = self._messages[:-max_messages]
            recent_messages = self._messages[-max_messages:]

            summary_parts = []
            for m in old_messages:
                prefix = "User" if m["role"] == "user" else "Assistant"
                summary_parts.append(f"{prefix}: {m['content'][:100]}")

            if self._summary:
                self._summary = f"{self._summary}; " + "; ".join(summary_parts)
            else:
                self._summary = "; ".join(summary_parts)

            self._messages = recent_messages
