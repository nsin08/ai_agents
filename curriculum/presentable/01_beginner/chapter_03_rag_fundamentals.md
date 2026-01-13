# Chapter 3: RAG Fundamentals

**Level**: Beginner  
**Duration**: 30-45 minutes  
**Prerequisites**: [Chapter 2 - Your First Agent](./chapter_02_your_first_agent.md)  
**Lab**: [Lab 1 - RAG Fundamentals](../../../labs/01/README.md)

---

## Learning Objectives

By the end of this chapter, you will:

1. **Understand** what RAG (Retrieval-Augmented Generation) is and why it's critical
2. **Build** a simple document retrieval system
3. **Implement** vector embeddings for semantic search
4. **Compare** RAG vs. fine-tuning vs. prompt engineering
5. **Create** your first RAG-powered agent

---

## 1. The Knowledge Problem

### Why Agents Need RAG

Imagine you ask an agent: **"What's our company's vacation policy?"**

**Without RAG**:
```
Agent: I don't know your specific company policy. I can provide general information...
```
❌ The agent only knows what's in its training data (frozen in time).

**With RAG**:
```
Agent: According to your employee handbook (retrieved from documents), 
you get 15 days PTO annually, accruing at 1.25 days per month...
```
✅ The agent **retrieves** your company's actual policy document and **generates** an answer from it.

### The RAG Formula

```
RAG = Retrieve + Generate
```

1. **Retrieve**: Find relevant documents from your knowledge base
2. **Generate**: Use those documents as context for the LLM

**Real-world example**: Customer support agents that answer from your product documentation, not generic internet knowledge.

---

## 2. How RAG Works (Step by Step)

### The Full Pipeline

```
┌──────────────────────────────────────────────────────┐
│  1. USER QUERY                                       │
│     "What's our refund policy?"                      │
└────────────────────┬─────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────┐
│  2. EMBED QUERY                                      │
│     Convert text → numbers (vector)                  │
│     "refund policy" → [0.2, 0.8, 0.3, ...]          │
└────────────────────┬─────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────┐
│  3. VECTOR SEARCH                                    │
│     Find similar documents in database               │
│     Compare query vector to all doc vectors          │
└────────────────────┬─────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────┐
│  4. RETRIEVE TOP-K                                   │
│     Get 3-5 most relevant documents                  │
│     "Refund Policy.pdf" (similarity: 0.95)           │
└────────────────────┬─────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────┐
│  5. BUILD PROMPT                                     │
│     Inject documents into prompt:                    │
│     "Context: [Refund Policy doc]                    │
│      Question: What's our refund policy?"            │
└────────────────────┬─────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────┐
│  6. GENERATE ANSWER                                  │
│     LLM reads context + question → answer            │
│     "We offer full refunds within 30 days..."        │
└──────────────────────────────────────────────────────┘
```

---

## 3. Vector Embeddings: The Magic Behind RAG

### What Are Embeddings?

**Definition**: Embeddings convert text into numbers (vectors) that capture meaning.

**Example**:
```python
"dog" → [0.8, 0.2, 0.1, ...]      # High on "animal" dimension
"cat" → [0.7, 0.3, 0.1, ...]      # Similar vector (also animal)
"car" → [0.1, 0.1, 0.9, ...]      # Different (vehicle, not animal)
```

**Key insight**: Similar meanings → similar vectors.

### Why Embeddings Matter

**Keyword search** (old way):
```
Query: "vehicle"
Matches: Documents containing exactly "vehicle"
Misses: "car", "truck", "automobile" (different words, same meaning)
```

**Vector search** (RAG way):
```
Query: "vehicle" → [0.1, 0.1, 0.9, ...]
Matches: Documents with similar vectors
Finds: "car", "truck", "automobile" (semantic similarity!)
```

