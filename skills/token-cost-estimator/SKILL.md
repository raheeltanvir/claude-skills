---
name: token-cost-estimator
description: Estimates and compares Claude API costs across different optimization strategies — prompt caching, the Batch API, model tiering (Haiku/Sonnet/Opus mix), and RAG vs. long-context tradeoffs. Use this whenever the user describes an LLM workload (requests per day/month, typical input/output size, whether prompts share a common prefix, latency requirements) and wants to know what it will cost, whether prompt caching or batching is worth it, or how to reduce spend. Trigger on phrases like "how much will this cost", "estimate API costs", "is prompt caching worth it", "should I use batch API", "which model should I use for this", "RAG vs long context", or any request to size/budget a Claude-powered feature or pipeline. Always pull current per-model pricing from Anthropic's docs rather than relying on memorized numbers, since pricing changes.
---

# Token Economics / Cost Estimator

Help the user estimate real API spend and compare cost-reduction strategies, grounded in current pricing — not memorized numbers, which go stale.

## Step 1: Get current pricing

Before estimating anything, check `/mnt/skills/public/product-self-knowledge/SKILL.md` if available, and otherwise web-search Anthropic's current pricing page (docs.claude.com or anthropic.com/pricing) for:
- Per-model price per million input/output tokens (Haiku, Sonnet, Opus — and any newer tiers)
- Prompt caching discount rate (cache write premium and cache read discount)
- Batch API discount rate

Pricing changes over time — never estimate off of a remembered number without verifying it's current.

## Step 2: Gather the workload shape

Ask only for what you don't already have (don't re-ask if the user already stated it):
- Requests per day (or month)
- Typical input tokens per request, and typical output tokens per request
- Whether requests share a common prefix/system prompt (candidate for caching) and roughly what fraction of the prompt that prefix represents
- Latency requirement: real-time (user-facing) or can tolerate async processing (batch candidate)
- Task complexity spread: is it uniform, or does it range from simple lookups to complex reasoning (tiering candidate)

If the user gives a rough/order-of-magnitude description instead of exact numbers, work with that — precision to the token isn't the point, directional cost comparison is.

## Step 3: Calculate

Use `scripts/estimate_cost.py` to compute baseline cost and cost under each applicable strategy. Run it, don't hand-calculate — token math across multiple strategies is exactly the kind of thing that's easy to get subtly wrong by hand.

```bash
python3 scripts/estimate_cost.py \
  --requests-per-day <N> \
  --input-tokens <N> \
  --output-tokens <N> \
  --input-price-per-mtok <price> \
  --output-price-per-mtok <price> \
  --cached-fraction <0-1, optional> \
  --cache-discount <0-1, default 0.9> \
  --cache-write-premium <e.g. 0.25, default 0.25> \
  --batch-discount <0-1, default 0.5>
```

Run it once for the baseline (no cached-fraction) and again with caching/batch flags to produce a comparison. See `scripts/estimate_cost.py --help` for all flags.

## Step 4: Present a comparison, not just a number

Structure the output as a table:

| Strategy | Est. monthly cost | Savings vs. baseline | Tradeoff |
|---|---|---|---|
| Baseline (no optimization) | $X | — | — |
| + Prompt caching | $X | -X% | Cache write premium on first hit; only pays off if prefix is reused frequently enough |
| + Batch API | $X | -X% | ~24hr turnaround, not for user-facing latency |
| + Model tiering | $X | -X% | Requires reliable complexity routing logic |

Then give a direct recommendation for *this* workload — not a generic "caching is good" statement. Caching only pays off above a reuse-frequency threshold; batch only makes sense if latency truly doesn't matter; tiering only helps if complexity is genuinely bimodal. Say which of these actually apply here and why.

## Step 5: Flag the RAG vs. long-context tradeoff when relevant

If the user's workload involves large reference documents/knowledge bases repeated across requests, this is a separate axis from caching:
- **Long context + caching**: simpler architecture, but pays input-token cost (even discounted) on every request and has a context-window ceiling.
- **RAG**: cheaper per-request once built, but adds retrieval infrastructure, embedding costs, and retrieval-quality risk (missed chunks).

Don't recommend one categorically — note that the crossover point depends on request volume and how static the reference material is, and estimate roughly where their workload falls.
