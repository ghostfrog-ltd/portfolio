---
title: "The Planner–Executor Pattern in AI: Explained Simply"
date: "2025-11-15"
summary: "The core design that powers modern agent systems, including my own Bob + Chad setup."
---

The **Planner → Executor** pattern is the backbone of agent systems.

Here’s the breakdown:

## 🧠 1. Planner (Bob in my case)
Responsible for:
- analysing the goal  
- breaking it down  
- generating a structured plan  
- deciding which tools to use  
- describing expected outputs  

In English: *thinks before acting*.

## 🔧 2. Executor (Chad)
Responsible for:
- running tools  
- performing steps  
- modifying files  
- running scripts  
- catching errors  
- reporting results  

In English: *does the work*.

## 🔁 3. Two-way feedback loop
After executing steps:
- executor reports results  
- planner revises plan  
- executor keeps running  

This is what lets an agent recover from errors.

## 🧩 4. Why this works
Humans do this instinctively:
> "Let me think... ok I’ll do X, then Y, then Z."

LLMs don’t — unless you explicitly build this structure.

## 🚀 5. Why I built Bob + Chad this way
Because it mirrors how real engineering teams work:  
**one senior engineer + one junior engineer**.

And it works unbelievably well.
