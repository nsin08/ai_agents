"""
Tool Registry - Tool management and execution with validation.

This module provides:
1. ToolRegistry - Central registry for tool registration and execution
2. Input validation before tool execution
3. Error handling and result formatting
"""

import time
from typing import Dict, List, Optional
from .base import Tool
from .contract import ToolResult, ExecutionStatus
from .validators import ToolInputValidator


class ToolRegistry:
    """Registry for managing and executing tools with validation.
    
    The ToolRegistry:
    - Stores registered tools
    - Validates inputs against tool schemas before execution
    - Provides tool lookup by name
    - Executes tools with error handling
    - Tracks execution metadata
    
    Example:
        >>> registry = ToolRegistry()
        >>> calculator = Calculator()
        >>> registry.register(calculator)
        >>> result = await registry.execute("calculator", operation="add", a=5, b=3)
        >>> assert result.success
        >>> assert result.output == 8.0
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
    
    def unregister(self, name: str) -> bool:
        """Unregister a tool from the registry.
        
        Args:
            name: Tool name to unregister
            
        Returns:
            True if tool was removed, False if not found
        """
        if name in self._tools:
            del self._tools[name]
            return True
        return False
    
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
    
    def get_all_schemas(self) -> Dict[str, Dict]:
        """Get schemas for all registered tools.
        
        Returns:
            Dictionary mapping tool names to their schemas
        """
        return {name: tool.get_schema() for name, tool in self._tools.items()}
    
    async def execute(
        self,
        name: str,
        validate_input: bool = True,
        **kwargs
    ) -> ToolResult:
        """Execute a tool by name with optional input validation.
        
        Args:
            name: Name of tool to execute
            validate_input: Whether to validate inputs before execution (default: True)
            **kwargs: Parameters to pass to tool.execute()
            
        Returns:
            ToolResult with execution outcome, timing, and metadata
            
        Example:
            >>> result = await registry.execute(
            ...     "calculator",
            ...     operation="add",
            ...     a=5,
            ...     b=3
            ... )
            >>> print(result.output)  # 8.0
        """
        start_time = time.perf_counter()
        
        # Check if tool exists
        tool = self.get(name)
        
        if tool is None:
            return ToolResult(
                status=ExecutionStatus.NOT_FOUND,
                output=None,
                error=f"Tool '{name}' not found in registry. Available tools: {', '.join(self.list_tools())}",
                metadata={"tool_name": name, "available_tools": self.list_tools()},
                latency_ms=(time.perf_counter() - start_time) * 1000,
            )
        
        # Validate inputs if requested and tool has contract
        if validate_input and hasattr(tool, 'contract'):
            schema = tool.contract.input_schema
            
            # Try JSON schema validation
            is_valid, validated_data, error = ToolInputValidator.validate_with_json_schema(
                kwargs, schema
            )
            
            if not is_valid:
                return ToolResult(
                    status=ExecutionStatus.INVALID_INPUT,
                    output=None,
                    error=f"Input validation failed for '{name}': {error}",
                    metadata={
                        "tool_name": name,
                        "validation_error": error,
                        "provided_inputs": list(kwargs.keys()),
                    },
                    latency_ms=(time.perf_counter() - start_time) * 1000,
                )
        
        # Execute tool
        try:
            result = await tool.execute(**kwargs)
            return result
            
        except Exception as e:
            return ToolResult(
                status=ExecutionStatus.FAILURE,
                output=None,
                error=f"Error executing tool '{name}': {str(e)}",
                metadata={
                    "tool_name": name,
                    "exception_type": type(e).__name__,
                },
                latency_ms=(time.perf_counter() - start_time) * 1000,
            )
    
    async def execute_batch(
        self,
        operations: List[Dict[str, any]]
    ) -> List[ToolResult]:
        """Execute multiple tool operations in sequence.
        
        Args:
            operations: List of dicts with 'tool' and 'params' keys
            
        Returns:
            List of ToolResults for each operation
            
        Example:
            >>> operations = [
            ...     {"tool": "calculator", "params": {"operation": "add", "a": 5, "b": 3}},
            ...     {"tool": "calculator", "params": {"operation": "multiply", "a": 2, "b": 4}}
            ... ]
            >>> results = await registry.execute_batch(operations)
        """
        results = []
        for op in operations:
            tool_name = op.get("tool")
            params = op.get("params", {})
            
            if not tool_name:
                results.append(ToolResult(
                    status=ExecutionStatus.INVALID_INPUT,
                    error="Missing 'tool' field in operation",
                    metadata={"operation": op},
                ))
                continue
            
            result = await self.execute(tool_name, **params)
            results.append(result)
        
        return results
    
    def clear(self) -> None:
        """Remove all tools from registry."""
        self._tools.clear()
    
    def __len__(self) -> int:
        """Get number of registered tools."""
        return len(self._tools)
    
    def __contains__(self, name: str) -> bool:
        """Check if tool is registered."""
        return name in self._tools
    
    def __repr__(self) -> str:
        """String representation of registry."""
        return f"ToolRegistry(tools={len(self._tools)}, names={list(self._tools.keys())})"
