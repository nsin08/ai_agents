"""
Prompt Template Library

Provides ready-to-use templates for common agent tasks:
- Q&A: Direct question answering
- Reasoning: Step-by-step problem solving
- Tool-Use: Structured action selection
- Few-Shot: In-context learning examples
- Classification: Category prediction
- Analysis: Document analysis and summarization
"""


class PromptTemplates:
    """Library of prompt templates for various agent tasks."""
    
    # Q&A Template: Direct question answering
    QA_TEMPLATE = """\
You are a helpful assistant. Answer the following question clearly and concisely.

Question: {question}
Context: {context}

Answer:"""
    
    # Reasoning Template: Chain-of-thought problem solving
    REASONING_TEMPLATE = """\
Solve this problem step by step.

Problem: {problem}

Step 1: Identify what we know
Step 2: Determine what we need to find
Step 3: Apply relevant formulas or logic
Step 4: Calculate the result
Step 5: Verify the answer

Solution:"""
    
    # Tool-Use Template: Structured action selection
    TOOL_USE_TEMPLATE = """\
You are an agent that can use tools to solve problems.

Available Tools:
{tools}

Task: {task}

Select the most appropriate tool and provide:
1. Tool Name: [which tool to use]
2. Reasoning: [why this tool is best]
3. Parameters: [required parameters]
4. Expected Outcome: [what the tool will return]

Response:"""
    
    # Sentiment Analysis Template: Few-shot classification
    SENTIMENT_ANALYSIS_TEMPLATE = """\
Classify the sentiment of the text as POSITIVE, NEGATIVE, or NEUTRAL.

Examples:
Text: "This product is amazing! Best purchase ever."
Sentiment: POSITIVE

Text: "Terrible experience. Would not recommend."
Sentiment: NEGATIVE

Text: "The item arrived on time."
Sentiment: NEUTRAL

Now classify:
Text: "{text}"
Sentiment:"""
    
    # Code Review Template: Structured code analysis
    CODE_REVIEW_TEMPLATE = """\
Role: You are a Python expert code reviewer.

Task: Review the following code for bugs and style issues.

Guidelines:
1. Identify critical bugs that could cause failures
2. Flag style issues that violate PEP 8
3. Suggest performance improvements
4. Check for security vulnerabilities

Format your response as:
1. Bugs: [list critical issues, or "None found"]
2. Style: [list style improvements, or "Meets PEP 8"]
3. Performance: [optimization opportunities, or "Good"]
4. Security: [security concerns, or "No issues found"]
5. Rating: [1-5 scale]

Code:
{code}

Review:"""
    
    # Summarization Template: Document condensing
    SUMMARIZATION_TEMPLATE = """\
Summarize the following document concisely.

Requirements:
- Keep summary to {max_length} words
- Preserve key information and main points
- Use clear, professional language
- Include numbers and specific facts

Document:
{document}

Summary:"""
    
    # Classification Template: Multi-class categorization
    CLASSIFICATION_TEMPLATE = """\
Classify the following text into one of these categories:
{categories}

Text: "{text}"

Provide:
1. Selected Category: [category name]
2. Confidence: [High/Medium/Low]
3. Reasoning: [brief explanation]

Classification:"""
    
    # Entity Extraction Template: Information extraction
    ENTITY_EXTRACTION_TEMPLATE = """\
Extract all entities of the specified types from the text.

Entity Types to Extract:
{entity_types}

Text: "{text}"

Format your response as:
[Entity Type]: [entity1, entity2, entity3]

Extraction:"""
    
    # Comparison Template: Contrast analysis
    COMPARISON_TEMPLATE = """\
Compare the following items across key dimensions.

Items: {items}
Dimensions: {dimensions}

Provide:
1. Similarities: [what they have in common]
2. Differences: [key distinctions]
3. Advantages of Item 1: [benefits]
4. Advantages of Item 2: [benefits]
5. Recommendation: [which is better for what use case]

Comparison:"""
    
    # Role-Play Template: Character-based interaction
    ROLE_PLAY_TEMPLATE = """\
You are a {role}.

Context: {context}

Your personality traits:
- {trait1}
- {trait2}
- {trait3}

User: {user_message}

Response (in character):"""
    
    # Analysis Template: Detailed examination
    ANALYSIS_TEMPLATE = """\
Provide a detailed analysis of the following:

Subject: {subject}

Required Sections:
1. Overview: [what it is]
2. Key Components: [important parts]
3. How It Works: [mechanism or process]
4. Strengths: [advantages]
5. Weaknesses: [limitations]
6. Use Cases: [applications]

Analysis:"""
    
    # Planning Template: Action planning
    PLANNING_TEMPLATE = """\
Create a detailed plan to achieve the following goal.

Goal: {goal}
Constraints: {constraints}
Timeline: {timeline}

Plan must include:
1. Objectives: [specific, measurable outcomes]
2. Steps: [ordered action items]
3. Resources: [what's needed]
4. Risks: [potential issues]
5. Milestones: [checkpoints]

Plan:"""


