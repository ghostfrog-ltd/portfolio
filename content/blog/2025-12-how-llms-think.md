---
title: "How LLMs Actually Work: The Mental Model Every AI Developer Needs"
date: "2025-12-11"
summary: "Forget the mystical hype. Here's a blunt, developer-friendly explanation of how transformers think, plan, and hallucinate."
---

## 🔤 1. Everything is tokens

LLMs don't see sentences. They see token IDs.  
This is why:

- context length matters  
- long prompts cost more  
- models lose track of earlier text  

## 🧠 2. Attention

Attention lets each token inspect every other token and decide relevance.

Gives you:

- reasoning  
- relationships  
- instruction following  

Also causes:

- hallucinations (wrong patterns reinforced)

## 🪜 3. Transformer layers

Layers refine meaning:

- lower → syntax  
- middle → facts  
- upper → reasoning  

## 🧩 4. Why LLMs hallucinate

Because they **predict**, they don’t **verify**.

Agents fix this with:

- tools  
- retrieval  
- planning loops  

## 📦 5. Why small models often win

Tools + retrieval > raw model size.

