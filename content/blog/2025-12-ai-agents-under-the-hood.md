---
title: "AI Agents Under the Hood: What They Actually Do (Not the Hype Version)"
date: "2025-12-11"
summary: "Everyone talks about AI agents. Few understand how they work. Here's a developer-first breakdown of tools, loops, memory, state, and why most agents explode at 2am."
---

Agents aren't magic. They're:

1. a planner  
2. an executor  
3. a memory layer  
4. a loop holding it together with duct tape  

## 🤖 What an agent *is*

An AI agent is:

> an LLM that can call tools, inspect results, decide next actions, and loop until done.

## 🛠️ Tools

Tools are functions the LLM can call:

- Python  
- APIs  
- SQL  
- file operations  

LLMs with tools = applications.  
LLMs without tools = chatbots.

## 🔁 The loop

1. LLM decides action  
2. Calls tool  
3. Gets output  
4. Reflects  
5. Replans  

The hard parts: retries, timeouts, bad JSON, hallucinated arguments, infinite loops.

## 🧠 Memory types

- short-term  
- working memory  
- long-term vector store  
- episodic history  
- procedural rules  

## 🧱 Industry architecture

Production agents use:

- planner LLM  
- executor  
- tool registry  
- memory layer  
- safety checks  
- observability / logs  

## 🐸 Bob + Chad

Bob = planner.  
Chad = executor.

Exactly how industry agents work.

