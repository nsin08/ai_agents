"""
Tools & Execution Framework - Tool abstractions and management.

This module provides:
1. Tool ABC - abstract base class for all tools
2. ToolResult - structured result from tool execution
3. ToolRegistry - manages registered tools and their execution
4. MockTool - deterministic tool implementation for testing

A Tool is a callable abstraction that:
- Has an async execute() method to perform work
- Has a get_schema() method to describe its interface
- Returns a ToolResult with success status and output
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ToolResult:
    """Result from executing a tool.
    
    Attributes:
        success: True if tool executed successfully
        output: Output from the tool (None if failed or no output)
        error: Error message if tool failed (None if successful)
    """
    
    success: bool
    output: Optional[Any] = None
    error: Optional[str] = None


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
            success=True,
            output=output,
            error=None
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


class ToolRegistry:
    """Registry for managing and executing tools.
    
    The ToolRegistry:
    - Stores registered tools
    - Provides tool lookup by name
    - Executes tools by name with parameters
    - Lists available tools
    """
    
    def __init__(self):
        """Initialize empty tool registry."""
        self._tools: Dict[str, Tool] = {}
    
    def register(self, tool: Tool) -> None:
        """Register a tool in the registry.
        
        Args:
            tool: Tool instance to register (must have .name attribute)
            
        Raises:
            AttributeError: If tool doesn't have a name attribute
        """
        if not hasattr(tool, 'name'):
            raise AttributeError("Tool must have a 'name' attribute")
        
        self._tools[tool.name] = tool
    
    def get(self, name: str) -> Optional[Tool]:
        """Get a registered tool by name.
        
        Args:
            name: Tool name to retrieve
            
        Returns:
            Tool instance if found, None otherwise
        """
        return self._tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names.
        
        Returns:
            List of tool names in registry
        """
        return list(self._tools.keys())
    
    async def execute(self, name: str, **kwargs) -> ToolResult:
        """Execute a tool by name with given parameters.
        
        Args:
            name: Name of tool to execute
            **kwargs: Parameters to pass to tool.execute()
            
        Returns:
            ToolResult from the tool, or failed result if tool not found
        """
        tool = self.get(name)
        
        if tool is None:
            return ToolResult(
                success=False,
                output=None,
                error=f"Tool '{name}' not found in registry"
            )
        
        try:
            return await tool.execute(**kwargs)
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error=f"Error executing tool '{name}': {str(e)}"
            )
