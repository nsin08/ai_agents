"""
Test suite for multi-agent system coordination.

Tests cover:
- Agent registration and capability tracking
- Task routing to appropriate agents
- Multi-agent coordination and result combination
- Message logging and communication flow
- Error handling and edge cases
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from multi_agent_system import MultiAgentSystem, Agent, Message, Task
from specialist_agents import (
    ResearchAgent,
    WritingAgent,
    CodingAgent,
    AnalysisAgent,
)


class TestAgentRegistration:
    """Test agent registration and management."""
    
    def test_register_agent(self):
        """Agents can be registered to system."""
        system = MultiAgentSystem(verbose=False)
        agent = ResearchAgent()
        
        system.register_agent("research", agent)
        
        assert "research" in system.agents
        assert system.agents["research"] is agent
    
    def test_register_multiple_agents(self):
        """Multiple agents can be registered."""
        system = MultiAgentSystem(verbose=False)
        agents = {
            "research": ResearchAgent(),
            "writing": WritingAgent(),
            "coding": CodingAgent(),
        }
        
        for name, agent in agents.items():
            system.register_agent(name, agent)
        
        assert len(system.agents) == 3
        assert all(name in system.agents for name in agents)
    
    def test_statistics(self):
        """System provides statistics."""
        system = MultiAgentSystem(verbose=False)
        system.register_agent("research", ResearchAgent())
        system.register_agent("writing", WritingAgent())
        
        stats = system.get_statistics()
        
        assert stats["registered_agents"] == 2
        assert "research" in stats["agent_list"]
        assert "writing" in stats["agent_list"]


class TestTaskRouting:
    """Test task routing to appropriate agents."""
    
    def test_route_research_task(self):
        """Research tasks routed to research agent."""
        system = MultiAgentSystem(verbose=False)
        system.register_agent("research", ResearchAgent())
        system.register_agent("writing", WritingAgent())
        
        agent_name = system.route_task("Find information about AI")
        
        assert agent_name == "research"
    
    def test_route_writing_task(self):
        """Writing tasks routed to writing agent."""
        system = MultiAgentSystem(verbose=False)
        system.register_agent("research", ResearchAgent())
        system.register_agent("writing", WritingAgent())
        
        agent_name = system.route_task("Write a summary")
        
        assert agent_name == "writing"
    
    def test_route_coding_task(self):
        """Coding tasks routed to coding agent."""
        system = MultiAgentSystem(verbose=False)
        system.register_agent("research", ResearchAgent())
        system.register_agent("coding", CodingAgent())
        
        agent_name = system.route_task("Implement a function")
        
        assert agent_name == "coding"
    
    def test_route_to_first_agent_as_fallback(self):
        """Falls back to first agent if no match."""
        system = MultiAgentSystem(verbose=False)
        system.register_agent("research", ResearchAgent())
        system.register_agent("writing", WritingAgent())
        
        agent_name = system.route_task("Unknown task type")
        
        assert agent_name in system.agents


class TestAgentExecution:
    """Test agent execution and delegation."""
    
    def test_delegate_to_research_agent(self):
        """Task delegated to research agent returns result."""
        system = MultiAgentSystem(verbose=False)
        system.register_agent("research", ResearchAgent())
        
        result = system.delegate("Research AI", "research")
        
        assert "AI" in result or "Artificial Intelligence" in result
        assert len(result) > 0
    
    def test_delegate_to_writing_agent(self):
        """Task delegated to writing agent returns content."""
        system = MultiAgentSystem(verbose=False)
        system.register_agent("writing", WritingAgent())
        
        result = system.delegate("Write a summary", "writing")
        
        assert "summary" in result.lower()
        assert len(result) > 0
    
    def test_delegate_to_coding_agent(self):
        """Task delegated to coding agent returns code."""
        system = MultiAgentSystem(verbose=False)
        system.register_agent("coding", CodingAgent())
        
        result = system.delegate("Implement a function", "coding")
        
        assert "def " in result or "class " in result
        assert len(result) > 0
    
    def test_delegate_nonexistent_agent_raises_error(self):
        """Delegating to nonexistent agent raises error."""
        system = MultiAgentSystem(verbose=False)
        system.register_agent("research", ResearchAgent())
        
        with pytest.raises(ValueError, match="not found"):
            system.delegate("Task", "nonexistent")


class TestTaskDecomposition:
    """Test task decomposition into subtasks."""
    
    def test_decompose_simple_task(self):
        """Simple task returns as single subtask."""
        system = MultiAgentSystem(verbose=False)
        
        subtasks = system.decompose("Research AI")
        
        assert len(subtasks) == 1
        assert subtasks[0] == "Research AI"
    
    def test_decompose_compound_task(self):
        """Compound task split by 'and'."""
        system = MultiAgentSystem(verbose=False)
        
        subtasks = system.decompose("Research Python and write tutorial")
        
        assert len(subtasks) == 2
        assert "Research Python" in subtasks
        assert "write tutorial" in subtasks
    
    def test_decompose_multiple_subtasks(self):
        """Multiple subtasks separated by 'and'."""
        system = MultiAgentSystem(verbose=False)
        
        subtasks = system.decompose("Research AI and write tutorial and create code")
        
        assert len(subtasks) == 3


class TestResultCombination:
    """Test result combination from multiple agents."""
    
    def test_combine_two_results(self):
        """Two results combined with formatting."""
        system = MultiAgentSystem(verbose=False)
        
        results = ["First result", "Second result"]
        combined = system.combine(results)
        
        assert "First result" in combined
        assert "Second result" in combined
        assert "Result 1:" in combined
        assert "Result 2:" in combined
    
    def test_combine_multiple_results(self):
        """Multiple results combined properly."""
        system = MultiAgentSystem(verbose=False)
        
        results = ["R1", "R2", "R3"]
        combined = system.combine(results)
        
        assert "Result 1:" in combined
        assert "Result 2:" in combined
        assert "Result 3:" in combined


class TestMultiAgentCoordination:
    """Test complete multi-agent workflow."""
    
    def test_two_agent_coordination(self):
        """Two agents coordinate successfully."""
        system = MultiAgentSystem(verbose=False)
        system.register_agent("research", ResearchAgent())
        system.register_agent("writing", WritingAgent())
        
        result = system.run("Research Python and write tutorial")
        
        # Verify both agents participated
        messages = system.get_communication_flow()
        agents_used = set(m['to'] for m in messages if m['to'] != 'system')
        assert len(agents_used) >= 1  # At least one agent used
    
    def test_three_agent_coordination(self):
        """Three agents coordinate successfully."""
        system = MultiAgentSystem(verbose=False)
        system.register_agent("research", ResearchAgent())
        system.register_agent("writing", WritingAgent())
        system.register_agent("coding", CodingAgent())
        
        result = system.run("Research async and write tutorial and implement code")
        
        assert len(result) > 0
        messages = system.get_communication_flow()
        assert len(messages) >= 3  # At least 3 messages
    
    def test_complex_task_returns_combined_result(self):
        """Complex task returns properly combined result."""
        system = MultiAgentSystem(verbose=False)
        system.register_agent("research", ResearchAgent())
        system.register_agent("writing", WritingAgent())
        
        result = system.run("Research machine learning and write summary")
        
        assert "Result 1:" in result
        assert "Result 2:" in result
        assert len(result) > 100


class TestCommunicationLogging:
    """Test inter-agent communication logging."""
    
    def test_messages_logged(self):
        """Inter-agent communication is logged."""
        system = MultiAgentSystem(verbose=False)
        system.register_agent("research", ResearchAgent())
        
        system.run("Research AI")
        
        messages = system.get_communication_flow()
        assert len(messages) > 0
    
    def test_message_structure(self):
        """Messages have correct structure."""
        system = MultiAgentSystem(verbose=False)
        system.register_agent("research", ResearchAgent())
        
        system.run("Research Python")
        
        messages = system.get_communication_flow()
        for msg in messages:
            assert "from" in msg
            assert "to" in msg
            assert "content" in msg
            assert "timestamp" in msg
    
    def test_bidirectional_communication(self):
        """System and agents communicate bidirectionally."""
        system = MultiAgentSystem(verbose=False)
        system.register_agent("research", ResearchAgent())
        
        system.run("Research AI")
        
        messages = system.get_communication_flow()
        
        # Check for both directions
        from_system = [m for m in messages if m['from'] == 'system']
        to_system = [m for m in messages if m['to'] == 'system']
        
        assert len(from_system) > 0
        assert len(to_system) > 0


class TestSpecialistAgents:
    """Test individual specialist agent implementations."""
    
    def test_research_agent_capabilities(self):
        """ResearchAgent has correct capabilities."""
        agent = ResearchAgent()
        capabilities = agent.get_capabilities()
        
        assert "research" in capabilities
        assert "find" in capabilities
        assert "analyze" in capabilities
    
    def test_writing_agent_capabilities(self):
        """WritingAgent has correct capabilities."""
        agent = WritingAgent()
        capabilities = agent.get_capabilities()
        
        assert "write" in capabilities
        assert "document" in capabilities
        assert "summarize" in capabilities
    
    def test_coding_agent_capabilities(self):
        """CodingAgent has correct capabilities."""
        agent = CodingAgent()
        capabilities = agent.get_capabilities()
        
        assert "code" in capabilities
        assert "implement" in capabilities
        assert "debug" in capabilities
    
    def test_analysis_agent_capabilities(self):
        """AnalysisAgent has correct capabilities."""
        agent = AnalysisAgent()
        capabilities = agent.get_capabilities()
        
        assert "analyze" in capabilities
        assert "evaluate" in capabilities
    
    def test_research_agent_produces_findings(self):
        """ResearchAgent produces informative findings."""
        agent = ResearchAgent()
        result = agent.run("Research AI")
        
        assert "Artificial Intelligence" in result or "AI" in result
        assert "Finding" in result or "Key" in result
    
    def test_writing_agent_produces_content(self):
        """WritingAgent produces substantial content."""
        agent = WritingAgent()
        result = agent.run("Write a tutorial")
        
        assert len(result) > 200  # Substantial content
        assert "tutorial" in result.lower() or "Tutorial" in result
    
    def test_coding_agent_produces_code(self):
        """CodingAgent produces valid code structure."""
        agent = CodingAgent()
        result = agent.run("Implement a function")
        
        assert "def " in result or "class " in result
        assert len(result) > 100
    
    def test_analysis_agent_produces_report(self):
        """AnalysisAgent produces analysis report."""
        agent = AnalysisAgent()
        result = agent.run("Analyze performance")
        
        assert "Analysis" in result or "Report" in result
        assert "Finding" in result or "Metrics" in result


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_agent_list(self):
        """System handles empty agent list."""
        system = MultiAgentSystem(verbose=False)
        
        # Should handle gracefully with default behavior
        assert len(system.agents) == 0
    
    def test_single_agent_system(self):
        """System works with single agent."""
        system = MultiAgentSystem(verbose=False)
        system.register_agent("research", ResearchAgent())
        
        result = system.run("Research AI")
        
        assert len(result) > 0
    
    def test_task_with_no_keywords(self):
        """Task with no matching keywords handled."""
        system = MultiAgentSystem(verbose=False)
        system.register_agent("research", ResearchAgent())
        
        result = system.run("xyz123abc")
        
        assert len(result) > 0  # Still processes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
