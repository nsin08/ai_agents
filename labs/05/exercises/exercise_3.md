# Exercise 3: Context Window Management

## Objective
Learn to handle large documents by implementing context overflow prevention strategies. Understand token budgets, chunking, and truncation.

## Background

All language models have a **context window** limit. For example:
- GPT-3.5-turbo: 4K or 16K tokens
- GPT-4: 8K or 32K tokens
- Claude: 100K tokens

When your prompt exceeds the limit, the model fails or truncates. Solutions:

1. **Truncation**: Cut text to fit limit
2. **Chunking**: Split into smaller pieces, process separately
3. **Summarization**: Compress document while preserving key information
4. **Ranking**: Include most relevant sections first

## Project: Document Processing with Context Management

You will build a system that:
- Counts tokens in documents
- Prevents overflow
- Compares truncation vs chunking strategies
- Measures output quality for each approach

---

## Tasks

### Task 3.1: Token Counting and Budget

Create `exercise_3_token_budgets.py`:

```python
from src.context_agent import ContextAgent

# Initialize agent for an 8K token model
agent = ContextAgent(model="gpt-3.5-turbo", max_tokens=8000)

# Define system prompt and response reservation
system_prompt_tokens = 200  # Instructions for agent
response_tokens = 500       # Space for answer

# Sample documents (varying sizes)
documents = {
    "small": "your text here" * 50,        # ~200 words
    "medium": "your text here" * 200,      # ~800 words
    "large": "your text here" * 500,       # ~2000 words
}

# Analyze each document
for name, doc in documents.items():
    summary = agent.get_budget_summary(
        doc,
        system_prompt_tokens=system_prompt_tokens,
        response_tokens=response_tokens
    )
    
    print(f"\n{'='*50}")
    print(f"Document: {name}")
    print(f"{'='*50}")
    print(f"System Prompt:    {summary['system_prompt']:>6} tokens")
    print(f"Document:         {summary['prompt']:>6} tokens")
    print(f"Response Buffer:  {summary['response']:>6} tokens")
    print(f"Total Used:       {summary['total_used']:>6} tokens")
    print(f"Available:        {summary['available']:>6} tokens")
    print(f"Context Window:   {summary['context_window']:>6} tokens")
    print(f"Fits Budget:      {'✓ YES' if summary['fits'] else '✗ NO (overflow)'}")
    
    if summary['overflow']:
        print(f"Overflow:         {summary['overflow']:>6} tokens")
```

**Expected Output**:
- Token counts for each document
- Budget breakdowns
- Indication of which documents exceed limit

**Deliverable**: Script showing token budgets for 3 document sizes

---

### Task 3.2: Implement Truncation Strategy

Create `exercise_3_truncation.py`:

```python
from src.context_agent import ContextAgent

agent = ContextAgent(max_tokens=8000)

# Load a large document (2000+ tokens)
large_document = "word " * 2000

# Method 1: Simple truncation
print("Method 1: Truncation")
print("="*50)

available_tokens = 4000  # After system prompt + response
truncated = agent.truncate_to_fit(large_document, available_tokens)

print(f"Original length:    {len(large_document):>6} chars")
print(f"Truncated length:   {len(truncated):>6} chars")
print(f"Original tokens:    {agent.count_tokens(large_document):>6}")
print(f"Truncated tokens:   {agent.count_tokens(truncated):>6}")
print(f"Reduction:          {(1 - len(truncated)/len(large_document))*100:.1f}%")

# Check if it fits budget
summary = agent.get_budget_summary(truncated)
print(f"Fits budget:        {'✓ YES' if summary['fits'] else '✗ NO'}")

# Preview the truncated text (first and last 100 chars)
print(f"\nFirst 100 chars:    {truncated[:100]}...")
print(f"Last 100 chars:     ...{truncated[-100:]}")
```

**Expected Output**:
- Original vs truncated size
- Character and token reduction percentages
- Budget verification
- Preview of truncated text

**Deliverable**: Truncation comparison script

---

