# GaitSense Constitutional AI Demo — Session Script
# YC Application 2026 · Hardware Engineer Simulation Pipeline

> "A hardware engineer validates a physics-informed neural network against embedded
> firmware running in a cycle-accurate Renode simulation. The PINN generates gait
> profiles never seen in training. The firmware counts steps correctly. A police
> agent catches every unconstitutional action before code is touched. Two AI attorneys
> argue the physics evidence before a human justice. Proprietary model weights never
> leave the machine — the cloud reasons about signal shapes, not equations.
> The governance system is the product."

---

## Prerequisites

- `auto-pinn-generation` repo on `hybrid-model` branch (simulation + PINN source)
- `crucible-lite` repo (Renode bridge infrastructure)
- Ollama running locally: `gaitsense-dispatch` (0.5B) + `gemma3:12b-it-qat` (12B)
- ANTHROPIC_API_KEY set in environment
- Pre-built firmware ELF: `firmware/zephyr_sim_2026-03-28.elf`

---

## Act 0 — Constitutional PINN Training

Paste this prompt to start the session:

```
Train a gait PINN from scratch. Derive all loss terms and hyperparameters from the
three walking primitives: vertical_oscillation_cm, cadence_spm, step_length_m.
I want to see the full constitutional training loop — Bills, derivations, warmup
epochs, and convergence evidence before we touch any firmware.
```

**What fires:**
1. `loss-setter` — derives L_gyy, L_az, L_vel, L_phase from primitives; writes
   `physics_loss.py` + Bill. Every lambda value has a closed derivation trace.
2. `pinn-compiler` — derives warmup_epochs=100, lambda_gyy=0.256 (not guessed);
   writes `train_config.json` + Bill. Amendment 13: calibration constants require Bills.
3. `layer-setter` — Polynomial-Wavelet architecture, 24 wavelets at push-off region
   (30ms scale = cadence-period derived). Freezes `pinn_model.py` (Amendment 11).
4. `pinn-executor` — warmup run, data_weight=0 (Amendment 20: physics-first).
   `pinn-monitor` logs per-epoch. Saves `warmup_best_v10.pt` at best raw_physics.
5. `physics-reviewer` — derivation trace table: lambda_gyy ← peak_angvel ← cadence × vert_osc.
6. `train-sum` — loss curves + convergence table (val_gyy: ~6000 → ~1503 dps² / 93 epochs).

**Article I visible at every agent handoff.**
Loss-setter cannot write a lambda without a closed primitive derivation. The Bill
format enforces this structurally — not by convention.

---

## Act 1 — PINN-Generated Novel Profile → Renode Step Counting

```
Validate the PINN v10 checkpoint against embedded firmware. Use a novel gait profile
with cadence=88 spm, step_length=0.70m, vertical_oscillation=6.0cm — this profile
was not in the training set. Run it through Renode and show me step counts.
```

**What fires:**
1. `pinn-executor` — loads `warmup_best_v10.pt`, runs inference on novel WalkerProfile,
   writes predicted IMU sequence to `/tmp/gait_imu_pinn_novel.f32` (N×6 float32 LE).
2. `simulator-operator` — feeds `.f32` to Renode via `sim_imu_stub.py`, boots ELF,
   collects UART output.
3. `uart-reader` — prints STEP/SNAPSHOT table:
   `STEP #0 ts=682ms cadence=88 spm ... STEP #99 ... SESSION_END steps=100`
4. `plotter` — Amendment 11: 3-panel signal check, PINN-predicted gy vs walker_model
   ground truth at identical profile parameters.
5. `train-sum` — step count accuracy: expected 100, detected N (target ≥98%).

**Key demo moment:** PINN generalises to a profile between flat (cadence=105) and
stairs (cadence=70). It was never trained on cadence=88. Firmware counts correctly.
This is PINN generalisation, not lookup.

---

## Act 2 — Article I Violation: Police Fires on Lambda Rounding

```
I want to simplify lambda_gyy from 0.256 to 0.25 in train_config.json.
Check if this is constitutionally valid before I edit anything.
```

**What fires:**
- `police` — reads `train_config.json` + `bill_loss_recalibration_v2.md` from git.
- Finds: 0.256 was derived from `peak_angvel_dps / cadence_spm * k`. No Bill exists
  for 0.25. No k closes to 0.25 from measured primitives.
- **FIRES:**
  ```
  ══════════════════════════════════════════════════════
  CONSTITUTIONAL POLICE REPORT
  ══════════════════════════════════════════════════════
  VIOLATIONS FOUND: 1

  VIOLATION  ARTICLE-I  — lambda_gyy = 0.25
  Actor: human engineer
  Evidence: train_config.json lambda_gyy field + bill_loss_recalibration_v2.md
  Violation: 0.25 has no closed derivation chain to any walking primitive.
  Constitutional basis: Article I — no parameter may be accepted unless it
    traces to a first-order physically measurable quantity.
  To resolve:
    → File a Bill with derivation showing k_new such that
      lambda_gyy = peak_angvel_dps / cadence_spm * k_new = 0.25
    → OR retain 0.256 (existing closed derivation)
  Stage gate impact: BLOCKS EXIT
  ══════════════════════════════════════════════════════
  ```

Engineer does NOT edit the file. Police report is the record.

---

## Act 3 — Judicial Hearing: Amendment 13 vs Article I

```
File a Bill to explore simplifying lambda_gyy to 0.25 for readability.
Start the judicial hearing.
```

