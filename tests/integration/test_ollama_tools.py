"""
Integration tests for Ollama-based tools.

These tests require a running Ollama instance with mistral:7b model.

Skip with: pytest -k "not ollama" or set SKIP_OLLAMA=true
"""

import pytest
import os
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agent_labs.tools.ollama_tools import TextSummarizer, CodeAnalyzer
from agent_labs.tools.contract import ExecutionStatus
from agent_labs.tools import ToolRegistry

# Skip all tests if SKIP_OLLAMA is set or Ollama not available
SKIP_OLLAMA = os.getenv("SKIP_OLLAMA", "false").lower() == "true"

pytestmark = pytest.mark.skipif(SKIP_OLLAMA, reason="Ollama tests disabled (set SKIP_OLLAMA=false to run)")


class TestTextSummarizer:
    """Tests for TextSummarizer tool with Ollama."""
    
    @pytest.fixture
    def summarizer(self):
        """Create TextSummarizer instance."""
        return TextSummarizer(
            ollama_url="http://localhost:11434",
            model="mistral:7b",
            max_tokens=200,
            temperature=0.3,
            timeout=60
        )
    
    @pytest.mark.asyncio
    async def test_summarizer_basic(self, summarizer):
        """Test basic text summarization."""
        text = """
        Python is a high-level, interpreted programming language with dynamic semantics.
        Its high-level built-in data structures, combined with dynamic typing and binding,
        make it very attractive for Rapid Application Development, as well as for use as
        a scripting or glue language to connect existing components together.
        Python's simple, easy to learn syntax emphasizes readability and therefore reduces
        the cost of program maintenance. Python supports modules and packages, which encourages
        program modularity and code reuse. The Python interpreter and the extensive standard library
        are available in source or binary form without charge for all major platforms, and can be
        freely distributed.
        """
        
        result = await summarizer.execute(text=text, max_length=50)
        
        assert result.status == ExecutionStatus.SUCCESS
        assert result.success
        assert isinstance(result.output, dict)
        assert "summary" in result.output
        assert "word_count" in result.output
        assert result.output["word_count"] > 0
        assert result.latency_ms > 0
        assert "model" in result.metadata
    
    @pytest.mark.asyncio
    async def test_summarizer_preserves_meaning(self, summarizer):
        """Test that summary captures key information."""
        text = """
        Machine Learning is a subset of Artificial Intelligence that enables systems to learn
        and improve from experience without being explicitly programmed. ML algorithms build
        mathematical models based on sample data, known as training data, in order to make
        predictions or decisions without being explicitly instructed to perform the task.
        Common ML techniques include supervised learning, unsupervised learning, and reinforcement
        learning. Applications range from recommendation systems to autonomous vehicles to medical
        diagnosis. The field has grown exponentially with advances in computing power and data availability.
        """
        
        result = await summarizer.execute(text=text, max_length=75)
        
        assert result.status == ExecutionStatus.SUCCESS
        assert "learning" in result.output["summary"].lower() or \
               "machine" in result.output["summary"].lower() or \
               "data" in result.output["summary"].lower()
    
    @pytest.mark.asyncio
    async def test_summarizer_respects_max_length(self, summarizer):
        """Test that summary respects max_length constraint."""
        text = """
        Artificial Intelligence (AI) encompasses a wide range of technologies and techniques
        designed to enable machines to perform tasks that typically require human intelligence.
        This includes visual perception, speech recognition, language understanding, and
        decision-making. AI systems can be categorized into narrow AI (specialized) and general AI
        (broad capability). Current AI is primarily narrow AI, excelling at specific tasks while
        lacking general knowledge transfer. Challenges include interpretability, bias, and safety.
        Recent breakthroughs in deep learning have accelerated AI progress across many domains.
        """
        
        result = await summarizer.execute(text=text, max_length=30)
        
        assert result.status == ExecutionStatus.SUCCESS
        word_count = result.output["word_count"]
        # Allow some flexibility due to LLM variability
        assert word_count <= 40  # 30 + 33% tolerance
    
    @pytest.mark.asyncio
    async def test_summarizer_short_text_error(self, summarizer):
        """Test that short text is rejected."""
        result = await summarizer.execute(text="This is too short.")
        
        assert result.status == ExecutionStatus.INVALID_INPUT
        assert result.failed
        assert "50 characters" in result.error
    
    @pytest.mark.asyncio
    async def test_summarizer_empty_text_error(self, summarizer):
        """Test that empty text is rejected."""
        result = await summarizer.execute(text="")
        
        assert result.status == ExecutionStatus.INVALID_INPUT
        assert "50 characters" in result.error
    
    @pytest.mark.asyncio
    async def test_summarizer_invalid_max_length(self, summarizer):
        """Test that invalid max_length is rejected."""
        text = "This is a valid text that is long enough to summarize." * 2
        
        result = await summarizer.execute(text=text, max_length=5)
        
        assert result.status == ExecutionStatus.INVALID_INPUT
        assert "10 and 1000" in result.error
    
    @pytest.mark.asyncio
    async def test_summarizer_includes_metadata(self, summarizer):
        """Test that execution includes rich metadata."""
        text = "Python is a programming language." * 5
        
        result = await summarizer.execute(text=text)
        
        assert result.status == ExecutionStatus.SUCCESS
        assert "model" in result.metadata
        assert "temperature" in result.metadata
        assert result.metadata["model"] == "mistral:7b"
        assert result.metadata["temperature"] == 0.3
    
    def test_summarizer_schema(self, summarizer):
        """Test tool schema structure."""
        schema = summarizer.get_schema()
        
        assert schema["name"] == "text_summarizer"
        assert schema["version"] == "1.0.0"
        assert "summarization" in schema["tags"]
        assert "input_schema" in schema
        assert "output_schema" in schema
        assert "constraints" in schema
        assert schema["constraints"]["requires_ollama"] is True


