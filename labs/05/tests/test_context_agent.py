"""
Test Suite for Context Agent

Tests cover:
- Template registration and rendering
- Token counting and budget management
- Context truncation and chunking
- Overflow prevention
- Few-shot example management
- Edge cases and error handling
"""

import pytest
from src.context_agent import ContextAgent, TokenBudget
from src.prompt_templates import (
    PromptTemplates,
    get_template,
    list_templates,
    build_few_shot_template
)


class TestTokenBudget:
    """Test token budget calculations."""
    
    def test_total_tokens(self):
        """TokenBudget calculates total correctly."""
        budget = TokenBudget(system_prompt=200, context=500, response=300)
        assert budget.total == 1000
    
    def test_available_tokens(self):
        """Calculate available tokens for context."""
        budget = TokenBudget(system_prompt=200, context=500, response=300)
        available = budget.available_for_context(8000)
        assert available == 8000 - 1000
    
    def test_available_tokens_overflow(self):
        """Available tokens is 0 when overflow."""
        budget = TokenBudget(system_prompt=200, context=500, response=300)
        available = budget.available_for_context(500)
        assert available == 0


class TestContextAgentInit:
    """Test agent initialization."""
    
    def test_init_default(self):
        """Agent initializes with defaults."""
        agent = ContextAgent()
        assert agent.model == "gpt-3.5-turbo"
        assert agent.max_tokens == 8000
        assert len(agent.templates) == 0
    
    def test_init_custom(self):
        """Agent initializes with custom parameters."""
        agent = ContextAgent(model="gpt-4", max_tokens=32000)
        assert agent.model == "gpt-4"
        assert agent.max_tokens == 32000


class TestTemplateRegistration:
    """Test template registration and rendering."""
    
    def test_register_template(self):
        """Register template successfully."""
        agent = ContextAgent()
        agent.register_template("greeting", "Hello {name}!")
        assert "greeting" in agent.templates
    
    def test_register_duplicate_raises_error(self):
        """Cannot register same template twice."""
        agent = ContextAgent()
        agent.register_template("greeting", "Hello {name}!")
        with pytest.raises(ValueError, match="already registered"):
            agent.register_template("greeting", "Hi {name}!")
    
    def test_render_template(self):
        """Render template with variables."""
        agent = ContextAgent()
        agent.register_template("greeting", "Hello {username}!")
        result = agent.render_template("greeting", username="Alice")
        assert result == "Hello Alice!"
    
    def test_render_nonexistent_template(self):
        """Rendering nonexistent template raises error."""
        agent = ContextAgent()
        with pytest.raises(ValueError, match="not found"):
            agent.render_template("missing", username="Alice")
    
    def test_render_missing_variable(self):
        """Rendering without required variable raises error."""
        agent = ContextAgent()
        agent.register_template("greeting", "Hello {name}!")
        with pytest.raises(ValueError, match="Missing required variable"):
            agent.render_template("greeting")
    
    def test_get_template_names(self):
        """Get list of registered templates."""
        agent = ContextAgent()
        agent.register_template("greeting", "Hello {name}!")
        agent.register_template("farewell", "Goodbye {name}!")
        names = agent.get_template_names()
        assert set(names) == {"greeting", "farewell"}


class TestTokenCounting:
    """Test token counting functionality."""
    
    def test_count_tokens_short(self):
        """Count tokens in short text."""
        agent = ContextAgent()
        tokens = agent.count_tokens("hello world")
        assert tokens > 0
        assert tokens < 10
    
    def test_count_tokens_long(self):
        """Count tokens in longer text."""
        agent = ContextAgent()
        text = "word " * 1000  # ~1000 words
        tokens = agent.count_tokens(text)
        assert tokens > 500  # Should be roughly half word count
    
    def test_count_tokens_empty(self):
        """Count tokens in empty string."""
        agent = ContextAgent()
        tokens = agent.count_tokens("")
        assert tokens == 0
    
    def test_token_estimation_consistency(self):
        """Token count scales roughly with text length."""
        agent = ContextAgent()
        text1 = "hello"
        text2 = "hello hello hello"
        
        tokens1 = agent.count_tokens(text1)
        tokens2 = agent.count_tokens(text2)
        
        # Longer text should have more tokens
        assert tokens2 > tokens1


class TestContextTruncation:
    """Test text truncation to fit token limits."""
    
    def test_truncate_fits_within_limit(self):
        """Text within limit is not truncated."""
        agent = ContextAgent()
        text = "short text"
        result = agent.truncate_to_fit(text, 100)
        assert result == text
    
    def test_truncate_exceeds_limit(self):
        """Text exceeding limit is truncated."""
        agent = ContextAgent()
        text = "word " * 1000
        result = agent.truncate_to_fit(text, 100)
        assert len(result) < len(text)
        assert agent.count_tokens(result) <= 100
    
    def test_truncate_zero_tokens(self):
        """Truncate to 0 tokens returns empty string."""
        agent = ContextAgent()
        text = "hello world"
        result = agent.truncate_to_fit(text, 0)
        assert result == ""


