"""Tools & Execution Framework module.

Exports:
- Tool: Abstract base class for all tools
- ToolResult: Enhanced result dataclass with status, metadata, timing
- ExecutionStatus: Enum for tool execution outcomes
- ToolContract: Schema definition for tools
- ToolRegistry: Registry for managing and executing tools with validation
- ToolInputValidator: Input validation using Pydantic
- MockTool: Mock tool implementation for testing
- Calculator: Built-in arithmetic tool
- WebSearch: Built-in mock web search tool
- FileRead: Built-in sandboxed file reading tool
"""

from .base import Tool, MockTool
from .contract import ToolResult, ExecutionStatus, ToolContract
from .registry import ToolRegistry
from .validators import (
    ToolInputValidator,
    ToolOutputValidator,
    CalculatorInput,
    WebSearchInput,
    FileReadInput,
)
from .builtin import Calculator, WebSearch, FileRead

__all__ = [
    # Base classes
    "Tool",
    "MockTool",
    
    # Contracts and results
    "ToolContract",
    "ToolResult",
    "ExecutionStatus",
    
    # Registry
    "ToolRegistry",
    
    # Validators
    "ToolInputValidator",
    "ToolOutputValidator",
    "CalculatorInput",
    "WebSearchInput",
    "FileReadInput",
    
    # Built-in tools
    "Calculator",
    "WebSearch",
    "FileRead",
]

