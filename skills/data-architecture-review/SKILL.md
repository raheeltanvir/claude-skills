---
name: data-architecture-review
description: Reviews a proposed or existing data/analytics architecture (lakehouse, data warehouse, data mesh, migration plan, or platform design) the way a staff-level data architect would, and produces a structured findings report. Use this whenever the user shares an architecture diagram, design doc, migration plan, or written description of a data platform and wants feedback, a second opinion, a risk assessment, or help preparing for an architecture review board. Trigger on phrases like "review this architecture", "does this design make sense", "what am I missing", "architecture review board", "lakehouse design", "data mesh", "migration plan", or when the user pastes/uploads a system design and asks what Claude thinks. Also use proactively when the user is designing a data platform from scratch and would benefit from a structured evaluation rather than freeform commentary.
---

# Data Architecture Review

Evaluate data platform architectures with the rigor of a staff/principal data architect doing a design review — not a generic "looks good" summary. The goal is to surface real risks and open questions the way an experienced reviewer would in an architecture review board (ARB), not to rubber-stamp the design.

## When to go deep vs. go light

- If the user shares a full design (diagram, doc, or detailed description covering multiple layers/components), run the **full structured review** below.
- If the user asks a narrow question about one aspect (e.g., "does Kafka make sense here for CDC?"), answer that specifically using the relevant checklist section instead of running the whole framework — don't force structure where it isn't needed.

## Step 1: Understand what's being proposed

Before critiquing, make sure you actually understand:
- What's the source system landscape (legacy DW, operational DBs, SaaS, streaming)?
- What's the target platform (lakehouse, warehouse, mesh, hybrid)?
- What's driving the change (cost, scale, agility, a specific pain point)?
- Who are the consumers of the data (BI, ML, other services, external partners)?

If any of this is missing and it materially affects the review, ask — but don't block on details that don't change your findings. A reasonable assumption stated inline beats a stalled review.

## Step 2: Run the review checklist

Read `references/checklist.md` for the full set of review dimensions (layering, governance, PII/security, ingestion patterns, ownership model, MDM, migration strategy, cost). Don't mechanically list every item — apply the ones relevant to what was actually proposed, and skip dimensions that don't apply (e.g., don't ding a batch-only warehouse for lacking CDC if nobody needs streaming).

For each relevant dimension, decide: is this **solid**, a **risk**, or an **open question**? A good review has all three categories — an architecture with zero risks or open questions hasn't been reviewed carefully enough.

Pay special attention to tensions that look fine on a diagram but bite in practice — these are the findings that make a review valuable rather than decorative:
- Data mesh domain ownership vs. a centralized "Customer 360" or golden-record view (who owns conflicts when a domain's local view disagrees with the mesh?)
- PII masking applied at ingestion vs. query time (affects who can ever see raw values, and how re-identification requests get handled)
- CDC/streaming ingestion promising low latency while downstream transformation is still batch-scheduled
- MDM survivorship rules that are well-defined for the "happy path" but unspecified for conflicting-source scenarios
- Migration/cutover plans that don't say how validation or rollback works

## Step 3: Produce the findings report

Use this structure:

```markdown
# Architecture Review: [name/summary of what's being reviewed]

## Summary
[2-3 sentences: what's proposed, overall impression]

## Strengths
- [What's genuinely well-designed, and why]

## Risks
- [Risk]: [why it matters, what could go wrong]

## Open Questions
- [Question a reviewer would actually ask in an ARB]

## Recommendations
- [Concrete, prioritized next steps — not generic advice]
```

Keep findings specific to what was actually proposed — reference the actual components (e.g., "the Kafka-based CDC layer" not "your streaming layer") so it reads like it came from someone who read the design, not a template.

## Step 4: Offer follow-through

After the report, offer to go deeper on any single risk, draft the ARB presentation, or turn this into a written doc/artifact if the user wants something shareable or to attach to a review packet.

## Reference

`references/checklist.md` — full review checklist covering medallion layering, governance/catalog strategy, PII handling, ingestion patterns, data mesh vs. centralized ownership, MDM, and migration/cutover risk. Read this before doing a full structured review.
