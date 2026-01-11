"""
Tests for Lab 4 memory agent.
"""

import json
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from memory_agent import MemoryAgent, Fact, RetrievalTrace  # noqa: E402


class TestMemoryAgent:
    """Test suite for MemoryAgent class."""

    def test_agent_initialization(self):
        """Test agent initializes with correct default values."""
        agent = MemoryAgent()
        assert agent.max_short_term == 10
        stats = agent.get_memory_stats()
        assert stats["short_term_count"] == 0
        assert stats["long_term_count"] == 0

    def test_agent_initialization_custom_size(self):
        """Test agent initializes with custom short-term size."""
        agent = MemoryAgent(max_short_term=5)
        assert agent.max_short_term == 5

    def test_agent_initialization_invalid_size(self):
        """Test agent rejects invalid max_short_term size."""
        with pytest.raises(ValueError, match="max_short_term must be positive"):
            MemoryAgent(max_short_term=0)
        
        with pytest.raises(ValueError, match="max_short_term must be positive"):
            MemoryAgent(max_short_term=-1)

    def test_add_conversation_turn(self):
        """Test adding conversation turns to short-term memory."""
        agent = MemoryAgent()
        agent.add_conversation_turn("user", "Hello")
        agent.add_conversation_turn("assistant", "Hi there!")
        
        stats = agent.get_memory_stats()
        assert stats["short_term_count"] == 2
        
        history = agent.get_conversation_history()
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello"
        assert history[1]["role"] == "assistant"
        assert history[1]["content"] == "Hi there!"

    def test_short_term_memory_fifo_pruning(self):
        """Test short-term memory respects max size with FIFO pruning."""
        agent = MemoryAgent(max_short_term=3)
        
        # Add 5 items to memory with max of 3
        for i in range(5):
            agent.add_conversation_turn("user", f"Message {i}")
        
        stats = agent.get_memory_stats()
        assert stats["short_term_count"] == 3
        
        # First two messages should be pruned (FIFO)
        history = agent.get_conversation_history()
        assert len(history) == 3
        assert history[0]["content"] == "Message 2"
        assert history[1]["content"] == "Message 3"
        assert history[2]["content"] == "Message 4"

    def test_add_fact(self):
        """Test adding facts to long-term memory."""
        agent = MemoryAgent()
        agent.add_fact("User lives in Seattle", confidence=1.0)
        agent.add_fact("User likes hiking", confidence=0.9)
        
        stats = agent.get_memory_stats()
        assert stats["long_term_count"] == 2
        
        facts = agent.get_all_facts()
        assert len(facts) == 2
        assert any(f.content == "User lives in Seattle" for f in facts)
        assert any(f.content == "User likes hiking" for f in facts)

    def test_add_fact_with_key(self):
        """Test adding facts with custom keys."""
        agent = MemoryAgent()
        agent.add_fact("User lives in Seattle", confidence=1.0, key="location")
        agent.add_fact("User likes hiking", confidence=0.9, key="hobby")
        
        facts = agent.get_all_facts()
        assert len(facts) == 2

    def test_add_fact_invalid_confidence(self):
        """Test fact rejects invalid confidence scores."""
        agent = MemoryAgent()
        
        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            agent.add_fact("Test", confidence=1.5)
        
        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            agent.add_fact("Test", confidence=-0.1)

    def test_retrieve_empty_memory(self):
        """Test retrieval from empty memory returns empty list."""
        agent = MemoryAgent()
        results = agent.retrieve("test query")
        assert results == []

    def test_retrieve_by_relevance(self):
        """Test memory retrieval based on query relevance."""
        agent = MemoryAgent()
        
        # Add some facts
        agent.add_fact("User lives in Seattle")
        agent.add_fact("User enjoys hiking")
        agent.add_fact("User is vegetarian")
        
        # Add conversation
        agent.add_conversation_turn("user", "I like hiking in the mountains")
        
        # Retrieve memories related to hiking
        results = agent.retrieve("hiking mountains")
        
        # Should retrieve items containing "hiking"
        hiking_contents = [item.content for item in results]
        assert any("hiking" in content.lower() for content in hiking_contents)

    def test_retrieve_with_trace(self, capsys):
        """Test memory retrieval with trace output."""
        agent = MemoryAgent()
        agent.add_fact("User lives in Seattle")
        agent.add_conversation_turn("user", "What's the weather in Seattle?")
        
        # Retrieve with trace
        results = agent.retrieve("Seattle weather", include_trace=True)
        
        # Check trace was printed
        captured = capsys.readouterr()
        assert "Memory Retrieval Trace" in captured.out
        assert "Query: Seattle weather" in captured.out
        assert "Short-term memory" in captured.out
        assert "Long-term memory" in captured.out

    def test_retrieval_latency(self):
        """Test retrieval latency is under 100ms target."""
        agent = MemoryAgent()
        
        # Add multiple facts to test with realistic data
        for i in range(20):
            agent.add_fact(f"Fact number {i} about various topics")
        
        for i in range(10):
            agent.add_conversation_turn("user", f"Message {i}")
        
        # Measure retrieval time
        start = time.time()
        agent.retrieve("topics message")
        latency_ms = (time.time() - start) * 1000
        
        # Should be under 100ms
        assert latency_ms < 100, f"Retrieval took {latency_ms:.2f}ms, expected <100ms"

    def test_get_all_facts(self):
        """Test retrieving all facts from long-term memory."""
        agent = MemoryAgent()
        
        expected_facts = [
            "User lives in Seattle",
            "User enjoys hiking",
            "User is vegetarian",
        ]
        
        for fact in expected_facts:
            agent.add_fact(fact)
        
        facts = agent.get_all_facts()
        fact_contents = [f.content for f in facts]
        
        assert len(facts) == 3
        for expected in expected_facts:
            assert expected in fact_contents

    def test_get_conversation_history(self):
        """Test retrieving conversation history."""
        agent = MemoryAgent()
        
        turns = [
            ("user", "Hello"),
            ("assistant", "Hi!"),
            ("user", "How are you?"),
            ("assistant", "I'm doing well!"),
        ]
        
        for role, content in turns:
            agent.add_conversation_turn(role, content)
        
        history = agent.get_conversation_history()
        assert len(history) == 4
        
        for i, (role, content) in enumerate(turns):
            assert history[i]["role"] == role
            assert history[i]["content"] == content

    def test_memory_persistence_save_load(self):
        """Test memory persistence through save and load."""
        agent = MemoryAgent(max_short_term=5)
        
        # Add some data
        agent.add_fact("User lives in Seattle", confidence=1.0)
        agent.add_fact("User enjoys hiking", confidence=0.9)
        agent.add_conversation_turn("user", "Hello")
        agent.add_conversation_turn("assistant", "Hi there!")
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name
        
        try:
            agent.save_to_json(temp_path)
            
            # Verify file was created
            assert Path(temp_path).exists()
            
            # Load into new agent
            loaded_agent = MemoryAgent.load_from_json(temp_path)
            
            # Verify configuration
            assert loaded_agent.max_short_term == 5
            
            # Verify facts
            facts = loaded_agent.get_all_facts()
            assert len(facts) == 2
            fact_contents = [f.content for f in facts]
            assert "User lives in Seattle" in fact_contents
            assert "User enjoys hiking" in fact_contents
            
            # Verify conversation history
            history = loaded_agent.get_conversation_history()
            assert len(history) == 2
            assert history[0]["content"] == "Hello"
            assert history[1]["content"] == "Hi there!"
        
        finally:
            # Clean up
            Path(temp_path).unlink(missing_ok=True)

    def test_memory_persistence_json_format(self):
        """Test saved JSON format is correct."""
        agent = MemoryAgent(max_short_term=3)
        agent.add_fact("Test fact", confidence=0.8)
        agent.add_conversation_turn("user", "Test message")
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name
        
        try:
            agent.save_to_json(temp_path)
            
            # Read and verify JSON structure
            with open(temp_path) as f:
                data = json.load(f)
            
            assert "max_short_term" in data
            assert "short_term" in data
            assert "long_term" in data
            assert data["max_short_term"] == 3
            assert isinstance(data["short_term"], list)
            assert isinstance(data["long_term"], list)
            assert len(data["long_term"]) == 1
            assert data["long_term"][0]["content"] == "Test fact"
            assert data["long_term"][0]["confidence"] == 0.8
        
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_clear_memory(self):
        """Test clearing all memory tiers."""
        agent = MemoryAgent()
        
        # Add data to both tiers
        agent.add_fact("Test fact")
        agent.add_conversation_turn("user", "Test message")
        
        # Verify data exists
        assert agent.get_memory_stats()["total_items"] > 0
        
        # Clear memory
        agent.clear()
        
        # Verify all memory is cleared
        stats = agent.get_memory_stats()
        assert stats["short_term_count"] == 0
        assert stats["long_term_count"] == 0
        assert stats["total_items"] == 0

    def test_memory_stats(self):
        """Test memory statistics calculation."""
        agent = MemoryAgent(max_short_term=5)
        
        # Add data
        agent.add_fact("Fact 1")
        agent.add_fact("Fact 2")
        agent.add_conversation_turn("user", "Message 1")
        agent.add_conversation_turn("user", "Message 2")
        agent.add_conversation_turn("user", "Message 3")
        
        stats = agent.get_memory_stats()
        
        assert stats["short_term_count"] == 3
        assert stats["short_term_max"] == 5
        assert stats["short_term_usage"] == 0.6
        assert stats["long_term_count"] == 2
        assert stats["total_items"] == 5


