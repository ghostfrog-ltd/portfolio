---
date: 2025-12-27
summary: After proving the concept with a first-pass eBay scraping
  system, I'm rebuilding it properly using LangGraph. This post explains
  why I moved on from V1, what a pipeline actually is, and how
  orchestration sets the foundation for reliable AI-driven systems.
title: "From eBay V1 Scripts to a Proper Pipeline: Introducing LangGraph
  as the Orchestrator"
---

## eBay V1 Did Its Job --- and That's Exactly Why It Had to Go

The original eBay implementation (V1) was successful by the only metric
that matters early on:

> **It proved the idea was viable.**

Listings could be fetched.\
Basic logic worked.\
The data had value.

But V1 was also what most early systems are: - tightly coupled scripts -
implicit control flow - scheduling logic mixed with business logic -
hard to visualise - harder to extend safely

That's fine for validation.\
It's not fine for building something that lasts.

So instead of bolting more logic onto V1, I made a clean decision:

**stop iterating --- start rebuilding properly.**

------------------------------------------------------------------------

## The Architectural Shift: Scripts → Pipelines

The key change in V2 is not "more AI".

It's **orchestration**.

Rather than one-off scripts, the system is now organised around
**pipelines**: - named - inspectable - deterministic -
single-responsibility

Each pipeline: - runs once - mutates explicit state - exits cleanly -
can be called by anything (CLI, cron, another pipeline)

This is the foundation required before adding reasoning, agents, or
automation.

------------------------------------------------------------------------

## Why LangGraph

LangGraph isn't being used here for hype or novelty.

It solves a very specific problem:

> How do you express *controlled iteration, branching, and termination*
> in a way that remains debuggable?

LangGraph gives me: - explicit nodes - explicit edges - visible stop
conditions - a state object I can reason about - visualisation of the
flow when needed

Most importantly:\
**the control flow is no longer implicit in a loop.**

------------------------------------------------------------------------

## The First V2 Pipeline: Retrieve

The first rebuilt pipeline is intentionally boring:

**Retrieve listings from multiple sources, safely.**

What it does: 1. Iterates through a defined list of adapters (sources)
2. Checks whether each source is allowed to run (time-gated) 3.
Either: - skips it (with a reason and next allowed time), or - runs it
and records the scrape 4. Stops once all sources are processed

What it does *not* do: - no retries - no AI - no ranking - no
notifications

That restraint is deliberate.

------------------------------------------------------------------------

## Gating Lives Inside the Pipeline

One of the most important design decisions:

**Scheduling is external.\
Decision-making is internal.**

Each adapter checks: - when it last ran - how frequently it is allowed
to run - whether it is enabled

Because this logic lives *inside* the pipeline: - the pipeline can be
triggered frequently - APIs are never hammered - "no work to do" is a
valid, clean outcome

This enables a simple heartbeat to drive the system.

------------------------------------------------------------------------

## How the Pipeline Runs

The pipeline does not run by itself.

It is invoked.

Right now, that invocation is via CLI:

``` bash
python3 -m pipelines.listing.retrieve
```

Internally, that simply calls:

``` python
run(ebay_token=...)
```

Tomorrow, that caller could be: - a cron job - a long-running heartbeat
process - another pipeline - an API endpoint

The pipeline doesn't care --- and that's the point.

------------------------------------------------------------------------

## The Heartbeat Model

The correct mental model for V2 is:

> "Every N minutes, wake up and run the pipeline once."

The heartbeat is dumb.\
The pipeline is smart.

If everything is gated, nothing happens.\
If one source is ready, only that work runs.

This is how reliable ingestion systems are built in practice.

------------------------------------------------------------------------

## This Is Still Not an Agent (On Purpose)

At this stage: - there is no planning - no autonomous reasoning - no LLM
in the loop

That comes later.

Right now, the priority is **structural correctness**: - predictable
execution - inspectable state - clean termination - safe iteration

Agents built on top of shaky ingestion layers fail in uninteresting
ways.

This pipeline exists to make sure that doesn't happen.

------------------------------------------------------------------------

## What This Enables Next

With orchestration in place, the roadmap becomes straightforward:

1.  **Normalisation & storage pipeline**
2.  **Assessment pipeline** (LLM-assisted, confidence-gated)
3.  **Ranking & filtering**
4.  **Notification / alerting**
5.  **Chained orchestration via a single heartbeat**

Each pipeline will do one job, and do it well.

------------------------------------------------------------------------

## Closing Thought

eBay V1 wasn't a mistake.

It was a prototype.

V2 is about taking what worked, discarding what didn't, and rebuilding
the system on foundations that can support: - automation - AI
decision-making - and eventually, real users

LangGraph isn't the product.

It's the **orchestrator** that makes the product possible.