class TestTextChunking:
    """Test text chunking functionality."""
    
    def test_chunk_short_text(self):
        """Short text that fits returns single chunk."""
        agent = ContextAgent()
        text = "hello world"
        chunks = agent.chunk_text(text, chunk_size=100)
        assert len(chunks) == 1
        assert chunks[0] == text
    
    def test_chunk_long_text(self):
        """Long text is split into multiple chunks."""
        agent = ContextAgent()
        text = "word " * 1000
        chunks = agent.chunk_text(text, chunk_size=200)
        
        assert len(chunks) > 1
        
        # Each chunk should fit within size
        for chunk in chunks:
            assert agent.count_tokens(chunk) <= 200
    
    def test_chunk_invalid_size(self):
        """Invalid chunk size raises error."""
        agent = ContextAgent()
        with pytest.raises(ValueError, match="must be positive"):
            agent.chunk_text("text", chunk_size=0)
        
        with pytest.raises(ValueError, match="must be positive"):
            agent.chunk_text("text", chunk_size=-1)
    
    def test_chunk_size_consistency(self):
        """Chunks stay within specified token size."""
        agent = ContextAgent()
        text = "word " * 2000
        chunk_size = 300
        chunks = agent.chunk_text(text, chunk_size)
        
        for chunk in chunks:
            assert agent.count_tokens(chunk) <= chunk_size


class TestContextOverflowPrevention:
    """Test overflow prevention."""
    
    def test_render_within_limit(self):
        """Rendering within limit succeeds."""
        agent = ContextAgent(max_tokens=8000)
        agent.register_template("test", "Hello {username}!")
        result = agent.render_with_context_check("test", username="Alice")
        assert "Hello Alice!" in result
    
    def test_render_exceeds_limit(self):
        """Rendering exceeding limit raises error."""
        agent = ContextAgent(max_tokens=10)  # Very small limit
        agent.register_template("long", "word " * 1000)  # Very long
        
        with pytest.raises(ValueError, match="exceeds token limit"):
            agent.render_with_context_check("long")
    
    def test_manage_context_truncate(self):
        """Manage context truncates when needed."""
        agent = ContextAgent(max_tokens=1000)
        text = "word " * 1000
        result = agent.manage_context(text, max_tokens=500, strategy="truncate")
        
        assert isinstance(result, str)
        assert len(result) < len(text)
    
    def test_manage_context_chunk(self):
        """Manage context chunks when needed."""
        agent = ContextAgent(max_tokens=1000)
        text = "word " * 1000
        result = agent.manage_context(text, max_tokens=500, strategy="chunk")
        
        assert isinstance(result, list)
        assert len(result) > 1
    
    def test_manage_context_fits(self):
        """Manage context returns original if it fits."""
        agent = ContextAgent(max_tokens=8000)
        text = "short text"
        result = agent.manage_context(text, max_tokens=8000, strategy="truncate")
        assert result == text
    
    def test_manage_context_invalid_strategy(self):
        """Invalid strategy raises error."""
        agent = ContextAgent()
        with pytest.raises(ValueError, match="Unknown strategy"):
            agent.manage_context("text", strategy="invalid")


class TestBudgetSummary:
    """Test budget summary calculations."""
    
    def test_budget_summary_basic(self):
        """Get budget summary for prompt."""
        agent = ContextAgent(max_tokens=8000)
        agent.register_template("test", "Hello world!")
        prompt = agent.render_template("test")
        
        summary = agent.get_budget_summary(
            prompt,
            system_prompt_tokens=200,
            response_tokens=500
        )
        
        assert summary["model"] == "gpt-3.5-turbo"
        assert summary["context_window"] == 8000
        assert summary["system_prompt"] == 200
        assert summary["response"] == 500
        assert summary["available"] >= 0
    
    def test_budget_summary_overflow(self):
        """Budget shows overflow when tokens exceed."""
        agent = ContextAgent(max_tokens=100)
        text = "word " * 1000
        
        summary = agent.get_budget_summary(
            text,
            system_prompt_tokens=50,
            response_tokens=50
        )
        
        assert summary["overflow"] > 0
        assert not summary["fits"]
    
    def test_budget_summary_fits(self):
        """Budget shows fit when within limit."""
        agent = ContextAgent(max_tokens=8000)
        text = "short text"
        
        summary = agent.get_budget_summary(
            text,
            system_prompt_tokens=200,
            response_tokens=500
        )
        
        assert summary["fits"]
        assert summary["available"] > 0


