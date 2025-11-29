---
title: "GhostFrog: Building a Data-Driven eBay Arbitrage Engine"
date: "2025-11-27"
summary: "I built a full pipeline that scrapes eBay listings, classifies products, calculates ROI, and sends alerts."
---

GhostFrog started as a tiny “let’s scrape eBay consoles” idea.  
It grew into a full arbitrage intelligence system with:

- multiple scraper adapters (consoles, Apple, bikes, vans, etc.)
- Postgres pipelines for listings, comps, snapshots
- ROI calculation and modelling
- alert thresholds (profit, ROI, ‘insane deal’ markers)
- Telegram alerts (siren, digest, firehose)
- classification logic for product types
- a niche-based architecture (lego, consoles, vehicles)

### 🧩 Why it works
Cheap flips follow patterns.  
But 99% of people don’t see them.

GhostFrog collects:

- listing data  
- price history  
- auction time left  
- expected profit  
- expected ROI  
- repair/resale assumptions  

It then sends:

- ROI alerts  
- last-hour sirens  
- summaries  
- custom webhooks  

I also built a **unified webhook receiver** on my portfolio site to capture eBay events.

GhostFrog is now the backbone of my data-driven flipping experiments — and one of the best engineering projects I’ve ever built.
