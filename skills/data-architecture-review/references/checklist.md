# Data Architecture Review Checklist

Use the relevant sections only — not every design touches every dimension.

## 1. Medallion / layering strategy (bronze / silver / gold)

- Is raw data ever mutated in the bronze layer, or is it truly immutable/append-only?
- Does silver actually do conformance (schema, types, dedup) or just copy bronze with light cleanup?
- Are gold tables owned by consuming teams or by a central team? Mismatches here cause the most friction.
- Is there a clear contract (schema + SLA) between layers, or do downstream consumers reach into silver directly?

## 2. Governance and catalog strategy

- Single catalog (e.g., Unity Catalog) or federated across domains? Federation adds flexibility but fragments discoverability.
- Is lineage tracked automatically (via the platform) or manually documented? Manual lineage rots fast.
- Who approves new datasets entering the gold layer — is there an actual gate, or is it self-service with no review?

## 3. PII and security

- Where is masking/tokenization applied: at ingestion (safer, but loses raw data for some legitimate uses) or at query time via views/policies (more flexible, but depends on policy enforcement never being bypassed)?
- Is there a documented process for re-identification requests (support, legal, fraud investigation)?
- Do row/column-level security policies get tested, or just configured and assumed correct?
- For regulated data (HIPAA/GDPR/GxP-type contexts), is retention/deletion actually enforceable at the storage layer, or only at the catalog/access layer?

## 4. Ingestion patterns

- Batch, micro-batch, or true streaming (CDC via Kafka/Debezium, etc.)? Does the choice match actual latency requirements, or is streaming used because it's trendy?
- If CDC is used: how are schema changes on the source handled? Silently broken pipelines from upstream schema drift are one of the most common real-world failures.
- Is there a dead-letter/replay strategy for ingestion failures?

## 5. Data mesh vs. centralized ownership

- If domains own their own data products, how is a cross-domain "golden record" (e.g., Customer 360) reconciled? This is the single most common tension in mesh designs — flag it explicitly if a 360 view exists alongside domain ownership.
- Who resolves conflicts when two domains disagree on the same entity's attributes?
- Is there real domain accountability (on-call, SLAs) or is "ownership" nominal only?

## 6. MDM and survivorship

- Are survivorship rules (which source wins per attribute) defined for the common case AND the conflict case?
- Is there a manual override/stewardship workflow, or is it fully rules-based with no escape hatch?
- How are merges/unmerges (e.g., discovering two customer records are actually different people) handled after the fact?

## 7. Migration and cutover (if this is a migration project)

- Is there a parallel-run/validation period before cutover, or a hard cutover?
- What's the rollback plan if the new platform produces materially different numbers than the legacy system?
- Lakehouse Federation or similar query-federation tools: are they a permanent architecture choice or a temporary migration bridge? (These are easy to accidentally leave in production long-term.)
- How is reconciliation between old and new systems being validated — spot checks, full diffing, or trust?

## 8. Cost and operational sustainability

- Does the design account for compute costs of reprocessing (e.g., re-running Delta Live Tables pipelines on schema changes)?
- Is there a plan for who operates this day-to-day, or does the design assume the build team stays forever?
