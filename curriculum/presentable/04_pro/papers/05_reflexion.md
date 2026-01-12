# Paper Summary: Reflexion - Language Agents with Verbal Reinforcement Learning

- arXiv: 2303.11366 - https://arxiv.org/abs/2303.11366
- Published: 2023-03-20

## One-paragraph takeaway

Reflexion shows that an agent can improve over repeated attempts by writing "reflection" text about what went wrong and feeding that reflection into subsequent trials. The key engineering lesson is not that free-form reflection is magical, but that you need a place in your architecture for structured post-mortems: capture failure signals, compress them into actionable guidance, and reuse that guidance as a first-class artifact (like a policy or a test). In production, reflections should be bounded, testable, and tied to observed failures.

## What the paper contributes (agent-relevant)

- A loop that turns outcomes into feedback and feedback into improved next attempts.
- Demonstrates gains on tasks where naive retrying repeats the same mistake.
- Encourages treating agent memory as "learning from experience" (not just chat history).

## How to apply Reflexion safely (practical)

1. Prefer structured reflection over free-form reflection.
   - "Failure category", "root cause", "fix", "new guardrail".
2. Store reflections with provenance.
   - Link to: input, tool trace, model version, evaluation score.
3. Convert reflections into constraints.
   - Update prompts, tool allowlists, routing rules, or tests.
4. Cap and decay.
   - Limit how many reflections are carried into a run.
   - Expire stale reflections when tools/models change.

## Failure modes to watch

- Reflection hallucination: the model invents a reason that was not observed.
- Over-generalization: reflection becomes a hard rule that blocks valid behavior.
- Memory poisoning: storing untrusted user content as "lessons learned".

## Evaluation guidance

- Compare:
  - baseline success rate
  - naive retry success rate
  - reflection-enabled retry success rate
- Track stability: does reflection reduce variance across runs?

## How it maps to this curriculum

- Chapter 03 uses Reflexion to motivate a "post-run feedback loop" pattern (logs -> insights -> constraints).
- Chapter 04 discusses self-improving agents as a frontier, and why evaluation gates must stay in control.

