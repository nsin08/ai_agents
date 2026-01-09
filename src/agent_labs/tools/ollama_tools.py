"""
Ollama-based tools that leverage LLM capabilities for text analysis and generation.

Tools in this module require a running Ollama instance.
Default: http://localhost:11434
"""

import time
import re
from typing import Optional, Dict, Any
from enum import Enum
import httpx

from .base import Tool
from .contract import ToolContract, ToolResult, ExecutionStatus
from ..config import Config


class OllamaConnectionError(Exception):
    """Raised when Ollama connection fails."""
    pass


class TextSummarizer(Tool):
    """Summarize text using Ollama LLM."""
    
    def __init__(
        self,
        ollama_url: str = None,
        model: str = None,
        max_tokens: int = 200,
        temperature: float = None,
        timeout: int = 30
    ):
        """
        Initialize TextSummarizer.
        
        Args:
            ollama_url: Ollama API endpoint (default: from Config.OLLAMA_BASE_URL)
            model: Model name (default: from Config.OLLAMA_MODEL)
            max_tokens: Maximum tokens in summary
            temperature: Temperature for generation (default: from Config.OLLAMA_TOOLS_TEMPERATURE)
            timeout: Request timeout in seconds
        """
        self.ollama_url = (ollama_url or Config.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or Config.OLLAMA_MODEL
        self.max_tokens = max_tokens
        self.temperature = temperature if temperature is not None else Config.OLLAMA_TOOLS_TEMPERATURE
        self.timeout = timeout
        
        self.contract = ToolContract(
            name="text_summarizer",
            description="Summarize text using Ollama LLM",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to summarize",
                        "minLength": 50
                    },
                    "max_length": {
                        "type": "integer",
                        "description": "Maximum summary length in words",
                        "minimum": 10,
                        "maximum": 1000,
                        "default": 100
                    }
                },
                "required": ["text"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "word_count": {"type": "integer"}
                }
            },
            version="1.0.0",
            tags=["nlp", "summarization", "llm"],
            constraints={
                "requires_ollama": True,
                "min_text_length": 50,
                "max_request_timeout": 30
            }
        )
    
    @property
    def name(self) -> str:
        return "text_summarizer"
    
    @property
    def description(self) -> str:
        return "Summarize text using Ollama LLM"
    
    async def execute(self, **kwargs) -> ToolResult:
        start = time.perf_counter()
        
        try:
            text = kwargs.get("text", "").strip()
            max_length = kwargs.get("max_length", 100)
            
            # Validate input
            if not text:
                return ToolResult(
                    status=ExecutionStatus.INVALID_INPUT,
                    output=None,
                    error="text: Ensure this value has at least 50 characters",
                    latency_ms=int((time.perf_counter() - start) * 1000)
                )
            
            if len(text) < 50:
                return ToolResult(
                    status=ExecutionStatus.INVALID_INPUT,
                    output=None,
                    error="text: Ensure this value has at least 50 characters",
                    latency_ms=int((time.perf_counter() - start) * 1000)
                )
            
            if not 10 <= max_length <= 1000:
                return ToolResult(
                    status=ExecutionStatus.INVALID_INPUT,
                    output=None,
                    error=f"max_length: Value must be between 10 and 1000, got {max_length}",
                    latency_ms=int((time.perf_counter() - start) * 1000)
                )
            
            # Call Ollama API
            prompt = f"""Summarize the following text in {max_length} words or less. 
Provide only the summary, no additional text.

Text: {text}

Summary:"""
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "temperature": self.temperature,
                        "num_predict": self.max_tokens
                    }
                )
            
            if response.status_code != 200:
                return ToolResult(
                    status=ExecutionStatus.FAILURE,
                    output=None,
                    error=f"Ollama API returned {response.status_code}",
                    metadata={"status_code": response.status_code},
                    latency_ms=int((time.perf_counter() - start) * 1000)
                )
            
            data = response.json()
            summary = data.get("response", "").strip()
            
            if not summary:
                return ToolResult(
                    status=ExecutionStatus.FAILURE,
                    output=None,
                    error="Ollama returned empty response",
                    latency_ms=int((time.perf_counter() - start) * 1000)
                )
            
            word_count = len(summary.split())
            
            return ToolResult(
                status=ExecutionStatus.SUCCESS,
                output={
                    "summary": summary,
                    "word_count": word_count
                },
                metadata={
                    "tool_name": self.name,
                    "model": self.model,
                    "input_length": len(text.split()),
                    "temperature": self.temperature
                },
                latency_ms=int((time.perf_counter() - start) * 1000)
            )
        
        except httpx.ConnectError:
            return ToolResult(
                status=ExecutionStatus.FAILURE,
                output=None,
                error=f"Cannot connect to Ollama at {self.ollama_url}",
                metadata={"error_type": "ConnectionError"},
                latency_ms=int((time.perf_counter() - start) * 1000)
            )
        
        except TimeoutError:
            return ToolResult(
                status=ExecutionStatus.TIMEOUT,
                output=None,
                error=f"Request timed out after {self.timeout}s",
                latency_ms=int((time.perf_counter() - start) * 1000)
            )
        
        except Exception as e:
            return ToolResult(
                status=ExecutionStatus.FAILURE,
                output=None,
                error=str(e),
                metadata={"exception_type": type(e).__name__},
                latency_ms=int((time.perf_counter() - start) * 1000)
            )
    
    def get_schema(self) -> dict:
        return self.contract.to_dict()