class TestFact:
    """Test suite for Fact class."""

    def test_fact_initialization(self):
        """Test fact initializes with correct values."""
        fact = Fact("Test content", confidence=0.9)
        assert fact.content == "Test content"
        assert fact.confidence == 0.9
        assert isinstance(fact.timestamp, datetime)

    def test_fact_to_memory_item(self):
        """Test fact converts to MemoryItem correctly."""
        fact = Fact("Test content", confidence=0.8)
        item = fact.to_memory_item()
        
        assert item.content == "Test content"
        assert item.metadata["confidence"] == 0.8

    def test_fact_serialization(self):
        """Test fact serialization to dictionary."""
        fact = Fact("Test content", confidence=0.7, metadata={"key": "value"})
        data = fact.to_dict()
        
        assert data["content"] == "Test content"
        assert data["confidence"] == 0.7
        assert data["metadata"]["key"] == "value"
        assert "timestamp" in data

    def test_fact_deserialization(self):
        """Test fact deserialization from dictionary."""
        data = {
            "content": "Test content",
            "confidence": 0.9,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {"key": "value"},
        }
        
        fact = Fact.from_dict(data)
        assert fact.content == "Test content"
        assert fact.confidence == 0.9
        assert fact.metadata["key"] == "value"


class TestRetrievalTrace:
    """Test suite for RetrievalTrace class."""

    def test_retrieval_trace_str(self):
        """Test retrieval trace string representation."""
        from src.agent_labs.memory import MemoryItem
        
        items = [MemoryItem(content="Test item", metadata={"confidence": 0.9})]
        trace = RetrievalTrace(
            query="test query",
            short_term_items=items,
            long_term_items=items,
            retrieval_time_ms=5.5,
            relevance_scores={"Test item": 0.75},
        )
        
        trace_str = str(trace)
        assert "Memory Retrieval Trace" in trace_str
        assert "Query: test query" in trace_str
        assert "5.50ms" in trace_str
        assert "Short-term memory" in trace_str
        assert "Long-term memory" in trace_str
        assert "Relevance scores" in trace_str


