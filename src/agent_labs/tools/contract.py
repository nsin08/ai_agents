"""
Tool Contract System - Schema definitions and execution results.

This module provides:
1. ToolContract - Schema definition for tools (name, description, parameters)
2. ExecutionStatus - Enum for tool execution outcomes
3. Enhanced ToolResult - Rich result with status, metadata, timing
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional
from datetime import datetime


class ExecutionStatus(Enum):
    """Status of tool execution.
    
    Values:
        SUCCESS - Tool executed successfully
        FAILURE - Tool failed with error
        TIMEOUT - Tool execution exceeded time limit
        INVALID_INPUT - Input validation failed
        NOT_FOUND - Tool not found in registry
    """
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    INVALID_INPUT = "invalid_input"
    NOT_FOUND = "not_found"


@dataclass
class ToolContract:
    """Contract defining a tool's interface and capabilities.
    
    A ToolContract specifies:
    - Tool name and description
    - Input schema (parameters, types, constraints)
    - Output schema (return type, structure)
    - Metadata (version, tags, constraints)
    
    Attributes:
        name: Unique tool identifier
        description: Human-readable description of what the tool does
        input_schema: JSON schema or Pydantic model defining input parameters
        output_schema: Expected output structure/type
        version: Tool version (semver)
        tags: Categorization tags (e.g., "math", "web", "file")
        constraints: Additional constraints (timeout, retry, rate limits)
    
    Example:
        >>> contract = ToolContract(
        ...     name="calculator",
        ...     description="Perform arithmetic operations",
        ...     input_schema={
        ...         "type": "object",
        ...         "properties": {
        ...             "operation": {"type": "string", "enum": ["add", "subtract"]},
        ...             "a": {"type": "number"},
        ...             "b": {"type": "number"}
        ...         },
        ...         "required": ["operation", "a", "b"]
        ...     },
        ...     output_schema={"type": "number"},
        ...     tags=["math", "arithmetic"]
        ... )
    """
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Optional[Dict[str, Any]] = None
    version: str = "1.0.0"
    tags: list[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert contract to dictionary representation.
        
        Returns:
            Dictionary with all contract fields
        """
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
            "parameters": self.input_schema,
            "output_schema": self.output_schema,
            "version": self.version,
            "tags": self.tags,
            "constraints": self.constraints,
        }


@dataclass
class ToolResult:
    """Enhanced result from tool execution.
    
    Provides comprehensive information about tool execution including:
    - Success/failure status
    - Output data or error message
    - Execution metadata (timing, retries, tool info)
    
    Attributes:
        status: Execution status (SUCCESS, FAILURE, TIMEOUT, etc.)
        output: Output data from successful execution (None if failed)
        error: Error message if execution failed (None if successful)
        metadata: Additional execution information
        latency_ms: Execution time in milliseconds
        retries: Number of retry attempts (0 if first attempt succeeded)
        timestamp: When the execution completed
    
    Example:
        >>> result = ToolResult(
        ...     status=ExecutionStatus.SUCCESS,
        ...     output={"result": 42},
        ...     metadata={"tool_name": "calculator", "operation": "add"},
        ...     latency_ms=15.3,
        ...     retries=0
        ... )
    """
    status: ExecutionStatus
    output: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    latency_ms: float = 0.0
    retries: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def success(self) -> bool:
        """Check if execution was successful.
        
        Returns:
            True if status is SUCCESS, False otherwise
        """
        return self.status == ExecutionStatus.SUCCESS
    
    @property
    def failed(self) -> bool:
        """Check if execution failed.
        
        Returns:
            True if status indicates failure, False otherwise
        """
        return self.status in (
            ExecutionStatus.FAILURE,
            ExecutionStatus.TIMEOUT,
            ExecutionStatus.INVALID_INPUT,
            ExecutionStatus.NOT_FOUND,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary representation.
        
        Returns:
            Dictionary with all result fields
        """
        return {
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "metadata": self.metadata,
            "latency_ms": self.latency_ms,
            "retries": self.retries,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
        }