def get_template(name: str) -> str:
    """
    Get a template by name.
    
    Args:
        name: Template name (without 'TEMPLATE' suffix)
    
    Returns:
        Template string
    
    Raises:
        ValueError: If template not found
    """
    template_name = f"{name.upper()}_TEMPLATE"
    
    if not hasattr(PromptTemplates, template_name):
        available = _get_available_templates()
        raise ValueError(
            f"Template '{name}' not found. Available: {available}"
        )
    
    return getattr(PromptTemplates, template_name)


def _get_available_templates() -> list[str]:
    """Get list of available template names."""
    templates = []
    for attr in dir(PromptTemplates):
        if attr.endswith("_TEMPLATE") and not attr.startswith("_"):
            # Remove 'TEMPLATE' suffix and lowercase
            name = attr.replace("_TEMPLATE", "").lower()
            templates.append(name)
    return sorted(templates)


def list_templates() -> dict[str, str]:
    """
    Get all templates with brief descriptions.
    
    Returns:
        Dict of template names to descriptions
    """
    descriptions = {
        "qa": "Direct question answering with context",
        "reasoning": "Step-by-step problem solving (Chain-of-Thought)",
        "tool_use": "Structured tool selection and parameter specification",
        "sentiment_analysis": "Text sentiment classification (Few-shot learning)",
        "code_review": "Python code analysis and feedback",
        "summarization": "Document summarization to specified length",
        "classification": "Multi-class text categorization",
        "entity_extraction": "Named entity recognition and extraction",
        "comparison": "Comparative analysis of items",
        "role_play": "Character-based interaction",
        "analysis": "Detailed subject examination",
        "planning": "Goal achievement planning with milestones"
    }
    return descriptions


def build_few_shot_template(
    task_description: str,
    examples: list[dict],
    example_format: str,
    input_field: str
) -> str:
    """
    Build a few-shot template from examples.
    
    Args:
        task_description: Description of the task
        examples: List of example dicts
        example_format: Format string for each example (e.g. "Text: {text}\\nLabel: {label}")
        input_field: Name of field for user input (e.g. "text")
    
    Returns:
        Few-shot template string
    
    Raises:
        ValueError: If examples or format is invalid
    """
    if not examples:
        raise ValueError("At least one example required")
    
    if not input_field:
        raise ValueError("input_field required")
    
    # Format examples
    formatted_examples = []
    for example in examples:
        try:
            formatted = example_format.format(**example)
            formatted_examples.append(formatted)
        except KeyError as e:
            raise ValueError(f"Example missing required field: {e}")
    
    examples_text = "\n\n".join(formatted_examples)
    
    return f"""{task_description}

Examples:
{examples_text}

Now process:
{{{input_field}}}:"""
