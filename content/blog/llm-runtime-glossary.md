---
title: "LLM Runtime Glossary: The Stuff Nobody Explains"
date: "2025-12-17"
summary: "A plain-English glossary of LLM runtime, API, and inference terms you actually encounter when building real systems with local and hosted models."
---

This glossary exists for one reason:  
**most AI resources skip the boring but critical layer.**

These are the terms you keep bumping into once you stop doing demos and start shipping systems.

Read this slowly. Revisit it often.

---

## API & INTERFACE LAYER

### `/api/generate`
A **single-prompt → single-output** endpoint.

- No roles (`system`, `user`, `assistant`)
- Lower overhead
- Easier to reason about
- Ideal for:
  - classification
  - scoring
  - extraction
  - routing decisions

**Mental model:**  
> Call it like a function, treat output as *untrusted text*.

---

### `/api/chat`
A **conversation-oriented** endpoint.

- Accepts structured messages with roles
- Maintains conversational context
- More tokens, more cost, more variance

**Use when:**
- You need memory of prior turns
- You want assistant-style responses
- You are building a UI chat experience

---

### Streaming
Receiving tokens as they are generated.

- Faster *perceived* response
- More complex handling
- Harder to retry cleanly

**Rule of thumb:**  
> Stream for UX, not for agents.

---

## CONTEXT & TOKENS

### Token
A chunk of text the model processes (not words).

- “hello” ≠ 1 token
- punctuation, spaces, emojis all count

---

### Context Window (`num_ctx`)
Maximum number of tokens the model can *see at once*.

Includes:
- prompt
- system instructions
- conversation history
- retrieved documents (RAG)
- tool outputs

**Too small:** model forgets things  
**Too large:** slow, RAM-heavy, can freeze local machines

---

### Truncation
When older tokens are silently dropped to fit the context window.

**Danger:**  
> The model doesn’t tell you what it forgot.

---

## GENERATION CONTROLS (THE KNOBS)

### `num_predict`
Maximum number of tokens the model is allowed to generate.

- Hard stop
- Prevents runaway responses
- Protects latency and memory

---

### Temperature
Controls randomness.

- `0.0 – 0.2` → deterministic, boring, safe
- `0.3 – 0.6` → balanced
- `0.7+` → creative, risky, vibes

**Never use high temperature for decisions.**

---

### `top_p` (Nucleus Sampling)
Probability cutoff for token selection.

- Lower = safer, more focused
- Higher = more diverse, more nonsense

Often used **instead of** temperature, not with it.

---

### `top_k`
Limits sampling to the top *K* most likely tokens.

- Smaller = stricter
- Larger = looser

Less commonly used now than `top_p`.

---

### Repeat Penalty
Discourages repeating the same tokens.

- Prevents loops
- Prevents “As an AI language model…” spam

---

### Mirostat
An adaptive sampling algorithm.

- Tries to maintain consistent “surprise”
- Reduces tuning guesswork
- More stable long generations

Good for chat, rarely needed for agents.

---

## MODEL & ENGINE REALITY

### Model
The neural network + weights.

Examples:
- LLaMA
- Qwen
- Mistral
- Gemma

Models **do not** define APIs. Engines do.

---

### Engine / Runtime
The software that runs the model.

Examples:
- Ollama
- llama.cpp
- vLLM
- OpenAI servers

This is where:
- `num_ctx` limits live
- performance constraints come from
- crashes originate

---

### Quantization
Reducing model precision to save memory.

- `Q4` / `Q5` / `Q8`
- Smaller = faster, dumber
- Larger = slower, smarter

Local reality:  
> Quantization is why your laptop can run models at all.

---

### VRAM / RAM Pressure
Local models compete with your OS.

Symptoms:
- UI freezes
- mouse lag
- fans screaming
- kernel panic (worst case)

**This is not a bug. It’s physics.**

---

## AGENT & SYSTEM DESIGN

### Determinism
Same input → same output (or close enough).

LLMs are **not deterministic by default**.

You must enforce it via:
- low temperature
- constrained prompts
- validation
- retries

---

### Retry Logic
Calling the model again when output is invalid.

Common strategies:
- fixed retries
- escalating strictness
- majority voting

---

### Majority Voting
Run the same prompt multiple times, pick the consensus.

Useful for:
- classification
- extraction
- weak signals

Costs more tokens, buys confidence.

---

### Abstention / `NONE`
Allowing the model to say:
> “I don’t know” or “No action required”

Critical for safety and trust.

---

### Router
A deterministic step that decides **what happens next**.

Examples:
- which tool to run
- which model to call
- whether to call an LLM at all

**Routers should be boring.**

---

### Policy Layer
Rules that override model intent.

- “Even if the model says yes, we say no”
- Safety, cost, legality, scope control

This layer should **not** be AI.

---

### Tool Use
Letting the model request actions:
- database queries
- API calls
- scripts

The model suggests.  
**Your code decides.**

---

## COMMON TRAPS

### “LLMs are just functions”
False.

They are:
- probabilistic
- stateful
- failure-prone

Treat them like **unreliable narrators**.

---

### “The model will behave if I prompt it well”
Also false.

Prompting helps.  
**Architecture matters more.**

---

### “Bigger model = better system”
No.

- Wrong defaults beat big models
- Determinism beats creativity
- Guardrails beat vibes

---

## FINAL MENTAL MODEL

Think in layers:

1. **Transport** – how you talk to the model  
2. **Inference** – how tokens are generated  
3. **Control** – how your system stays sane  

If you understand those three,  
you are no longer guessing.

---

*This glossary will grow. Real systems always do.*
