---
title: "Lesson 1: LLMs Are Not Functions (And Why That Changes Everything)"
date: "2025-12-14"
summary: "My first real AI engineering lesson: large language models are not functions. They're probabilistic generators — and unless you constrain them, they will break your system."
---

I started this project assuming an LLM call worked like a normal function:

```
input → output
```

Same input, same output. Simple.

That assumption lasted about half a day.

What followed was my **first real AI engineering lesson** — not about prompts, but about *control*.

---

## The mistake most people make

Most people (including me, initially) treat LLMs like this:

- write a prompt  
- call the API  
- parse the text  
- hope it behaves  

That works… until it doesn’t.

LLMs are **not deterministic functions**. They are **probabilistic generators**. If you don’t explicitly constrain them, they will:

- change answers  
- change structure  
- emit multiple outputs  
- break contracts  
- fail in ways that are hard to reproduce  

I hit all of those in Lesson 1.

---

## LLMs are not functions

A real function looks like this:

```
f(x) → y
```

An LLM call is closer to:

```
f(x, params, runtime_state) → {y₁, y₂, y₃, ...}
```

The model produces a *distribution of possible continuations*.  
Your job as an engineer is to decide **which ones you will accept**.

Until you do that, you don’t have a system — you have a demo.

---

## Temperature is not creativity — it is risk

The first control knob I learned to respect was **temperature**.

- `temperature = 0`  
  → greedy decoding  
  → pick the single most likely token every time  

- higher temperature  
  → more exploration  
  → more variation  
  → more structural deviation  

At high temperature, I didn’t just get different answers — I got:

- extra text after JSON  
- multiple outputs in a single response  
- broken parsing  
- runtime crashes  

That was the moment it clicked:

> **Randomness doesn’t just affect content.  
> It affects structure, control flow, and contracts.**

---

## Why schema matters (and why it still isn’t magic)

I added a strict JSON schema to enforce output shape:

- exactly one key  
- enum-only values  
- no extra properties  

That helped — but it didn’t make the system bulletproof.

At high temperature, the model still managed to:

- emit multiple valid JSON objects  
- concatenate them into one string  
- break `json.loads()`  

The fix wasn’t “better prompts”.  
The fix was **validation and assumptions**.

---

## The real abstraction

The correct abstraction is not:

```
LLM → answer
```

It is:

```
LLM → candidates → validation → selection → result
```

Only after validation does the system behave like a function.

That wrapper — not the model — is the real unit of engineering.

---

## Decision paths vs generative paths

This lesson led to a clean rule I now follow:

- **Decision-making paths**  
  (classification, routing, tool selection)  
  → temperature = 0  
  → strict schema  
  → exactly one output  

- **Generative paths**  
  (blog posts, summaries, ideas)  
  → higher temperature  
  → variation is a feature  

Writing a blog post should be creative.  
Choosing the correct tool should not.

---

## The takeaway

Lesson 1 wasn’t about prompt engineering.

It was about this shift:

> **LLMs are unreliable by default.  
> Reliable systems wrap them until they behave like functions.**

That means:
- constraints  
- contracts  
- validation  
- retries  
- and explicit assumptions  

Once you accept that, AI stops feeling magical — and starts feeling like engineering.

[View On Github](https://github.com/ghostfrog-ltd/ai-engineering-001)

---

*Lesson 2 will cover retries, voting, and how to design systems that stay reliable even when the model is uncertain.*





