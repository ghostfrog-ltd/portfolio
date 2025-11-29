---
title: "The Birth of Bob + Chad: My Local Agentic Coding Environment"
date: "2025-11-29"
summary: "I built a self-improving AI pair-programming system that runs locally, fixes its own code, and evolves over time."
---

For years I’ve worked as a Magento developer, but 2024–2025 changed everything for me.  
AI moved beyond “chatbots” and became something closer to an *engineer*.

I wanted something more than ChatGPT.  
I wanted a system that could:

- read my code
- plan changes
- execute tools
- fix mistakes
- and **improve itself**

So I built it.

### 🧠 Bob — The Planner
Bob is the reasoning model.  
He analyses my code, designs JSON plans, and decides which tools Chad should run.  
He’s fast, structured, and has a custom rules engine I built in markdown files so he can learn from failures.

### 🔧 Chad — The Junior Engineer
Chad executes Bob’s plans using:

- codemod tools  
- run_python_script  
- file read/write tooling  
- jailed paths to prevent damage  
- pytest validation  
- automatic self-repair cycles  

This makes the system feel like a *small AI engineering team* on my laptop.

### 🔁 Self-Improvement
I added:

- `self_cycle` to auto-generate improvement tickets  
- `teach_rule` for Bob to store new heuristics  
- automatic detection of failure patterns  
- safe file paths  
- execution logs

The entire GhostFrog architecture now runs agentically on my Mac.

This project changed how I write code and how fast I build things.  
And it’s only the beginning.
