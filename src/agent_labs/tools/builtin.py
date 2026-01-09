"""
Built-in Tools - Example tool implementations.

This module provides:
1. Calculator - Arithmetic operations (add, subtract, multiply, divide)
2. WebSearch - Mock web search (for testing, no real HTTP)
3. FileRead - Sandboxed file reading with security constraints
"""

import time
from pathlib import Path
from typing import Any, Dict, Optional
from .base import Tool
from .contract import ToolContract, ToolResult, ExecutionStatus
from .validators import CalculatorInput, WebSearchInput, FileReadInput, ToolInputValidator


class Calculator(Tool):
    """Calculator tool for arithmetic operations.
    
    Supports: add, subtract, multiply, divide
    Input validation ensures proper types and operation names.
    
    Example:
        >>> calc = Calculator()
        >>> result = await calc.execute(operation="add", a=5, b=3)
        >>> assert result.output == 8.0
    """
    
    def __init__(self):
        """Initialize Calculator tool."""
        self.name = "calculator"
        self.input_model = CalculatorInput
        self.contract = ToolContract(
            name="calculator",
            description="Perform arithmetic operations (add, subtract, multiply, divide)",
            input_schema={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"],
                        "description": "Arithmetic operation to perform"
                    },
                    "a": {"type": "number", "description": "First operand"},
                    "b": {"type": "number", "description": "Second operand"}
                },
                "required": ["operation", "a", "b"]
            },
            output_schema={"type": "number"},
            tags=["math", "arithmetic", "builtin"],
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute arithmetic operation.
        
        Args:
            operation: One of "add", "subtract", "multiply", "divide"
            a: First number
            b: Second number
            
        Returns:
            ToolResult with numeric output or error
        """
        start_time = time.perf_counter()
        
        # Validate inputs
        is_valid, validated_data, error = ToolInputValidator.validate_with_pydantic(
            kwargs, CalculatorInput
        )
        
        if not is_valid:
            return ToolResult(
                status=ExecutionStatus.INVALID_INPUT,
                error=f"Invalid input: {error}",
                metadata={"tool_name": self.name},
                latency_ms=(time.perf_counter() - start_time) * 1000,
            )
        
        operation = validated_data["operation"]
        a = validated_data["a"]
        b = validated_data["b"]
        
        try:
            # Perform operation
            if operation == "add":
                result = a + b
            elif operation == "subtract":
                result = a - b
            elif operation == "multiply":
                result = a * b
            elif operation == "divide":
                if b == 0:
                    return ToolResult(
                        status=ExecutionStatus.FAILURE,
                        error="Division by zero",
                        metadata={"tool_name": self.name, "operation": operation},
                        latency_ms=(time.perf_counter() - start_time) * 1000,
                    )
                result = a / b
            else:
                return ToolResult(
                    status=ExecutionStatus.FAILURE,
                    error=f"Unknown operation: {operation}",
                    metadata={"tool_name": self.name},
                    latency_ms=(time.perf_counter() - start_time) * 1000,
                )
            
            latency = (time.perf_counter() - start_time) * 1000
            
            return ToolResult(
                status=ExecutionStatus.SUCCESS,
                output=result,
                metadata={
                    "tool_name": self.name,
                    "operation": operation,
                    "operands": {"a": a, "b": b},
                },
                latency_ms=latency,
            )
            
        except Exception as e:
            return ToolResult(
                status=ExecutionStatus.FAILURE,
                error=f"Execution error: {str(e)}",
                metadata={"tool_name": self.name, "operation": operation},
                latency_ms=(time.perf_counter() - start_time) * 1000,
            )
    
    def get_schema(self) -> Dict[str, Any]:
        """Get calculator tool schema.
        
        Returns:
            Schema dictionary compatible with ToolContract
        """
        return self.contract.to_dict()


class WebSearch(Tool):
    """Mock web search tool for testing.
    
    Returns mock search results without making real HTTP requests.
    Useful for development and testing agent workflows.
    
    Example:
        >>> search = WebSearch()
        >>> result = await search.execute(query="python tutorials", max_results=5)
        >>> assert result.success
        >>> assert len(result.output["results"]) == 5
    """
    
    def __init__(self):
        """Initialize WebSearch tool."""
        self.name = "web_search"
        self.input_model = WebSearchInput
        self.contract = ToolContract(
            name="web_search",
            description="Search the web and return results (mock implementation)",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query",
                        "minLength": 1,
                        "maxLength": 500
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum results to return",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 100
                    },
                    "language": {
                        "type": "string",
                        "description": "Language code",
                        "default": "en"
                    }
                },
                "required": ["query"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "results": {"type": "array"},
                    "total_results": {"type": "integer"}
                }
            },
            tags=["web", "search", "mock", "builtin"],
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute mock web search.
        
        Args:
            query: Search query string
            max_results: Maximum number of results (default: 10)
            language: Language code (default: "en")
            
        Returns:
            ToolResult with mock search results
        """
        start_time = time.perf_counter()
        
        # Validate inputs
        is_valid, validated_data, error = ToolInputValidator.validate_with_pydantic(
            kwargs, WebSearchInput
        )
        
        if not is_valid:
            return ToolResult(
                status=ExecutionStatus.INVALID_INPUT,
                error=f"Invalid input: {error}",
                metadata={"tool_name": self.name},
                latency_ms=(time.perf_counter() - start_time) * 1000,
            )
        
        query = validated_data["query"]
        max_results = validated_data["max_results"]
        language = validated_data["language"]
        
        # Generate mock results
        results = []
        for i in range(min(max_results, 10)):
            results.append({
                "title": f"Result {i+1} for '{query}'",
                "url": f"https://example.com/result-{i+1}",
                "snippet": f"This is a mock search result snippet for query '{query}'. Result number {i+1}.",
                "rank": i + 1,
            })
        
        latency = (time.perf_counter() - start_time) * 1000
        
        return ToolResult(
            status=ExecutionStatus.SUCCESS,
            output={
                "query": query,
                "results": results,
                "total_results": len(results),
                "language": language,
            },
            metadata={
                "tool_name": self.name,
                "query": query,
                "max_results": max_results,
                "is_mock": True,
            },
            latency_ms=latency,
        )
    
    def get_schema(self) -> Dict[str, Any]:
        """Get web search tool schema.
        
        Returns:
            Schema dictionary compatible with ToolContract
        """
        return self.contract.to_dict()


