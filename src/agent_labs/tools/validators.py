"""
Tool Input/Output Validation - Schema validation using Pydantic.

This module provides:
1. Pydantic-based input validators for tool parameters
2. Schema validation utilities
3. Type coercion and error formatting
"""

from typing import Any, Dict, Optional, Type
from pydantic import BaseModel, ValidationError, Field


class ToolInputValidator:
    """Validates tool inputs against Pydantic models or JSON schemas.
    
    Supports:
    - Pydantic BaseModel validation (preferred)
    - JSON Schema validation (fallback)
    - Type coercion and error formatting
    """
    
    @staticmethod
    def validate_with_pydantic(
        inputs: Dict[str, Any],
        model: Type[BaseModel]
    ) -> tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Validate inputs against a Pydantic model.
        
        Args:
            inputs: Input parameters to validate
            model: Pydantic BaseModel class defining the schema
            
        Returns:
            Tuple of (is_valid, validated_data, error_message)
            - is_valid: True if validation passed
            - validated_data: Validated and coerced data (None if invalid)
            - error_message: Error description (None if valid)
        
        Example:
            >>> class CalculatorInput(BaseModel):
            ...     operation: str
            ...     a: float
            ...     b: float
            >>> 
            >>> valid, data, error = ToolInputValidator.validate_with_pydantic(
            ...     {"operation": "add", "a": 5, "b": 3},
            ...     CalculatorInput
            ... )
            >>> assert valid is True
            >>> assert data["a"] == 5.0
        """
        try:
            validated = model(**inputs)
            return True, validated.model_dump(), None
        except ValidationError as e:
            error_msg = ToolInputValidator._format_validation_error(e)
            return False, None, error_msg
    
    @staticmethod
    def validate_with_json_schema(
        inputs: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Validate inputs against a JSON schema.
        
        Args:
            inputs: Input parameters to validate
            schema: JSON Schema dict
            
        Returns:
            Tuple of (is_valid, validated_data, error_message)
        
        Note:
            This is a simplified validator. For production use,
            consider jsonschema library for full JSON Schema support.
        """
        # Simplified JSON schema validation
        # Check required fields
        required = schema.get("required", [])
        missing = [field for field in required if field not in inputs]
        
        if missing:
            return False, None, f"Missing required fields: {', '.join(missing)}"
        
        # Basic type checking for properties
        properties = schema.get("properties", {})
        errors = []
        
        for field, value in inputs.items():
            if field in properties:
                field_schema = properties[field]
                expected_type = field_schema.get("type")
                
                # Basic type validation
                if expected_type == "string" and not isinstance(value, str):
                    errors.append(f"{field}: expected string, got {type(value).__name__}")
                elif expected_type == "number" and not isinstance(value, (int, float)):
                    errors.append(f"{field}: expected number, got {type(value).__name__}")
                elif expected_type == "integer" and not isinstance(value, int):
                    errors.append(f"{field}: expected integer, got {type(value).__name__}")
                elif expected_type == "boolean" and not isinstance(value, bool):
                    errors.append(f"{field}: expected boolean, got {type(value).__name__}")
                
                # Enum validation
                if "enum" in field_schema and value not in field_schema["enum"]:
                    errors.append(f"{field}: value must be one of {field_schema['enum']}")
        
        if errors:
            return False, None, "; ".join(errors)
        
        return True, inputs, None
    
    @staticmethod
    def _format_validation_error(error: ValidationError) -> str:
        """Format Pydantic ValidationError into readable message.
        
        Args:
            error: Pydantic ValidationError
            
        Returns:
            Formatted error string
        """
        errors = []
        for err in error.errors():
            field = ".".join(str(loc) for loc in err["loc"])
            msg = err["msg"]
            errors.append(f"{field}: {msg}")
        
        return "; ".join(errors)


# Common Pydantic models for built-in tools

class CalculatorInput(BaseModel):
    """Input schema for Calculator tool."""
    operation: str = Field(..., description="Arithmetic operation", pattern="^(add|subtract|multiply|divide)$")
    a: float = Field(..., description="First operand")
    b: float = Field(..., description="Second operand")


class WebSearchInput(BaseModel):
    """Input schema for WebSearch tool."""
    query: str = Field(..., description="Search query", min_length=1, max_length=500)
    max_results: int = Field(default=10, description="Maximum results to return", ge=1, le=100)
    language: Optional[str] = Field(default="en", description="Language code")


class FileReadInput(BaseModel):
    """Input schema for FileRead tool."""
    path: str = Field(..., description="File path to read", min_length=1)
    encoding: str = Field(default="utf-8", description="File encoding")
    max_size_bytes: int = Field(default=1048576, description="Maximum file size to read", ge=1, le=10485760)


class ToolOutputValidator:
    """Validates tool outputs against expected schemas."""
    
    @staticmethod
    def validate_output(
        output: Any,
        schema: Optional[Dict[str, Any]] = None
    ) -> tuple[bool, Optional[str]]:
        """Validate tool output against expected schema.
        
        Args:
            output: Output to validate
            schema: Expected output schema (optional)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if schema is None:
            # No schema specified, any output is valid
            return True, None
        
        # Basic type validation
        expected_type = schema.get("type")
        
        if expected_type == "string" and not isinstance(output, str):
            return False, f"Expected string output, got {type(output).__name__}"
        elif expected_type == "number" and not isinstance(output, (int, float)):
            return False, f"Expected number output, got {type(output).__name__}"
        elif expected_type == "object" and not isinstance(output, dict):
            return False, f"Expected object output, got {type(output).__name__}"
        elif expected_type == "array" and not isinstance(output, list):
            return False, f"Expected array output, got {type(output).__name__}"
        
        return True, None