**Real example**:
- User asks: "How do I reset my password?"
- RAG finds: "Password Recovery Guide" (even though it doesn't contain word "reset")

---

## 4. Building Your First RAG Agent

### Step 1: Create a Knowledge Base

Create `labs/01/exercises/my_rag_agent.py`:

```python
"""
My First RAG Agent - Retrieves from documents before answering
"""
from agent_labs.orchestrator import AgentOrchestrator
from agent_labs.llm_providers import MockProvider
from agent_labs.memory import DocumentStore
from agent_labs.tools import VectorRetriever

# Knowledge base (your documents)
documents = [
    {
        "id": "doc1",
        "title": "Vacation Policy",
        "content": "Employees receive 15 days of paid vacation annually, accruing at 1.25 days per month."
    },
    {
        "id": "doc2",
        "title": "Sick Leave Policy",
        "content": "Employees receive 10 days of sick leave annually, non-accruing."
    },
    {
        "id": "doc3",
        "title": "Remote Work Policy",
        "content": "Employees may work remotely up to 3 days per week with manager approval."
    }
]

def main():
    # Create document store
    doc_store = DocumentStore()
    for doc in documents:
        doc_store.add_document(doc)
    
    # Create retriever
    retriever = VectorRetriever(doc_store, top_k=2)
    
    # Create agent with retriever
    provider = MockProvider()
    agent = AgentOrchestrator(
        llm_provider=provider,
        tools=[retriever]
    )
    
    # Query
    query = "How many vacation days do I get?"
    response = agent.run(query)
    
    print(f"Query: {query}")
    print(f"Answer: {response}")

if __name__ == "__main__":
    main()
```

**Run it**:
```bash
python labs/01/exercises/my_rag_agent.py
```

### Step 2: Understand What Happened

```
1. User query: "How many vacation days do I get?"
2. Retriever embedded query → vector
3. Searched document store for similar documents
4. Found "Vacation Policy" (highest similarity)
5. Injected "Vacation Policy" content into prompt
6. LLM generated: "Employees receive 15 days of paid vacation annually"
```

**Key point**: The agent **retrieved** the right document automatically, then **generated** an answer grounded in that document.

### Step 3: Add More Documents

```python
# Expand knowledge base
documents = [
    # ... existing docs ...
    {
        "id": "doc4",
        "title": "Parental Leave Policy",
        "content": "New parents receive 12 weeks of paid parental leave."
    },
    {
        "id": "doc5",
        "title": "Holiday Schedule",
        "content": "Company observes 10 federal holidays annually."
    }
]
```

Now the agent can answer questions about any of these topics!

---

## 5. RAG vs. Alternatives

### Option 1: Fine-Tuning
**What it is**: Retrain the LLM on your data  
**Pros**: Model "knows" your data directly  
**Cons**: Expensive, slow, hard to update, risk of hallucination

**When to use**: Specialized language/domain (legal, medical)

### Option 2: Prompt Engineering
**What it is**: Paste all docs in every prompt  
**Pros**: Simple, no extra tools needed  
**Cons**: Token limits (can't fit large docs), expensive

**When to use**: Small knowledge base (< 10 pages)

### Option 3: RAG
**What it is**: Retrieve relevant docs, then generate  
**Pros**: Scalable, fast, easy to update, cost-effective  
**Cons**: Depends on good retrieval

**When to use**: Most real-world applications ✅

### Comparison Table

| Approach | Cost | Speed | Updatable | Scalability | Best For |
|----------|------|-------|-----------|-------------|----------|
| **Fine-tuning** | $$$ | Slow | Hard | Poor | Specialized domains |
| **Prompt** | $ | Fast | Easy | Poor | Small knowledge |
| **RAG** | $ | Fast | Easy | Excellent | Most use cases ✅ |

---

## 6. Hands-On Exercises

### Exercise 1: Build a FAQ Bot

Create a knowledge base of common questions:

```python
documents = [
    {"id": "faq1", "content": "Q: How do I reset my password? A: Click 'Forgot Password' on the login page."},
    {"id": "faq2", "content": "Q: How do I update my profile? A: Go to Settings > Profile > Edit."},
    {"id": "faq3", "content": "Q: How do I delete my account? A: Contact support at support@company.com."}
]

# Build RAG agent
# Query: "I forgot my password"
# Expected: Agent retrieves faq1 and answers with reset instructions
```

### Exercise 2: Test Semantic Search

Query with different words but same meaning:

```python
queries = [
    "How many days off do I get?",           # "days off" = vacation
    "What's the PTO policy?",                # "PTO" = paid time off
    "When can I take a break from work?",    # indirect phrasing
]

# All should retrieve "Vacation Policy" document
```

### Exercise 3: Handle "No Match" Cases

Query something not in knowledge base:

```python
query = "What's the company's stock price?"

# Agent should respond: "I don't have information about that in my knowledge base."
```

Implement this by checking retrieval scores—if all are below threshold (e.g., 0.5), say "I don't know."

---

## 7. Common RAG Challenges

### Challenge 1: Poor Retrieval Quality
**Problem**: Agent retrieves wrong documents  
**Causes**: 
- Embeddings don't capture domain-specific meaning
- top_k is too low (not enough context) or too high (noise)

**Solution**: 
- Use domain-specific embedding models
- Tune `top_k` (try 3-5)
- Add metadata filters (dates, categories)

### Challenge 2: Chunking Issues
**Problem**: Documents are too long to fit in context  
**Solution**: Split into smaller chunks (500-1000 words)

```python
def chunk_document(text, chunk_size=500):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i+chunk_size]))
    return chunks
```

### Challenge 3: Hallucination
**Problem**: Agent makes up facts not in retrieved docs  
**Solution**: Prompt engineering

```python
system_prompt = """
You are a helpful assistant. Answer ONLY using the provided context.
If the answer is not in the context, say "I don't have that information."
DO NOT make up information.
"""
```

---

## 8. Key Concepts Summary

| Concept | What It Is | Why It Matters |
|---------|------------|----------------|
| **RAG** | Retrieve + Generate | Grounds answers in your data |
| **Embeddings** | Text → numbers (vectors) | Enables semantic search |
| **Vector Search** | Find similar vectors | Better than keyword matching |
| **Document Store** | Knowledge base | Where your docs live |
| **top_k** | Number of docs to retrieve | Balances context vs. noise |

---

## 9. Glossary

- **RAG**: Retrieval-Augmented Generation (retrieve docs → generate answer)
- **Embedding**: Numeric representation of text that captures meaning
- **Vector**: Array of numbers (e.g., [0.2, 0.8, 0.3])
- **Semantic Search**: Finding by meaning, not exact keywords
- **Document Store**: Database of documents for retrieval
- **top_k**: Number of most relevant documents to retrieve
- **Hallucination**: When LLM makes up facts not in data

---

## 10. What's Next?

✅ **You've completed**: Building a RAG-powered agent  
🎯 **Next chapter**: [Chapter 4 - Tool Integration](./chapter_04_tool_integration.md)  
🔬 **Next lab**: [Lab 2 - Tool Integration](../../../labs/02/README.md)

### Skills Unlocked
- ✅ Understand RAG architecture
- ✅ Build document retrieval systems
- ✅ Use vector embeddings for semantic search
- ✅ Create knowledge-grounded agents
- ✅ Handle "no match" scenarios gracefully

### Preview: Chapter 4 (Tools)
In the next chapter, you'll:
- Give agents the ability to take **actions** (not just answer)
- Build tools for APIs, databases, calculations
- Implement tool selection logic
- Handle multi-step workflows with tools

**The Big Idea**: RAG gives agents knowledge. **Tools give agents power.**

---

## 11. Self-Assessment Quiz

1. **What does RAG stand for?**
   - A) Random Answer Generation
   - B) Retrieval-Augmented Generation
   - C) Rapid Agent Gateway
   - D) Recursive Algorithm Grid

