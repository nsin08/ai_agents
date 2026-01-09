"""
Tools & Execution Framework - Tool abstractions and management.

This module provides:
1. Tool ABC - abstract base class for all tools
2. MockTool - deterministic tool implementation for testing

A Tool is a callable abstraction that:
- Has an async execute() method to perform work
- Has a get_schema() method to describe its interface
- Returns a ToolResult with success status and output

Note: ToolResult is now in contract.py
Note: ToolRegistry is now in registry.py
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
from .contract import ToolResult, ExecutionStatus


class Tool(ABC):
    """Abstract base class for all tools.
    
    Tools are atomic actions that an agent can call to perform work.
    Each tool has:
    - A name
    - An async execute method that performs work
    - A schema describing its parameters
    """
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            ToolResult with success status and output
        """
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Get the schema describing this tool.
        
        Returns:
            Dictionary with:
            - name: Tool name
            - description: What the tool does
            - parameters: Dict of parameter definitions
        """
        pass


class MockTool(Tool):
    """Mock tool implementation for testing and development.
    
    Returns deterministic results for testing orchestration logic
    without external dependencies.
    """
    
    def __init__(self, name: str, description: str = "Mock tool for testing"):
        """Initialize MockTool.
        
        Args:
            name: Tool name
            description: Tool description
        """
        self.name = name
        self.description = description
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute mock tool - always succeeds with deterministic output.
        
        Args:
            **kwargs: Ignored, but accepted for interface compatibility
            
        Returns:
            ToolResult with success=True and structured output
        """
        output = {
            "tool_name": self.name,
            "input": kwargs,
            "status": "completed"
        }
        
        return ToolResult(
            status=ExecutionStatus.SUCCESS,
            output=output,
            metadata={"tool_name": self.name},
        )
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the schema for this mock tool.
        
        Returns:
            Schema with name, description, and generic parameters
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "input": {
                        "type": "string",
                        "description": "Input parameter (generic)"
                    }
                },
                "required": []
            }
        }