class TestCodeAnalyzer:
    """Tests for CodeAnalyzer tool with Ollama."""
    
    @pytest.fixture
    def analyzer(self):
        """Create CodeAnalyzer instance."""
        return CodeAnalyzer(
            ollama_url="http://localhost:11434",
            model="mistral:7b",
            timeout=60
        )
    
    @pytest.mark.asyncio
    async def test_analyzer_quality_analysis(self, analyzer):
        """Test code quality analysis."""
        code = """
def calculate(x, y):
    z = x + y
    print(z)
    return z

result = calculate(5, 3)
"""
        
        result = await analyzer.execute(code=code, analysis_type="quality", language="python")
        
        assert result.status == ExecutionStatus.SUCCESS
        assert result.success
        assert isinstance(result.output, dict)
        assert "analysis" in result.output
        assert "issues_found" in result.output
        assert isinstance(result.output["issues_found"], int)
        assert "suggestions" in result.output
        assert isinstance(result.output["suggestions"], list)
    
    @pytest.mark.asyncio
    async def test_analyzer_security_analysis(self, analyzer):
        """Test code security analysis."""
        code = """
import os
password = "hardcoded_password_123"
os.system("rm -rf /")
"""
        
        result = await analyzer.execute(code=code, analysis_type="security", language="python")
        
        assert result.status == ExecutionStatus.SUCCESS
        assert result.output["issues_found"] > 0  # Should find security issues
        assert len(result.output["suggestions"]) > 0
    
    @pytest.mark.asyncio
    async def test_analyzer_performance_analysis(self, analyzer):
        """Test code performance analysis."""
        code = """
def inefficient_search(items, target):
    for i in range(len(items)):
        for j in range(len(items)):
            if items[i] == target or items[j] == target:
                return True
    return False
"""
        
        result = await analyzer.execute(code=code, analysis_type="performance", language="python")
        
        assert result.status == ExecutionStatus.SUCCESS
        assert "analysis" in result.output
        assert isinstance(result.output["analysis"], str)
    
    @pytest.mark.asyncio
    async def test_analyzer_documentation_analysis(self, analyzer):
        """Test code documentation analysis."""
        code = """
def calculate_area(radius):
    return 3.14159 * radius * radius

def process_data(data):
    result = {}
    for item in data:
        key = item[0]
        value = item[1]
        result[key] = value
    return result
"""
        
        result = await analyzer.execute(code=code, analysis_type="documentation", language="python")
        
        assert result.status == ExecutionStatus.SUCCESS
        assert "missing" in result.output["analysis"].lower() or \
               "document" in result.output["analysis"].lower() or \
               "comment" in result.output["analysis"].lower()
    
    @pytest.mark.asyncio
    async def test_analyzer_short_code_error(self, analyzer):
        """Test that code must be at least 10 characters."""
        result = await analyzer.execute(code="x = 1")
        
        assert result.status == ExecutionStatus.INVALID_INPUT
        assert "10 characters" in result.error
    
    @pytest.mark.asyncio
    async def test_analyzer_invalid_analysis_type(self, analyzer):
        """Test that invalid analysis_type is rejected."""
        code = "def test(): pass" * 2
        
        result = await analyzer.execute(code=code, analysis_type="invalid_type")
        
        assert result.status == ExecutionStatus.INVALID_INPUT
        assert "Invalid type" in result.error
    
    @pytest.mark.asyncio
    async def test_analyzer_all_analysis_types(self, analyzer):
        """Test all analysis types work."""
        code = """
def helper(data):
    return len(data)
""" * 2
        
        for analysis_type in ["quality", "security", "performance", "documentation"]:
            result = await analyzer.execute(code=code, analysis_type=analysis_type)
            assert result.status == ExecutionStatus.SUCCESS
            assert "analysis" in result.output
    
    @pytest.mark.asyncio
    async def test_analyzer_different_languages(self, analyzer):
        """Test analyzer with different programming languages."""
        js_code = """
function add(a, b) {
    return a + b;
}
const result = add(5, 3);
"""
        
        result = await analyzer.execute(code=js_code, language="javascript")
        
        assert result.status == ExecutionStatus.SUCCESS
        assert result.metadata["language"] == "javascript"
    
    @pytest.mark.asyncio
    async def test_analyzer_includes_metadata(self, analyzer):
        """Test that analysis includes rich metadata."""
        code = "def test(): pass" * 2
        
        result = await analyzer.execute(code=code, analysis_type="quality")
        
        assert result.status == ExecutionStatus.SUCCESS
        assert "model" in result.metadata
        assert "analysis_type" in result.metadata
        assert "language" in result.metadata
        assert result.metadata["analysis_type"] == "quality"
    
    def test_analyzer_schema(self, analyzer):
        """Test tool schema structure."""
        schema = analyzer.get_schema()
        
        assert schema["name"] == "code_analyzer"
        assert schema["version"] == "1.0.0"
        assert "code-analysis" in schema["tags"]
        assert "input_schema" in schema
        assert "output_schema" in schema
        assert "constraints" in schema
        assert schema["constraints"]["requires_ollama"] is True


