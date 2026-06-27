# Homework 3: Orchestration with Kestra

This homework focuses on AI orchestration with Kestra, including AI Copilot, RAG workflows, token usage monitoring, and deterministic workflow design.

## Q1

Question: Why does Kestra AI Copilot generate better Kestra flows than a general ChatGPT prompt?

Answer: AI Copilot has access to current Kestra plugin documentation.

## Q2

Question: What is the non-RAG response about Kestra 1.1 features like?

Answer: Vague, generic, or fabricated — the model guesses from training data.

The non-RAG response listed generic or inaccurate features, while the RAG version used retrieved Kestra 1.1 release documentation and produced a grounded answer.

## Q3

Run: `4_simple_agent` with `summary_length = short`

Token usage:

- Multilingual Agent input tokens: 282
- Multilingual Agent output tokens: 84
- Multilingual Agent total tokens: 366

Answer: 60-100 tokens

## Q4

Comparison:

- `summary_length = short`: 84 output tokens
- `summary_length = long`: 208 output tokens

Ratio:

208 / 84 ≈ 2.48x

Answer: 2-5x more

## Q5

Changed `english_brevity` prompt from exactly 1 sentence to exactly 3 sentences.

Both runs used `summary_length = long`.

Comparison:

- Original 1-sentence version: 47 output tokens
- 3-sentence version: 98 output tokens

Ratio:

98 / 47 ≈ 2.09x

Answer: 2-4x more

## Q6

Question: For production workflows requiring deterministic, repeatable results and strict compliance, what should be used?

Answer: Use traditional task-based workflows for predictability/auditability.