class TestExampleManagement:
    """Test few-shot example registration."""
    
    def test_register_examples(self):
        """Register example category."""
        agent = ContextAgent()
        examples = [
            {"text": "Great!", "label": "POSITIVE"},
            {"text": "Bad", "label": "NEGATIVE"}
        ]
        agent.register_examples("sentiment", examples)
        assert "sentiment" in agent.examples
    
    def test_get_example_categories(self):
        """Get list of example categories."""
        agent = ContextAgent()
        agent.register_examples("sentiment", [{"text": "Great!", "label": "POSITIVE"}])
        agent.register_examples("topic", [{"text": "Python", "label": "TECH"}])
        
        categories = agent.get_example_categories()
        assert set(categories) == {"sentiment", "topic"}
    
    def test_format_examples(self):
        """Format examples for prompt inclusion."""
        agent = ContextAgent()
        examples = [
            {"text": "Great!", "label": "POSITIVE"},
            {"text": "Bad", "label": "NEGATIVE"}
        ]
        agent.register_examples("sentiment", examples)
        
        formatted = agent.format_examples(
            "sentiment",
            'Text: {text}, Label: {label}'
        )
        
        assert "Great!" in formatted
        assert "POSITIVE" in formatted
        assert "Bad" in formatted
    
    def test_format_examples_missing_category(self):
        """Format missing category raises error."""
        agent = ContextAgent()
        with pytest.raises(ValueError, match="not found"):
            agent.format_examples("missing")
    
    def test_format_examples_missing_field(self):
        """Format with missing field raises error."""
        agent = ContextAgent()
        agent.register_examples("test", [{"text": "hello"}])
        
        with pytest.raises(ValueError, match="Missing field"):
            agent.format_examples("test", "Text: {text}, Missing: {missing}")


class TestPromptTemplates:
    """Test prompt template library."""
    
    def test_get_template_qa(self):
        """Get Q&A template."""
        template = get_template("qa")
        assert "question" in template.lower()
        assert "context" in template.lower()
    
    def test_get_template_reasoning(self):
        """Get reasoning template."""
        template = get_template("reasoning")
        assert "step" in template.lower()
    
    def test_get_template_sentiment(self):
        """Get sentiment analysis template."""
        template = get_template("sentiment_analysis")
        assert "positive" in template.lower()
        assert "negative" in template.lower()
    
    def test_get_template_invalid(self):
        """Getting invalid template raises error."""
        with pytest.raises(ValueError, match="not found"):
            get_template("nonexistent")
    
    def test_list_templates(self):
        """List all available templates."""
        templates = list_templates()
        assert isinstance(templates, dict)
        assert len(templates) > 0
        assert "qa" in templates
        assert "reasoning" in templates


class TestFewShotBuilder:
    """Test few-shot template builder."""
    
    def test_build_few_shot_basic(self):
        """Build few-shot template from examples."""
        examples = [
            {"text": "Great!", "sentiment": "POSITIVE"},
            {"text": "Bad", "sentiment": "NEGATIVE"}
        ]
        
        template = build_few_shot_template(
            "Classify sentiment",
            examples,
            'Text: {text}, Sentiment: {sentiment}',
            "text"
        )
        
        assert "Classify sentiment" in template
        assert "Great!" in template
        assert "POSITIVE" in template
    
    def test_build_few_shot_no_examples(self):
        """Build without examples raises error."""
        with pytest.raises(ValueError, match="At least one"):
            build_few_shot_template(
                "Test",
                [],
                "format",
                "input"
            )
    
    def test_build_few_shot_missing_field(self):
        """Build with missing field in example raises error."""
        examples = [{"text": "hello"}]  # Missing 'label'
        
        with pytest.raises(ValueError, match="Example missing required field"):
            build_few_shot_template(
                "Test",
                examples,
                'Text: {text}, Label: {label}',
                "text"
            )


class TestIntegration:
    """Integration tests combining multiple features."""
    
    def test_workflow_qa_with_context(self):
        """Complete Q&A workflow with context management."""
        agent = ContextAgent(max_tokens=8000)
        
        # Register Q&A template
        agent.register_template(
            "qa",
            "Question: {question}\nContext: {context}\nAnswer:"
        )
        
        # Manage large context
        large_context = "word " * 500
        managed_context = agent.manage_context(large_context, strategy="truncate")
        
        # Render with managed context
        prompt = agent.render_template("qa", question="What is AI?", context=managed_context)
        
        # Check budget
        summary = agent.get_budget_summary(prompt)
        assert summary["fits"]
    
    def test_workflow_few_shot_classification(self):
        """Complete few-shot classification workflow."""
        agent = ContextAgent()
        
        # Register examples
        examples = [
            {"text": "Excellent product", "label": "POSITIVE"},
            {"text": "Terrible service", "label": "NEGATIVE"},
            {"text": "Item arrived", "label": "NEUTRAL"}
        ]
        agent.register_examples("sentiment", examples)
        
        # Format examples in template
        template = PromptTemplates.SENTIMENT_ANALYSIS_TEMPLATE
        agent.register_template("sentiment", template)
        
        # Render with examples
        prompt = agent.render_template("sentiment", text="This is great!")
        assert "Excellent product" in prompt or "POSITIVE" in prompt
    
    def test_workflow_large_document_handling(self):
        """Handle large document with chunking."""
        agent = ContextAgent(max_tokens=8000)
        
        # Large document
        large_doc = "word " * 2000
        
        # Chunk document
        chunks = agent.chunk_text(large_doc, chunk_size=400)
        
        assert len(chunks) > 1
        
        # Each chunk fits budget
        for chunk in chunks:
            summary = agent.get_budget_summary(chunk)
            assert summary["fits"]
