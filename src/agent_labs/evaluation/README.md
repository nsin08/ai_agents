# Evaluation Framework

Utilities to evaluate agent outputs using metrics, benchmarks, and reports.

## Components

- `Metric`: abstract base class for scorers.
- Built-in scorers: `ExactMatchScorer`, `SimilarityScorer`, `RougeScorer` (mock).
- `BenchmarkRunner`: batch evaluation runner.
- `EvaluationResult`: score, explanation, details.
- Reports: JSON + Markdown.
- Visualization: score distribution + ASCII comparison chart.

## Scorer Example

```python
from agent_labs.evaluation import ExactMatchScorer

scorer = ExactMatchScorer()
result = scorer.score("hello", "hello")
print(result.score)
```

## Benchmark Runner Example

```python
from agent_labs.evaluation import BenchmarkRunner, BenchmarkCase, SimilarityScorer

runner = BenchmarkRunner(metric=SimilarityScorer())
cases = [
    BenchmarkCase(case_id="1", input_text="Q1", reference="Answer one"),
]
outputs = {"1": "Answer one"}
result = runner.run(cases, outputs)
```

## Report Example

```python
from agent_labs.evaluation import report_markdown

markdown = report_markdown(result.cases)
print(markdown)
```

## Notes

- Scorers are deterministic and mock-friendly.
- Visualization uses simple ASCII for Phase 1 (no external deps).