### Task 3.3: Implement Chunking Strategy

Create `exercise_3_chunking.py`:

```python
from src.context_agent import ContextAgent

agent = ContextAgent(max_tokens=8000)

# Large document (2000+ tokens)
large_document = "word " * 2000

# Method 2: Chunking
print("Method 2: Chunking")
print("="*50)

chunk_size = 400  # Tokens per chunk
chunks = agent.chunk_text(large_document, chunk_size)

print(f"Original tokens:    {agent.count_tokens(large_document):>6}")
print(f"Chunk size target:  {chunk_size:>6} tokens")
print(f"Number of chunks:   {len(chunks):>6}")

print(f"\nChunk Analysis:")
print(f"{'Chunk':<10} {'Size':<10} {'Tokens':<10} {'Fits':<10}")
print("-" * 40)

for i, chunk in enumerate(chunks):
    tokens = agent.count_tokens(chunk)
    fits = "✓ YES" if tokens <= chunk_size else "✗ NO"
    print(f"Chunk {i:<2} {len(chunk):<10} {tokens:<10} {fits:<10}")

# Total coverage
total_chars_chunked = sum(len(chunk) for chunk in chunks)
coverage = (total_chars_chunked / len(large_document)) * 100
print(f"\nTotal coverage: {coverage:.1f}% of original document")
```

**Expected Output**:
- Number of chunks needed
- Size of each chunk
- Verification that each fits budget
- Coverage percentage

**Deliverable**: Chunking analysis script

---

### Task 3.4: Strategy Comparison

Create `exercise_3_strategy_comparison.md`:

Compare truncation vs chunking approaches:

```markdown
# Strategy Comparison

## Truncation Strategy
**Pros**:
- Simple, one-step process
- No coordination overhead
- Preserves chronological order

**Cons**:
- Loses end of document
- May cut mid-sentence
- Important info might be at end

**Best For**:
- Documents with important info at start
- Real-time applications (need fast response)
- Sequential documents (logs, timelines)

**Quality Trade-off**:
- Information loss: HIGH
- Implementation complexity: LOW
- Processing speed: FAST

---

## Chunking Strategy
**Pros**:
- Preserves full document
- Can process in parallel
- Allows reordering by importance

**Cons**:
- More complex processing
- Requires chunk coordination
- May cut mid-thought across chunks

**Best For**:
- Long documents needing full analysis
- Batch processing (not real-time)
- High-quality requirements

**Quality Trade-off**:
- Information loss: LOW
- Implementation complexity: MEDIUM
- Processing speed: SLOW

---

## Recommendation Matrix

| Use Case | Strategy | Reason |
|----------|----------|--------|
| Real-time chat | Truncate | Speed critical |
| Document analysis | Chunk | Quality critical |
| Log summarization | Truncate | Info at start |
| Book analysis | Chunk | Preserve all |
| API response | Truncate | Single response |
| Research paper | Chunk | Complex analysis |
```

**Deliverable**: Strategy comparison document

---

### Task 3.5: Integrated Context Management

Create `exercise_3_workflow.py` - Complete workflow:

