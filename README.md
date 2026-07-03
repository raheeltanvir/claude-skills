# Claude Skills: Data Architecture Review & Token Cost Estimator

Two [Claude Skills](https://docs.claude.com) built for data/AI architects and engineers — one for reviewing data platform designs, one for estimating and optimizing Claude API costs.

A Skill packages instructions, checklists, and (where useful) executable scripts into something Claude loads on demand for a specific kind of task. Unlike a one-off prompt, a Skill runs the same review logic or the same calculation every time it's invoked — consistent output, not reinvented per conversation.

## Repo contents

```
.
├── README.md
├── data-architecture-review.skill        # packaged skill, ready to install
├── token-cost-estimator.skill            # packaged skill, ready to install
├── skills/
│   ├── data-architecture-review/
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── checklist.md
│   └── token-cost-estimator/
│       ├── SKILL.md
│       └── scripts/
│           └── estimate_cost.py
├── samples/
│   ├── sample-architecture-design.md     # test input for the review skill
└── └── sample-workload-description.md    # test input for the cost estimator
```

---

## Skill 1: Data Architecture Review

Reviews a proposed or existing data platform architecture (lakehouse, warehouse, migration plan, data mesh) with the rigor of a staff-level architect doing a design review, and produces a structured findings report: strengths, risks, open questions, recommendations.

**Checklist coverage:**
- Medallion layering (bronze/silver/gold)
- Governance and catalog strategy
- PII handling and masking approach
- Ingestion patterns (batch vs. CDC/streaming)
- Data mesh domain ownership vs. centralized views (e.g. Customer 360)
- MDM and survivorship rules
- Migration/cutover risk
- Cost and operational sustainability

**When it triggers:** sharing an architecture diagram, design doc, or migration plan and asking for feedback, a second opinion, or ARB prep.

---

## Skill 2: Token Cost Estimator

Estimates Claude API costs for a described workload and compares optimization strategies — prompt caching, the Batch API, model tiering, and RAG vs. long-context tradeoffs — using an actual calculation script rather than estimating in prose.

**What it checks:**
- Current Anthropic pricing (fetched live, never hardcoded — pricing changes)
- Baseline cost vs. cost with each optimization strategy applied
- Whether caching, batching, or tiering are actually worth it for *this* workload's shape, not generically
- The RAG vs. long-context crossover point for workloads with large repeated reference material

**When it triggers:** describing an LLM workload (volume, prompt shape, latency needs) and asking about cost, or whether a specific optimization is worth implementing.

---

## Installation

**Claude.ai / Claude Desktop / Claude mobile:**
1. Download the `.skill` file (`data-architecture-review.skill` or `token-cost-estimator.skill`).
2. Open it in Claude — a **Save skill** button appears.
3. Click it to install the skill into your profile. (Requires an org/plan that allows custom skills.)

**Claude Code / Cowork:**
1. Unzip the `.skill` file (it's a zip archive) or use the corresponding folder under `skills/`.
2. Copy the folder into your local skills directory (commonly `~/.claude/skills/` or your project's `.claude/skills/`).
3. Claude will pick it up automatically based on the `SKILL.md` description — no manual invocation needed.

---

## Usage

Just describe the task naturally — you don't need to explicitly name the skill. Claude reads the skill descriptions and pulls in the relevant one automatically.

**Data Architecture Review:**
> "Here's our proposed lakehouse migration design — can you review it and tell me what I'm missing before I take this to the architecture review board?"

**Token Cost Estimator:**
> "We're running about 4,000 requests a day through Sonnet, average 6,800 input tokens with a shared 6,000-token system prompt. Is prompt caching worth turning on?"

---

## Testing

The `samples/` folder has two files built specifically to test whether each skill catches real issues rather than rubber-stamping:

**`sample-architecture-design.md`** — a lakehouse migration doc with intentionally planted gaps: a data-mesh-vs-centralized-Customer-360 ownership tension, no MDM fallback rule for unmatched records, no GDPR deletion process, and no rollback plan for cutover. A good review should surface all four.

**`sample-workload-description.md`** — a support-ticket-triage workload with a large shared system prompt (caching candidate), relaxed latency tolerance (batch candidate), and a 70/30 simple/complex ticket split (model-tiering candidate). A good response should evaluate all three levers against this specific workload, not give generic advice.

**To test:**
1. Install the relevant skill (see Installation above).
2. Upload or paste the contents of the matching sample file.
3. Ask Claude to review it / estimate cost for it.
4. Compare the output against the planted issues listed above.

The cost estimator's calculation script can also be run standalone, independent of Claude:

```bash
python3 skills/token-cost-estimator/scripts/estimate_cost.py \
  --requests-per-day 4000 \
  --input-tokens 6800 \
  --output-tokens 350 \
  --input-price-per-mtok 3 \
  --output-price-per-mtok 15 \
  --cached-fraction 0.88
```

---

## Notes

- Pricing figures used by the cost estimator are fetched at run time, not hardcoded in the skill — always verify against [Anthropic's current pricing](https://docs.claude.com) if running the script standalone with your own price inputs.
- Both skills are starting points, not final word — treat findings as a structured first pass, and use judgment (or a human reviewer) for anything high-stakes.

## License

MIT — use, adapt, and share freely. Attribution appreciated but not required.
