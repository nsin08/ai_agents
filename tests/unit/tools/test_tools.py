"""
Tests for the tools module - Tool ABC, ToolResult, and ToolRegistry.

This module tests:
1. Tool ABC interface (abstract methods)
2. ToolResult dataclass (structure and validation)
3. ToolRegistry (registration, retrieval, execution)
4. MockTool implementation (for testing)
"""

import pytest
from typing import Any, Dict, Optional

# Tests will import from src.agent_labs.tools
# Using TYPE_CHECKING to avoid circular imports during test collection
from src.agent_labs.tools import Tool, ToolResult, ToolRegistry, MockTool


class TestToolResult:
    """Tests for ToolResult dataclass."""

    def test_tool_result_success_creation(self):
        """Test creating a successful ToolResult."""
        result = ToolResult(success=True, output="test output", error=None)
        assert result.success is True
        assert result.output == "test output"
        assert result.error is None

    def test_tool_result_failure_creation(self):
        """Test creating a failed ToolResult with error."""
        result = ToolResult(success=False, output=None, error="Tool failed")
        assert result.success is False
        assert result.output is None
        assert result.error == "Tool failed"

    def test_tool_result_with_complex_output(self):
        """Test ToolResult with complex output type."""
        output = {"key": "value", "count": 42, "items": [1, 2, 3]}
        result = ToolResult(success=True, output=output, error=None)
        assert result.output == output
        assert result.output["count"] == 42

    def test_tool_result_with_none_output(self):
        """Test ToolResult with None output (tool did nothing)."""
        result = ToolResult(success=True, output=None, error=None)
        assert result.success is True
        assert result.output is None


class TestToolInterface:
    """Tests for Tool ABC interface."""

    def test_tool_has_execute_method(self):
        """Test that Tool ABC has execute method."""
        assert hasattr(Tool, 'execute')
        assert callable(getattr(Tool, 'execute'))

    def test_tool_has_get_schema_method(self):
        """Test that Tool ABC has get_schema method."""
        assert hasattr(Tool, 'get_schema')
        assert callable(getattr(Tool, 'get_schema'))

    def test_tool_cannot_be_instantiated_directly(self):
        """Test that Tool ABC cannot be instantiated."""
        with pytest.raises(TypeError):
            Tool()


class TestMockTool:
    """Tests for MockTool implementation."""

    @pytest.mark.asyncio
    async def test_mock_tool_execute_returns_success(self):
        """Test MockTool execute returns successful ToolResult."""
        tool = MockTool(name="test_tool")
        result = await tool.execute(param="test_value")
        
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert result.error is None

    @pytest.mark.asyncio
    async def test_mock_tool_execute_output_format(self):
        """Test MockTool execute output has expected format."""
        tool = MockTool(name="test_tool")
        result = await tool.execute(param="test_value")
        
        assert result.output is not None
        assert isinstance(result.output, dict)
        assert "tool_name" in result.output
        assert "input" in result.output
        assert result.output["tool_name"] == "test_tool"

    @pytest.mark.asyncio
    async def test_mock_tool_execute_with_kwargs(self):
        """Test MockTool execute with multiple keyword arguments."""
        tool = MockTool(name="test_tool")
        result = await tool.execute(param1="value1", param2="value2", count=42)
        
        assert result.success is True
        assert result.output["input"]["param1"] == "value1"
        assert result.output["input"]["param2"] == "value2"

    def test_mock_tool_get_schema_returns_dict(self):
        """Test MockTool get_schema returns schema dictionary."""
        tool = MockTool(name="test_tool")
        schema = tool.get_schema()
        
        assert isinstance(schema, dict)
        assert "name" in schema
        assert "description" in schema
        assert schema["name"] == "test_tool"

    def test_mock_tool_get_schema_has_parameters(self):
        """Test MockTool schema has parameters field."""
        tool = MockTool(name="test_tool")
        schema = tool.get_schema()
        
        assert "parameters" in schema
        assert isinstance(schema["parameters"], dict)

    def test_mock_tool_name_stored_correctly(self):
        """Test MockTool stores name correctly."""
        tool = MockTool(name="my_tool")
        assert tool.name == "my_tool"


