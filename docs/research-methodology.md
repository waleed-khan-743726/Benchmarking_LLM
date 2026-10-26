# Research methodology

## Question

How accurately and efficiently can small, locally runnable open-weight models translate navigation instructions into the same validated task schema, and what effect do prompt reduction, deterministic preprocessing, response validation, and caching have on system-level performance?

## Experimental unit

One run is one model/configuration/scenario/instruction/repetition combination. Models run sequentially. Raw output, parse status, validation status, latency, token data when available, memory observations, prompt version, model tag, scenario seed, planner metrics, and failure reason are retained.

## Conditions

- **Baseline:** full documented prompt, no response cache, standard validation, one inference per eligible task.
- **Optimized:** concise prompt, deterministic normalization, schema-aware parsing, input/model/prompt keyed cache, and no repeat inference for identical tasks.

Both conditions use the same scenario, instruction, model tag, generation settings, timeout policy, and planning algorithm. Warm-up runs are recorded separately and excluded from steady-state summaries.

## Correctness

An interpretation is correct only when it matches the scenario's expected structured intent and passes schema/map validation. A navigation success additionally requires a validator-approved A* route and safe simulated completion. Failures remain in the denominator.

## Reproducibility

Scenarios use fixed seeds and versioned JSON. Runs retain application, prompt, scenario, model, and environment identifiers. Offline-mode tests prove deterministic behavior but are never reported as LLM benchmark results.

