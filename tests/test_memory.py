import pytest
from src.rosa.memory.chat_history import ChatHistoryManager


def test_accumulate_strategy_keeps_all():
    mgr = ChatHistoryManager(strategy="accumulate")
    mgr.add_message("user", "Hello")
    mgr.add_message("assistant", "Hi there")
    mgr.add_message("user", "How are you?")
    assert len(mgr.get_messages()) == 3


def test_window_strategy_limits_count():
    mgr = ChatHistoryManager(strategy="window", window_size=2)
    mgr.add_message("user", "msg1")
    mgr.add_message("assistant", "reply1")
    mgr.add_message("user", "msg2")
    mgr.add_message("assistant", "reply2")
    mgr.add_message("user", "msg3")
    mgr.add_message("assistant", "reply3")
    messages = mgr.get_messages()
    assert len(messages) == 4  # 2 pairs
    assert messages[0]["content"] == "msg2"


def test_token_budget_strategy_limits_tokens():
    mgr = ChatHistoryManager(strategy="token_budget", token_budget=10)
    mgr.add_message("user", "This is a test message")
    mgr.add_message("assistant", "This is a reply message")
    mgr.add_message("user", "Short")
    messages = mgr.get_messages()
    # Should drop oldest messages to stay under budget
    assert len(messages) <= 2


def test_summarize_strategy_keeps_recent():
    mgr = ChatHistoryManager(strategy="summarize", window_size=2)
    mgr.add_message("user", "msg1")
    mgr.add_message("assistant", "reply1")
    mgr.add_message("user", "msg2")
    mgr.add_message("assistant", "reply2")
    mgr.add_message("user", "msg3")
    messages = mgr.get_messages()
    assert len(messages) <= 3  # Summary + recent pair


def test_invalid_strategy_raises():
    with pytest.raises(ValueError):
        ChatHistoryManager(strategy="invalid")


def test_clear_history():
    mgr = ChatHistoryManager()
    mgr.add_message("user", "Hello")
    mgr.clear()
    assert len(mgr.get_messages()) == 0


def test_get_stats():
    mgr = ChatHistoryManager()
    mgr.add_message("user", "Hello world")
    mgr.add_message("assistant", "Hi")
    stats = mgr.get_stats()
    assert stats["message_count"] == 2
    assert stats["strategy"] == "accumulate"
    assert "estimated_tokens" in stats