class TestToolRegistry:
    """Tests for ToolRegistry."""

    def test_tool_registry_creation(self):
        """Test creating an empty ToolRegistry."""
        registry = ToolRegistry()
        assert registry is not None

    def test_tool_registry_register_single_tool(self):
        """Test registering a single tool."""
        registry = ToolRegistry()
        tool = MockTool(name="tool1")
        
        registry.register(tool)
        # If no exception, registration was successful
        assert True

    def test_tool_registry_register_multiple_tools(self):
        """Test registering multiple tools."""
        registry = ToolRegistry()
        tool1 = MockTool(name="tool1")
        tool2 = MockTool(name="tool2")
        tool3 = MockTool(name="tool3")
        
        registry.register(tool1)
        registry.register(tool2)
        registry.register(tool3)
        # If no exception, all registrations were successful
        assert True

    def test_tool_registry_get_registered_tool(self):
        """Test retrieving a registered tool."""
        registry = ToolRegistry()
        tool = MockTool(name="my_tool")
        registry.register(tool)
        
        retrieved = registry.get("my_tool")
        assert retrieved is not None
        assert retrieved.name == "my_tool"

    def test_tool_registry_get_nonexistent_tool_returns_none(self):
        """Test getting a non-existent tool returns None."""
        registry = ToolRegistry()
        
        retrieved = registry.get("nonexistent")
        assert retrieved is None

    def test_tool_registry_get_multiple_tools(self):
        """Test retrieving multiple different tools."""
        registry = ToolRegistry()
        tool1 = MockTool(name="tool1")
        tool2 = MockTool(name="tool2")
        
        registry.register(tool1)
        registry.register(tool2)
        
        assert registry.get("tool1").name == "tool1"
        assert registry.get("tool2").name == "tool2"

    @pytest.mark.asyncio
    async def test_tool_registry_execute_returns_tool_result(self):
        """Test executing a tool through registry returns ToolResult."""
        registry = ToolRegistry()
        tool = MockTool(name="test_tool")
        registry.register(tool)
        
        result = await registry.execute("test_tool", param="value")
        
        assert isinstance(result, ToolResult)
        assert result.success is True

    @pytest.mark.asyncio
    async def test_tool_registry_execute_nonexistent_tool_fails(self):
        """Test executing non-existent tool returns failed result."""
        registry = ToolRegistry()
        
        result = await registry.execute("nonexistent", param="value")
        
        assert isinstance(result, ToolResult)
        assert result.success is False
        assert result.error is not None

    @pytest.mark.asyncio
    async def test_tool_registry_execute_with_kwargs(self):
        """Test registry execute with multiple keyword arguments."""
        registry = ToolRegistry()
        tool = MockTool(name="test_tool")
        registry.register(tool)
        
        result = await registry.execute(
            "test_tool",
            param1="value1",
            param2="value2",
            count=42
        )
        
        assert result.success is True
        assert result.output["input"]["param1"] == "value1"

    def test_tool_registry_list_tools(self):
        """Test listing all registered tools."""
        registry = ToolRegistry()
        tool1 = MockTool(name="tool1")
        tool2 = MockTool(name="tool2")
        
        registry.register(tool1)
        registry.register(tool2)
        
        tools = registry.list_tools()
        assert len(tools) == 2
        assert "tool1" in tools
        assert "tool2" in tools

    def test_tool_registry_list_empty_registry(self):
        """Test listing tools in empty registry."""
        registry = ToolRegistry()
        
        tools = registry.list_tools()
        assert len(tools) == 0
        assert tools == []

    @pytest.mark.asyncio
    async def test_tool_registry_integration_workflow(self):
        """Test complete workflow: register multiple tools and execute."""
        registry = ToolRegistry()
        
        # Register tools
        calculator = MockTool(name="calculator")
        search = MockTool(name="search")
        registry.register(calculator)
        registry.register(search)
        
        # List tools
        tools = registry.list_tools()
        assert len(tools) == 2
        
        # Execute tools
        calc_result = await registry.execute("calculator", expression="2+2")
        search_result = await registry.execute("search", query="test")
        
        assert calc_result.success is True
        assert search_result.success is True

    def test_tool_registry_duplicate_registration_overwrites(self):
        """Test that registering same tool name overwrites previous."""
        registry = ToolRegistry()
        tool1 = MockTool(name="tool")
        tool2 = MockTool(name="tool")
        
        registry.register(tool1)
        registry.register(tool2)
        
        # Should have only one tool with that name
        tools = registry.list_tools()
        assert len(tools) == 1


class TestToolEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_tool_execute_with_no_parameters(self):
        """Test executing tool with no parameters."""
        tool = MockTool(name="test_tool")
        result = await tool.execute()
        
        assert result.success is True

    def test_tool_schema_has_correct_structure(self):
        """Test tool schema has all required fields."""
        tool = MockTool(name="test_tool")
        schema = tool.get_schema()
        
        required_fields = ["name", "description", "parameters"]
        for field in required_fields:
            assert field in schema

    def test_tool_registry_get_returns_same_instance(self):
        """Test that registry.get() returns the same tool instance."""
        registry = ToolRegistry()
        tool = MockTool(name="tool")
        registry.register(tool)
        
        retrieved1 = registry.get("tool")
        retrieved2 = registry.get("tool")
        
        assert retrieved1 is retrieved2

    def test_tool_registry_register_tool_without_name_raises_error(self):
        """Test registering tool without name attribute raises AttributeError."""
        registry = ToolRegistry()
        
        class BadTool:
            pass
        
        with pytest.raises(AttributeError):
            registry.register(BadTool())

    @pytest.mark.asyncio
    async def test_tool_registry_execute_tool_exception_handling(self):
        """Test registry handles tool execution exceptions gracefully."""
        registry = ToolRegistry()
        
        class FailingTool(Tool):
            def __init__(self):
                self.name = "failing_tool"
            
            async def execute(self, **kwargs):
                raise ValueError("Tool error")
            
            def get_schema(self):
                return {"name": "failing_tool"}
        
        registry.register(FailingTool())
        result = await registry.execute("failing_tool")
        
        assert result.success is False
        assert "Error executing tool" in result.error

    @pytest.mark.asyncio
    async def test_mock_tool_deterministic_behavior(self):
        """Test MockTool produces deterministic output."""
        tool = MockTool(name="test_tool")
        
        result1 = await tool.execute(param="value")
        result2 = await tool.execute(param="value")
        
        assert result1.output == result2.output

    def test_mock_tool_schema_parameters_structure(self):
        """Test MockTool schema parameters have proper structure."""
        tool = MockTool(name="test_tool")
        schema = tool.get_schema()
        
        params = schema["parameters"]
        assert "type" in params
        assert params["type"] == "object"
        assert "properties" in params

    def test_tool_result_immutability_best_practice(self):
        """Test ToolResult dataclass structure."""
        result = ToolResult(success=True, output="test", error=None)
        
        # Verify dataclass fields
        assert hasattr(result, 'success')
        assert hasattr(result, 'output')
        assert hasattr(result, 'error')

    @pytest.mark.asyncio
    async def test_mock_tool_preserves_all_kwargs(self):
        """Test MockTool preserves all kwargs in output."""
        tool = MockTool(name="test_tool")
        kwargs = {
            "string": "value",
            "number": 42,
            "float": 3.14,
            "bool": True,
            "list": [1, 2, 3]
        }
        
        result = await tool.execute(**kwargs)
        
        for key, value in kwargs.items():
            assert result.output["input"][key] == value

    def test_tool_registry_operations_sequence(self):
        """Test complete registry operations sequence."""
        registry = ToolRegistry()
        assert len(registry.list_tools()) == 0
        
        tool1 = MockTool(name="tool1")
        tool2 = MockTool(name="tool2")
        
        registry.register(tool1)
        assert len(registry.list_tools()) == 1
        assert registry.get("tool1") is not None
        
        registry.register(tool2)
        assert len(registry.list_tools()) == 2
        assert registry.get("tool1") is not None
        assert registry.get("tool2") is not None