class CodeAnalyzer(Tool):
    """Analyze code for issues, improvements, and documentation using Ollama."""
    
    class AnalysisType(str, Enum):
        """Types of code analysis."""
        QUALITY = "quality"
        SECURITY = "security"
        PERFORMANCE = "performance"
        DOCUMENTATION = "documentation"
    
    def __init__(
        self,
        ollama_url: str = None,
        model: str = None,
        timeout: int = 30
    ):
        """
        Initialize CodeAnalyzer.
        
        Args:
            ollama_url: Ollama API endpoint (default: from Config.OLLAMA_BASE_URL)
            model: Model name (default: from Config.OLLAMA_MODEL)
            timeout: Request timeout in seconds
        """
        self.ollama_url = (ollama_url or Config.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or Config.OLLAMA_MODEL
        self.timeout = timeout
        
        self.contract = ToolContract(
            name="code_analyzer",
            description="Analyze code for quality, security, performance, or documentation",
            input_schema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Code to analyze",
                        "minLength": 10
                    },
                    "analysis_type": {
                        "type": "string",
                        "enum": ["quality", "security", "performance", "documentation"],
                        "description": "Type of analysis to perform",
                        "default": "quality"
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language (for context)",
                        "default": "python"
                    }
                },
                "required": ["code"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "analysis": {"type": "string"},
                    "issues_found": {"type": "integer"},
                    "suggestions": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            },
            version="1.0.0",
            tags=["code-analysis", "llm", "quality"],
            constraints={
                "requires_ollama": True,
                "min_code_length": 10
            }
        )
    
    @property
    def name(self) -> str:
        return "code_analyzer"
    
    @property
    def description(self) -> str:
        return "Analyze code using Ollama LLM"
    
    async def execute(self, **kwargs) -> ToolResult:
        start = time.perf_counter()
        
        try:
            code = kwargs.get("code", "").strip()
            analysis_type = kwargs.get("analysis_type", "quality")
            language = kwargs.get("language", "python")
            
            # Validate input
            if not code or len(code) < 10:
                return ToolResult(
                    status=ExecutionStatus.INVALID_INPUT,
                    output=None,
                    error="code: Code must be at least 10 characters",
                    latency_ms=int((time.perf_counter() - start) * 1000)
                )
            
            # Validate analysis type
            try:
                self.AnalysisType(analysis_type)
            except ValueError:
                return ToolResult(
                    status=ExecutionStatus.INVALID_INPUT,
                    output=None,
                    error=f"analysis_type: Invalid type '{analysis_type}'. Must be one of: quality, security, performance, documentation",
                    latency_ms=int((time.perf_counter() - start) * 1000)
                )
            
            # Build analysis prompt
            analysis_prompts = {
                "quality": "Analyze this code for quality issues, code smells, and maintainability problems.",
                "security": "Analyze this code for security vulnerabilities and potential exploits.",
                "performance": "Analyze this code for performance issues and optimization opportunities.",
                "documentation": "Analyze this code and suggest what documentation and comments are missing."
            }
            
            prompt = f"""You are a {language} code expert. {analysis_prompts[analysis_type]}

Code:
```{language}
{code}
```

Provide a concise analysis with specific issues found and actionable suggestions."""
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "temperature": 0.3
                    }
                )
            
            if response.status_code != 200:
                return ToolResult(
                    status=ExecutionStatus.FAILURE,
                    output=None,
                    error=f"Ollama API returned {response.status_code}",
                    latency_ms=int((time.perf_counter() - start) * 1000)
                )
            
            analysis_text = response.json().get("response", "").strip()
            
            if not analysis_text:
                return ToolResult(
                    status=ExecutionStatus.FAILURE,
                    output=None,
                    error="Ollama returned empty response",
                    latency_ms=int((time.perf_counter() - start) * 1000)
                )
            
            # Extract issues count (simple heuristic)
            issues_found = len(re.findall(r'issue|problem|vulnerable|error|bug', analysis_text.lower()))
            
            # Extract suggestions (lines starting with dash or number)
            suggestions = [
                line.strip() 
                for line in analysis_text.split('\n') 
                if line.strip().startswith(('-', '*', '•', '1.', '2.', '3.', '4.', '5.'))
            ][:5]  # Limit to 5
            
            return ToolResult(
                status=ExecutionStatus.SUCCESS,
                output={
                    "analysis": analysis_text,
                    "issues_found": issues_found,
                    "suggestions": suggestions if suggestions else ["See full analysis above"]
                },
                metadata={
                    "tool_name": self.name,
                    "model": self.model,
                    "analysis_type": analysis_type,
                    "language": language
                },
                latency_ms=int((time.perf_counter() - start) * 1000)
            )
        
        except httpx.ConnectError:
            return ToolResult(
                status=ExecutionStatus.FAILURE,
                output=None,
                error=f"Cannot connect to Ollama at {self.ollama_url}",
                metadata={"error_type": "ConnectionError"},
                latency_ms=int((time.perf_counter() - start) * 1000)
            )
        
        except TimeoutError:
            return ToolResult(
                status=ExecutionStatus.TIMEOUT,
                output=None,
                error=f"Request timed out after {self.timeout}s",
                latency_ms=int((time.perf_counter() - start) * 1000)
            )
        
        except Exception as e:
            return ToolResult(
                status=ExecutionStatus.FAILURE,
                output=None,
                error=str(e),
                metadata={"exception_type": type(e).__name__},
                latency_ms=int((time.perf_counter() - start) * 1000)
            )
    
    def get_schema(self) -> dict:
        return self.contract.to_dict()