class FileRead(Tool):
    """Sandboxed file reading tool.
    
    Reads files with security constraints:
    - Only reads from allowed root directories
    - Enforces maximum file size
    - Handles binary and text files
    - Prevents path traversal attacks
    
    Example:
        >>> file_read = FileRead(allowed_roots=["/tmp/safe"])
        >>> result = await file_read.execute(path="/tmp/safe/data.txt")
        >>> assert result.success
        >>> assert "content" in result.output
    """
    
    def __init__(self, allowed_roots: Optional[list[str]] = None):
        """Initialize FileRead tool.
        
        Args:
            allowed_roots: List of allowed root directory paths.
                          If None, defaults to current directory only.
        """
        self.name = "file_read"
        self.input_model = FileReadInput
        self.allowed_roots = [Path(root).resolve() for root in (allowed_roots or ["."])]
        
        self.contract = ToolContract(
            name="file_read",
            description="Read file contents with sandbox security (allowed roots only)",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path to read",
                        "minLength": 1
                    },
                    "encoding": {
                        "type": "string",
                        "description": "File encoding",
                        "default": "utf-8"
                    },
                    "max_size_bytes": {
                        "type": "integer",
                        "description": "Maximum file size to read",
                        "default": 1048576,
                        "minimum": 1,
                        "maximum": 10485760
                    }
                },
                "required": ["path"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "size_bytes": {"type": "integer"},
                    "encoding": {"type": "string"},
                    "is_binary": {"type": "boolean"}
                }
            },
            tags=["file", "io", "sandboxed", "builtin"],
            constraints={
                "allowed_roots": [str(root) for root in self.allowed_roots],
                "max_file_size": 10485760,  # 10 MB
            }
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute sandboxed file read.
        
        Args:
            path: File path to read
            encoding: File encoding (default: "utf-8")
            max_size_bytes: Maximum file size (default: 1MB)
            
        Returns:
            ToolResult with file content or error
        """
        start_time = time.perf_counter()
        
        # Validate inputs
        is_valid, validated_data, error = ToolInputValidator.validate_with_pydantic(
            kwargs, FileReadInput
        )
        
        if not is_valid:
            return ToolResult(
                status=ExecutionStatus.INVALID_INPUT,
                error=f"Invalid input: {error}",
                metadata={"tool_name": self.name},
                latency_ms=(time.perf_counter() - start_time) * 1000,
            )
        
        file_path = validated_data["path"]
        encoding = validated_data["encoding"]
        max_size = validated_data["max_size_bytes"]
        
        try:
            # Resolve path and check if it's within allowed roots
            resolved_path = Path(file_path).resolve()
            
            # Security check: Ensure path is within allowed roots
            is_allowed = any(
                resolved_path.is_relative_to(root) or resolved_path == root
                for root in self.allowed_roots
            )
            
            if not is_allowed:
                return ToolResult(
                    status=ExecutionStatus.FAILURE,
                    error=f"Access denied: Path outside allowed roots. Allowed: {[str(r) for r in self.allowed_roots]}",
                    metadata={
                        "tool_name": self.name,
                        "path": str(resolved_path),
                        "security_violation": "path_traversal_attempt",
                    },
                    latency_ms=(time.perf_counter() - start_time) * 1000,
                )
            
            # Check if file exists
            if not resolved_path.exists():
                return ToolResult(
                    status=ExecutionStatus.FAILURE,
                    error=f"File not found: {file_path}",
                    metadata={"tool_name": self.name, "path": str(resolved_path)},
                    latency_ms=(time.perf_counter() - start_time) * 1000,
                )
            
            # Check file size
            file_size = resolved_path.stat().st_size
            if file_size > max_size:
                return ToolResult(
                    status=ExecutionStatus.FAILURE,
                    error=f"File too large: {file_size} bytes (max: {max_size})",
                    metadata={
                        "tool_name": self.name,
                        "path": str(resolved_path),
                        "file_size": file_size,
                        "max_size": max_size,
                    },
                    latency_ms=(time.perf_counter() - start_time) * 1000,
                )
            
            # Try to read as text first
            try:
                content = resolved_path.read_text(encoding=encoding)
                is_binary = False
            except (UnicodeDecodeError, LookupError):
                # If text reading fails, read as binary and encode to base64
                import base64
                content = base64.b64encode(resolved_path.read_bytes()).decode('ascii')
                is_binary = True
                encoding = "base64"
            
            latency = (time.perf_counter() - start_time) * 1000
            
            return ToolResult(
                status=ExecutionStatus.SUCCESS,
                output={
                    "content": content,
                    "size_bytes": file_size,
                    "encoding": encoding,
                    "is_binary": is_binary,
                    "path": str(resolved_path),
                },
                metadata={
                    "tool_name": self.name,
                    "path": str(resolved_path),
                    "encoding": encoding,
                },
                latency_ms=latency,
            )
            
        except Exception as e:
            return ToolResult(
                status=ExecutionStatus.FAILURE,
                error=f"File read error: {str(e)}",
                metadata={"tool_name": self.name, "path": file_path},
                latency_ms=(time.perf_counter() - start_time) * 1000,
            )
    
    def get_schema(self) -> Dict[str, Any]:
        """Get file read tool schema.
        
        Returns:
            Schema dictionary compatible with ToolContract
        """
        return self.contract.to_dict()