2. **What are embeddings?**
   - A) Fancy words for databases
   - B) Numeric representations of text meaning
   - C) LLM responses
   - D) Error messages

3. **Why is RAG better than pasting all docs in every prompt?**
   - A) It's not—pasting is always better
   - B) Token limits and cost (RAG only sends relevant docs)
   - C) RAG is slower
   - D) No reason

4. **What does top_k=3 mean?**
   - A) Use 3 LLMs
   - B) Retrieve the 3 most relevant documents
   - C) Limit answers to 3 words
   - D) Run 3 times

5. **What's semantic search?**
   - A) Exact keyword matching
   - B) Finding by meaning (similar vectors)
   - C) Random search
   - D) Database queries

6. **When should you use RAG over fine-tuning?**
   - A) Never—fine-tuning is always better
   - B) When you need updatable, scalable knowledge (most cases)
   - C) Only on weekends
   - D) When you have no data

7. **What happens if retrieved docs don't answer the question?**
   - A) Agent crashes
   - B) Agent should say "I don't have that information"
   - C) Agent always makes something up
   - D) Nothing—retrieval always works

8. **What's a DocumentStore?**
   - A) Physical warehouse
   - B) Database of documents for retrieval
   - C) LLM provider
   - D) Testing tool

9. **Why chunk large documents?**
   - A) To make them look nicer
   - B) LLMs have token limits—can't process huge docs
   - C) Chunking is not necessary
   - D) To increase cost

10. **What's the RAG pipeline order?**
    - A) Generate → Retrieve → Embed
    - B) Embed query → Search → Retrieve → Generate
    - C) Search → Embed → Retrieve → Generate
    - D) Retrieve → Embed → Generate → Search

### Answers
1. B, 2. B, 3. B, 4. B, 5. B, 6. B, 7. B, 8. B, 9. B, 10. B

---

## Further Reading

- [Lab 1 - RAG Fundamentals (Full Implementation)](../../../labs/01/README.md)
- [Vector Databases Explained](https://www.pinecone.io/learn/vector-database/)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [RAG Research Paper](https://arxiv.org/abs/2005.11401)

---

**Chapter Complete!** 🎉  
You've learned how to ground agent answers in your own documents using RAG!

**Next**: [Chapter 4 - Tool Integration →](./chapter_04_tool_integration.md)

---

*Estimated reading time: 25 minutes*  
*Hands-on exercises: 15-20 minutes*  
*Total chapter time: 40-45 minutes*