```python
from src.context_agent import ContextAgent
from src.prompt_templates import get_template

# Initialize agent
agent = ContextAgent(max_tokens=8000)

# Register summarization template
agent.register_template(
    "summarize",
    get_template("summarization")
)

# Document to process
document = "word " * 2000

print("="*60)
print("CONTEXT MANAGEMENT WORKFLOW")
print("="*60)

# Step 1: Analyze document
print("\nStep 1: Analyze Document")
print("-"*40)
doc_tokens = agent.count_tokens(document)
print(f"Document size: {doc_tokens} tokens")

# Step 2: Check fit
print("\nStep 2: Check Token Budget")
print("-"*40)
summary = agent.get_budget_summary(document, system_prompt_tokens=200, response_tokens=500)
print(f"Fits in 8K model: {summary['fits']}")

if not summary['fits']:
    overflow = summary['overflow']
    print(f"Overflow: {overflow} tokens")
    
    # Step 3: Choose strategy
    print("\nStep 3: Choose Management Strategy")
    print("-"*40)
    
    if overflow < 1000:
        # Truncate (small overflow)
        print("Strategy: TRUNCATE (overflow < 1000 tokens)")
        managed = agent.manage_context(document, strategy="truncate")
        print(f"Truncated to: {agent.count_tokens(managed)} tokens")
    else:
        # Chunk (large overflow)
        print("Strategy: CHUNK (overflow >= 1000 tokens)")
        managed = agent.manage_context(document, strategy="chunk")
        print(f"Chunked into: {len(managed)} pieces")
        
        # Process each chunk
        for i, chunk in enumerate(managed):
            chunk_tokens = agent.count_tokens(chunk)
            print(f"  Chunk {i}: {chunk_tokens} tokens")
    
    # Step 4: Verify fit
    print("\nStep 4: Verify Managed Content Fits")
    print("-"*40)
    if isinstance(managed, str):
        final_summary = agent.get_budget_summary(managed)
    else:  # list of chunks
        # Check largest chunk
        largest = max(managed, key=lambda x: agent.count_tokens(x))
        final_summary = agent.get_budget_summary(largest)
    
    print(f"Fits in 8K model: {'✓ YES' if final_summary['fits'] else '✗ NO'}")
else:
    print("Document fits - no management needed")

print("\n" + "="*60)
```

**Deliverable**: Complete workflow script

---

### Task 3.6: Analysis Report

Create `exercise_3_analysis_report.md`:

Document your findings:

1. **Token Counting Accuracy**:
   - How accurate is the token estimation?
   - Test on documents of varying lengths
   - Compare estimated vs actual (if possible)

2. **Truncation Performance**:
   - What % of text retained for 50%, 75%, 90% budget?
   - What information is lost?
   - Usefulness for common tasks?

3. **Chunking Performance**:
   - How many chunks for 2K, 5K, 10K token documents?
   - Average chunk size?
   - How much processing overhead?

4. **Strategy Selection Decision Tree**:
   ```
   Is document within budget?
   ├─ YES → Use as-is
   └─ NO  → Is overflow < 1000 tokens?
            ├─ YES → TRUNCATE
            └─ NO  → CHUNK
   ```

5. **Real-World Scenarios**:
   - Customer support: Truncate or chunk?
   - Research paper summarization: Truncate or chunk?
   - Code review: Truncate or chunk?
   - Chat message: Truncate or chunk?

**Deliverable**: Analysis report (2-3 pages)

---

## Success Criteria

- [ ] Token counting implemented and tested
- [ ] Budget calculation verified for 3 document sizes
- [ ] Truncation strategy tested (text shortened correctly)
- [ ] Chunking strategy tested (chunks fit budget)
- [ ] Strategy comparison document created
- [ ] Integrated workflow demonstrates both approaches
- [ ] Analysis report with decision guidelines

## Testing Your Solution

Run tests:
```bash
pytest tests/test_context_agent.py::TestTokenCounting -v
pytest tests/test_context_agent.py::TestContextTruncation -v
pytest tests/test_context_agent.py::TestTextChunking -v
pytest tests/test_context_agent.py::TestContextOverflowPrevention -v
pytest tests/test_context_agent.py::TestIntegration::test_workflow_large_document_handling -v
```

## Key Learning Points

1. Every model has a context limit - understand yours
2. Token budgets require: system prompt + document + response reserve
3. Truncation is fast but loses information
4. Chunking preserves content but needs coordination
5. Choose strategy based on: accuracy needs, speed needs, document importance
6. Always verify managed content fits final budget

## Advanced Extensions

1. Implement summarization-based management (compress instead of truncate/chunk)
2. Implement importance ranking (prioritize key sections)
3. Compare quality: truncation vs chunking vs summarization
4. Build adaptive strategy selector based on document type
5. Implement sliding window approach (overlapping chunks)

## Next Steps

- Integrate with actual LLM API for production use
- Build template + context management pipeline
- Create monitoring for token usage in production
