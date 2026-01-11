"""
Multi-Agent System - Coordinator and Router Pattern

This module implements a multi-agent coordination system where a central router
dispatches tasks to specialized agents based on task requirements.

Example:
    >>> system = MultiAgentSystem()
    >>> system.register_agent("research", ResearchAgent())
    >>> system.register_agent("writing", WritingAgent())
    >>> result = system.run("Research Python async and write tutorial")
    >>> print(result)
"""

from typing import Dict, List, Protocol, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Inter-agent communication message."""
    
    from_agent: str
    to_agent: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Task:
    """Task to be routed to agents."""
    
    description: str
    subtasks: List[str] = field(default_factory=list)
    required_capabilities: List[str] = field(default_factory=list)


class Agent(Protocol):
    """Interface for specialist agents."""
    
    def run(self, task: str) -> str:
        """Execute task and return result."""
        ...
    
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities."""
        ...


class MultiAgentSystem:
    """Coordinates multiple specialist agents.
    
    The system uses a router pattern:
    1. Receives complex task
    2. Decomposes into subtasks
    3. Routes each subtask to appropriate agent
    4. Collects and combines results
    """
    
    def __init__(self, verbose: bool = True):
        """Initialize multi-agent system.
        
        Args:
            verbose: Enable logging of system operations
        """
        self.agents: Dict[str, Agent] = {}
        self.message_log: List[Message] = []
        self.verbose = verbose
        
        if self.verbose:
            logger.setLevel(logging.DEBUG)
    
    def register_agent(self, name: str, agent: Agent) -> None:
        """Register a specialist agent with the system.
        
        Args:
            name: Unique identifier for the agent
            agent: Agent instance implementing Agent protocol
            
        Example:
            >>> system.register_agent("research", ResearchAgent())
        """
        self.agents[name] = agent
        self._log_message("system", name, f"Agent registered with capabilities: {agent.get_capabilities()}")
        if self.verbose:
            print(f"[System] Registered agent: {name}")
    
    def route_task(self, task: str) -> str:
        """Determine which agent should handle task based on capabilities.
        
        Uses simple keyword matching to score agent fit.
        
        Args:
            task: Task description to route
            
        Returns:
            Name of best-matching agent
        """
        task_keywords = set(task.lower().split())
        best_match = None
        best_score = 0
        
        for name, agent in self.agents.items():
            capabilities = agent.get_capabilities()
            # Score: number of capability keywords in task
            score = sum(1 for cap in capabilities if cap in task_keywords)
            if score > best_score:
                best_score = score
                best_match = name
        
        if not self.agents:
            raise ValueError("No agents registered. Register at least one agent before routing tasks.")
        return best_match or list(self.agents.keys())[0]
    
    def delegate(self, task: str, agent_name: str) -> str:
        """Send task to specific agent and collect result.
        
        Args:
            task: Task description
            agent_name: Name of agent to delegate to
            
        Returns:
            Agent's response/result
            
        Raises:
            ValueError: If agent not found
        """
        agent = self.agents.get(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found. Available: {list(self.agents.keys())}")
        
        # Log delegation
        self._log_message("system", agent_name, task)
        
        if self.verbose:
            print(f"\n[System] Delegating to {agent_name}: {task[:50]}...")
        
        # Execute
        try:
            result = agent.run(task)
            self._log_message(agent_name, "system", result)
            
            if self.verbose:
                print(f"[{agent_name}] Completed task")
            
            return result
        except Exception as e:
            error_msg = f"Error in {agent_name}: {str(e)}"
            self._log_message(agent_name, "system", error_msg)
            if self.verbose:
                print(f"[{agent_name}] Error: {error_msg}")
            raise
    
    def decompose(self, task: str) -> List[str]:
        """Break complex task into subtasks.
        
        Simple implementation: splits by " and "
        Can be enhanced with NLP or explicit task templates.
        
        Args:
            task: Complex task description
            
        Returns:
            List of subtasks
            
        Example:
            >>> system.decompose("Research Python and write tutorial")
            ['Research Python', 'write tutorial']
        """
        # Simple decomposition by "and"
        subtasks = [t.strip() for t in task.split(" and ")]
        return subtasks if len(subtasks) > 1 else [task]
    
    def combine(self, results: List[str]) -> str:
        """Merge subtask results into final output.
        
        Args:
            results: List of subtask results
            
        Returns:
            Combined final result
        """
        return "\n\n".join([f"Result {i+1}:\n{r}" for i, r in enumerate(results)])
    
    def run(self, task: str) -> str:
        """Execute task using multi-agent system.
        
        Workflow:
        1. Decompose task into subtasks
        2. Route each to appropriate agent
        3. Collect results
        4. Combine into final response
        
        Args:
            task: Main task description
            
        Returns:
            Combined result from all agents
            
        Example:
            >>> result = system.run("Research AI and write summary")
            >>> print(result)
        """
        if self.verbose:
            print(f"\n{'='*64}")
            print(f"Multi-Agent System - Task: {task}")
            print(f"{'='*64}\n")
        
        # Decompose into subtasks
        subtasks = self.decompose(task)
        if self.verbose:
            print(f"[System] Decomposed into {len(subtasks)} subtask(s)")
        
        results = []
        
        # Route and execute each subtask
        for i, subtask in enumerate(subtasks, 1):
            if self.verbose:
                print(f"\n[System] Subtask {i}/{len(subtasks)}: {subtask}")
            
            # Route to appropriate agent
            agent_name = self.route_task(subtask)
            if self.verbose:
                print(f"[System] -> Routing to: {agent_name}")
            
            # Delegate and collect result
            result = self.delegate(subtask, agent_name)
            results.append(result)
        
        # Combine results
        final_result = self.combine(results)
        
        if self.verbose:
            print(f"\n{'-'*64}")
            print(f"[System] Task complete!")
            print(f"{'-'*64}\n")
        
        return final_result
    
    def _log_message(self, from_agent: str, to_agent: str, content: str) -> None:
        """Record inter-agent communication.
        
        Args:
            from_agent: Source agent name
            to_agent: Destination agent name
            content: Message content
        """
        message = Message(
            from_agent=from_agent,
            to_agent=to_agent,
            content=content[:100] + "..." if len(content) > 100 else content
        )
        self.message_log.append(message)
    
    def get_communication_flow(self) -> List[Dict]:
        """Return full message log for visualization.
        
        Returns:
            List of message dictionaries with timestamps
        """
        return [
            {
                "from": msg.from_agent,
                "to": msg.to_agent,
                "content": msg.content,
                "timestamp": msg.timestamp
            }
            for msg in self.message_log
        ]
    
    def get_statistics(self) -> Dict:
        """Get system statistics.
        
        Returns:
            Dictionary with agent counts, message counts, etc.
        """
        return {
            "registered_agents": len(self.agents),
            "total_messages": len(self.message_log),
            "agent_list": list(self.agents.keys())
        }
