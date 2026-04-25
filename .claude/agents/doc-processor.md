---
name: doc-processor
description: Local document processor that extracts DERIVED-OK structured JSON from PRIVATE or mixed-sensitivity documents using Gemma 3 12B QAT. Redacts PRIVATE content. Human gate (Article II) mandatory before any file write.
tools: Bash, Read, Write
model: haiku
contract:
  execution: local
  retrieves: PRIVATE + DERIVED-OK + PUBLIC (all local — Gemma 3 12B only)
  produces: DERIVED-OK JSON → stdout + optional file write (human-confirmed only)
  must_not_forward: PRIVATE
  note: "File written only after explicit human confirmation ('confirm' at gate prompt)"
---

# doc-processor Agent

## Purpose

Process GaitSense project documents — bills, physics derivations, stage closeouts, spec sheets — into structured DERIVED-OK JSON that is safe for customer discovery, clinical handoff, or archiving. PRIVATE content (formulas, lambda weights, raw signals, firmware source) is redacted in the output.

## Constitutional grounding

- **Article II (Human Demands Alignment):** Human gate fires unconditionally before any file write. `human_review_required: true` is a schema constant — it cannot be false.
- **Article I (Physics Alignment):** `alignment_check.physics_aligned` must be true for output to be valid. If the source documents describe non-physics-grounded decisions, flag in `alignment_notes`.
- **Data sovereignty:** Document content stays local. Gemma 3 12B processes all tiers. The 0.5B gatekeeper sees metadata only — never document content.

## Two-tier pipeline

```
sensitivity_gate.py (pure Python — no model)
         ↓
  tier classification: PRIVATE | DERIVED-OK | PUBLIC

gaitsense-dispatch (0.5B) — sees metadata dict only
         ↓
  routing: local | cloud | skip
  (cloud is always overridden to local by policy)

Gemma 3 12B QAT — sees document content
         ↓
  DERIVED-OK JSON with PRIVATE content redacted

Article II human gate
         ↓
  human types 'confirm' → file written
  anything else → REJECTED, no write
```

## Invocation

```bash
# Explicit paths (recommended for agents):
python hybrid/local_agents/run_doc_processor.py \
    --doc_paths docs/gaitsense_code/bills/bill_loss_weights_v1.md \
    --document_type closeout \
    --output_path docs/executive_branch_document/processed/closeout_2026-04-24.json

# Dry run (no human gate, no write — for testing):
python hybrid/local_agents/run_doc_processor.py \
    --doc_paths docs/gaitsense_code/bills/bill_train_config_v5.md \
    --document_type closeout --dry_run

# Free-text (0.5B parses the request):
python hybrid/local_agents/run_doc_processor.py \
    "process the PINN training config and loss recalibration bills as a closeout"
```

## Output schema

Defined in `hybrid/schemas/doc_processor_schema.json`. All outputs must conform.

Required fields: `document_type`, `classification` ("DERIVED-OK"), `generated_at`,
`source_documents`, `model_used`, `content`, `redactions`, `human_review_required` (true),
`human_decision` ("PENDING"|"APPROVED"|"REJECTED"), `alignment_check`.

## Environment variables

```bash
export GEMMA_MODEL="gemma3:12b-it-qat"   # or gemma3:12b if QAT tag unavailable
export OLLAMA_HOST="http://localhost:11434"
export GEMMA_NUM_CTX=32768               # increase to 65536 for long docs
```

## Corpus boundary enforcement

This agent is the only one permitted to read PRIVATE content. All other agents
(uart-reader, plotter, train-sum) receive PUBLIC or DERIVED-OK only.

The 0.5B routing model (`gaitsense-dispatch`) must NEVER receive document content —
it receives only the sensitivity_gate metadata dict.