class TestOllamaToolsRegistry:
    """Test Ollama tools integrated with ToolRegistry."""
    
    @pytest.mark.asyncio
    async def test_registry_with_ollama_tools(self):
        """Test registering and using Ollama tools with registry."""
        registry = ToolRegistry()
        
        summarizer = TextSummarizer()
        analyzer = CodeAnalyzer()
        
        registry.register(summarizer)
        registry.register(analyzer)
        
        assert "text_summarizer" in registry
        assert "code_analyzer" in registry
        assert len(registry) == 2
    
    @pytest.mark.asyncio
    async def test_registry_schema_discovery(self):
        """Test schema discovery for Ollama tools."""
        registry = ToolRegistry()
        
        summarizer = TextSummarizer()
        analyzer = CodeAnalyzer()
        
        registry.register(summarizer)
        registry.register(analyzer)
        
        schemas = registry.get_all_schemas()
        
        assert "text_summarizer" in schemas
        assert "code_analyzer" in schemas
        assert schemas["text_summarizer"]["constraints"]["requires_ollama"]
        assert schemas["code_analyzer"]["constraints"]["requires_ollama"]
    
    @pytest.mark.asyncio
    async def test_registry_execution_with_validation(self):
        """Test registry validates Ollama tool inputs."""
        registry = ToolRegistry()
        registry.register(TextSummarizer())
        
        # Valid execution
        text = "This is valid text for summarization." * 3
        result = await registry.execute("text_summarizer", text=text)
        assert result.status == ExecutionStatus.SUCCESS
        
        # Invalid execution (short text)
        result = await registry.execute("text_summarizer", text="Short", validate_input=False)
        # Registry doesn't validate if flag is False, but tool will validate
        assert result.status == ExecutionStatus.INVALID_INPUT
    
    @pytest.mark.asyncio
    async def test_registry_batch_execution_with_ollama_tools(self):
        """Test batch execution with Ollama tools."""
        registry = ToolRegistry()
        summarizer = TextSummarizer()
        registry.register(summarizer)
        
        text1 = "First text for summarization." * 3
        text2 = "Second text for summarization." * 3
        
        operations = [
            ("text_summarizer", {"text": text1, "max_length": 50}),
            ("text_summarizer", {"text": text2, "max_length": 75})
        ]
        
        results = await registry.execute_batch(operations)
        
        assert len(results) == 2
        assert all(r.success for r in results)


class TestOllamaToolsErrorHandling:
    """Test error handling in Ollama tools."""
    
    @pytest.mark.asyncio
    async def test_summarizer_connection_error(self):
        """Test handling of connection errors."""
        summarizer = TextSummarizer(
            ollama_url="http://localhost:9999",  # Wrong port
            timeout=5
        )
        
        text = "Valid text for summarization." * 3
        result = await summarizer.execute(text=text)
        
        # Should fail with connection error
        assert result.status == ExecutionStatus.FAILURE
        assert "Cannot connect" in result.error
    
    @pytest.mark.asyncio
    async def test_analyzer_connection_error(self):
        """Test analyzer connection error handling."""
        analyzer = CodeAnalyzer(
            ollama_url="http://localhost:9999",  # Wrong port
            timeout=5
        )
        
        code = "def test(): pass" * 2
        result = await analyzer.execute(code=code)
        
        assert result.status == ExecutionStatus.FAILURE
        assert "Cannot connect" in result.error


class TestOllamaToolsPerformance:
    """Test performance characteristics of Ollama tools."""
    
    @pytest.mark.asyncio
    async def test_summarizer_tracks_latency(self):
        """Test that summarizer tracks execution latency."""
        summarizer = TextSummarizer()
        
        text = "Performance test text." * 10
        result = await summarizer.execute(text=text)
        
        if result.success:
            assert result.latency_ms > 0
            assert result.latency_ms > 1000  # Ollama typically takes >1s
    
    @pytest.mark.asyncio
    async def test_analyzer_tracks_latency(self):
        """Test that analyzer tracks execution latency."""
        analyzer = CodeAnalyzer()
        
        code = "def test(): pass" * 5
        result = await analyzer.execute(code=code)
        
        if result.success:
            assert result.latency_ms > 0
            assert result.latency_ms > 1000  # Ollama typically takes >1s
