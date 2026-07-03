# Workload: Internal Support Ticket Triage Assistant

## What it does

We're building a Claude-powered assistant that reads incoming support tickets and drafts a suggested response + priority tag for a human agent to review before sending. It's not fully autonomous — a human always reviews before anything goes to the customer.

## Volume

- ~4,000 tickets per day
- Growing roughly 10% month over month, but estimate based on current volume for now

## Prompt shape

- Every request includes a fairly large system prompt: our support policy doc, tone guidelines, and a product FAQ reference — roughly 6,000 tokens total, and it's identical across every single request.
- The ticket-specific content (the customer's message, account context) adds another 800 tokens on average.
- So average input per request is around 6,800 tokens.
- Output is a suggested response draft plus a priority tag — averages around 350 tokens.

## Latency requirements

- Agents review tickets throughout the day during business hours, not instantly on arrival — a few minutes of delay is completely fine.
- Nothing here is real-time/user-facing; customers never see the model's output directly.

## Complexity spread

- Most tickets (~70%) are routine — password resets, order status, simple FAQ-type questions.
- The remaining ~30% are more complex — billing disputes, multi-part technical issues — and probably need a stronger model.
- Currently we run everything through one model regardless of complexity.

## Model currently in use

Sonnet, for everything, no tiering.

## Question

We want to know: what would we actually save by turning on prompt caching for the shared system prompt, and does it make sense to move this whole workload to the Batch API given the relaxed latency requirement? Also curious if splitting simple vs. complex tickets across two model tiers is worth the added routing complexity.