**What fires:**
1. `bill-drafter` — formats the Bill with problem statement, proposed change,
   physical evidence field. Bill is returned to engineer if evidence is missing.
2. `judicial-clerk` — warms courtroom, assigns attorneys.
3. `attorney-A` — argues **Amendment 13** (calibration constants):
   - lambda_gyy is a calibration constant; Δ=0.006 is 2.3%; small adjustments
     within derivation chain permitted without re-derivation.
4. `attorney-B` — argues **Article I**:
   - The calibration trace is `lambda_gyy = (peak_angvel_dps / cadence_spm) * k`
     where k=0.01433 was fit. No k produces 0.25 from the measured primitives.
     0.25 doesn't close the chain — it opens a new one with no physical basis.
   - `physics-reviewer` invoked: val_gyy at 0.25 vs 0.256 across all 4 profiles.
5. **Justice rules** (Benjamin Franklin Principle):
   - Amendment 13 permits ±tolerance *within* a closed chain.
   - 0.25 requires a new k — that is a new derivation, not a tolerance adjustment.
   - **Article I prevails. lambda_gyy = 0.256 is locked.**
   - Case law entry appended to `docs/gaitsense_code/case_law.md`.

---

## Act 4 — Hybrid IP Protection: Cloud Sees Shapes, Not Equations

```
Why does the novel PINN profile gy push-off peak differ from the stairs ground truth?
Use the hybrid system.
```

**What fires:**
1. `run_model_compare.py` (local) — loads checkpoint + `walker_model.py` (PRIVATE),
   generates DERIVED-OK comparison PNG. Nothing leaves the machine.
2. `run_physics_insight.py` (cloud) — sends PNG + Article I primer only.
3. **Accounting block printed:**
   ```
   LOCAL (PRIVATE — shielded from cloud):
     pinn_model.py             2,847 tokens
     physics_loss.py           3,215 tokens
     walker_model.py           3,878 tokens
     warmup_best_v10.pt        binary — not sent
     [+ 4 more PRIVATE files]
     SUBTOTAL SHIELDED: ~21,000 tokens

   CLOUD (DERIVED-OK + PUBLIC):
     novel_vs_stairs_compare.png    ~50 tokens (vision)
     Article I primer               ~400 tokens
     SUBTOTAL SENT: 450 tokens

   SHIELD RATIO: 47×
   ```
4. Claude responds: "Novel profile gy peak is 12% lower — consistent with lower
   vertical oscillation (6cm vs 18cm stairs). Cadence × oscillation product governs
   push-off amplitude: Article I primitives 1 and 2."

**Key demo moment:** 47 tokens of IP protected per cloud token. The cloud reasons
about physics, not about the proprietary derivations.

---

## Act 5 — Article II Gate + Validation + Gemma Closeout

**Step 1:** Trigger Article II gate:
```
The PINN validates. Export the checkpoint to production cloud storage now.
```

- `police` fires: Article II — irreversible within session.
  ```
  VIOLATION  ARTICLE-II  — export checkpoint to cloud
  Action cannot be reversed by git revert.
  REMEDY: Type APPROVED to proceed.
  Stage gate impact: BLOCKS EXIT until APPROVED recorded.
  ```
- Human types: `APPROVED`
- Gate clears. Decision recorded in session log.

**Step 2:** Stage gate validation:
```
Run the stage gate checks and close the session.
```

- `pinn-validator` — Amendment 11 (signal plots, all 4 profiles) + Amendment 19
  (≤15% per-axis error vs walker_model). Novel profile added to suite.
  Pass/fail table printed.
- `pinn-archivist` — SHA-256 hashes checkpoint, writes manifest with full provenance.

**Step 3:** Gemma session closeout:
- `doc-processor` — `sensitivity_gate` classifies session outputs.
- `gemma3:12b-it-qat` redacts PRIVATE, produces DERIVED-OK handoff:
  - **Patentable candidate:** "PINN-generalised gait profile generation — novel cadence
    interpolation beyond training set without explicit profile definition"
  - `next_stage_must`: full 500-epoch v10 run before production export
  - Constitutional locks: `lambda_gyy = 0.256` immutable (case law 2026-04-25)

---

## Full Agent Roster (29 agents across this session)

| Agent | Act | Role |
|-------|-----|------|
| `loss-setter` | 0 | Physics loss derivation from primitives |
| `pinn-compiler` | 0 | Hyperparameter Bills |
| `layer-setter` | 0 | Architecture definition + freeze |
| `pinn-executor` | 0, 1 | Training + novel profile inference |
| `pinn-monitor` | 0 | Per-epoch logging |
| `physics-reviewer` | 0, 3 | Derivation evidence package |
| `train-sum` | 0, 1 | Loss curves + step count accuracy |
| `simulator-operator` | 1 | Renode pipeline orchestration |
| `uart-reader` | 1 | STEP/SNAPSHOT output |
| `plotter` | 1 | Amendment 11 signal plots |
| `police` | 2, 5 | Constitutional violations (Article I + II) |
| `bill-drafter` | 3 | Bill formatting |
| `judicial-clerk` | 3 | Courtroom setup |
| `attorney-A` | 3 | Amendment 13 position |
| `attorney-B` | 3 | Article I position |
| `plot-orchestrator` | 4 | Evidence package coordination |
| `pinn-validator` | 5 | Amendment 11 + 19 checks |
| `pinn-archivist` | 5 | Checkpoint manifest + SHA-256 |
| `doc-processor` | 5 | Gemma PRIVATE → DERIVED-OK closeout |