class TestMultiTurnConversation:
    """Integration test for multi-turn conversation scenario."""

    def test_multi_turn_conversation_flow(self):
        """Test complete multi-turn conversation flow."""
        agent = MemoryAgent(max_short_term=10)
        
        # Turn 1: User shares location
        agent.add_conversation_turn("user", "I live in Seattle")
        agent.add_fact("User lives in Seattle", confidence=1.0, key="location")
        
        # Turn 2: Query requiring location
        agent.add_conversation_turn("user", "What's the weather like here?")
        memories = agent.retrieve("weather Seattle")
        assert len(memories) > 0
        assert any("Seattle" in m.content for m in memories)
        
        # Turn 3: User shares hobby
        agent.add_conversation_turn("user", "I like hiking")
        agent.add_fact("User enjoys hiking", confidence=1.0, key="hobby")
        
        # Turn 4: Query requiring multiple contexts
        agent.add_conversation_turn("user", "Recommend weekend activities")
        memories = agent.retrieve("activities hiking Seattle")
        assert len(memories) >= 2
        
        # Turn 5: User shares dietary preference
        agent.add_conversation_turn("user", "Remember: I'm vegetarian")
        agent.add_fact("User is vegetarian", confidence=1.0, key="diet")
        
        # Turn 6: Restaurant recommendation
        agent.add_conversation_turn("user", "Suggest a restaurant")
        memories = agent.retrieve("restaurant vegetarian Seattle")
        assert len(memories) > 0
        
        # Turn 7: What do you know about me
        facts = agent.get_all_facts()
        assert len(facts) == 3
        fact_contents = [f.content for f in facts]
        assert "User lives in Seattle" in fact_contents
        assert "User enjoys hiking" in fact_contents
        assert "User is vegetarian" in fact_contents
        
        # Verify memory stats
        stats = agent.get_memory_stats()
        assert stats["long_term_count"] == 3
        assert stats["short_term_count"] >= 6  # Multiple conversation turns
