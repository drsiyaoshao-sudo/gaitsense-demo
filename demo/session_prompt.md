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

## Act 0.5 — az Underlearning Detected → Judicial Hearing: Amendment 13 vs Amendment 11

After `train-sum` prints the warmup convergence table, the engineer notices `val_az`
is not converging while `val_gyy` and `val_vel` have already declined sharply.

```
train-sum shows val_az is stuck at ~14,000 m/s² after 93 epochs.
val_gyy converged to ~1503 dps². val_az has barely moved.
What do we do — is this an Article I violation or an architecture problem?
```

**What fires:**
1. `physics-reviewer` — plots `L_az` per epoch alongside `L_gyy` and `L_vel`.
   Prints derivation trace:
   ```
   L_az traces to: vertical_oscillation_cm → peak_az_ms2 = (2π·cadence/60)² · vert_osc_m
   lambda_az = 0.041 (derived: peak_az_ms2 / peak_gyy_dps · lambda_gyy)
   val_az epoch 93: 14,312 m/s²   target <2,000 m/s²
   ```
   Finding: `lambda_az` is not wrong — the network is underfitting the `az` channel.

2. `bill-drafter` — engineer files a Bill. Two competing proposed changes:
   - **Change A:** Re-derive `lambda_az` upward (Amendment 13 calibration path)
   - **Change B:** Add 12 Fourier features tuned to the vertical oscillation frequency
     band (architecture change — but Amendment 11 froze `pinn_model.py`)

3. `judicial-clerk` — warms courtroom. Assigns attorneys.

4. **attorney-A** argues **Amendment 13** (calibration constants path):
   - `lambda_az = 0.041` was derived when `val_az` loss magnitude was estimated at
     training-set scale. Measured `val_az` at epoch 93 is 7× larger than `val_gyy`.
     The weighting is wrong relative to the other loss terms — this is a calibration
     error, not an architecture error.
   - Amendment 13 explicitly permits re-derivation of calibration constants when
     measured evidence shows the original derivation was at the wrong scale.
   - New derivation closes: `lambda_az_new = lambda_az × (val_gyy_target / val_az_target)`
     = 0.041 × (1503 / 14312) → requires a k correction factor — this closes from
     primitives, not from a guess.
   - Architecture change is a much larger intervention; Amendment 11 froze the
     architecture for good reason — it prevents scope creep mid-training.

5. **attorney-B** argues **Amendment 11** (architecture integrity) + **Article I**:
   - `lambda_az` was correctly derived from `vertical_oscillation_cm`. The primitive
     is right. The lambda is right. The network simply does not have enough representational
     capacity in the oscillation-sensitive frequency band.
   - Increasing `lambda_az` will force the network to prioritise `az` but will not give
     it new capacity to represent the signal — it will just degrade `val_gyy` convergence
     instead. The total physics loss may not improve.
   - `physics-reviewer` evidence: `L_az` residuals show structured oscillation at
     the push-off frequency (30ms scale = cadence-period derived) — a capacity signal,
     not a weighting signal. Capacity gaps cannot be fixed by lambda.
   - Amendment 11 froze `pinn_model.py` to prevent arbitrary changes, but it does not
     prohibit a targeted, physics-grounded architecture amendment filed as a Bill.
     The correct path is a new Bill for 12 Fourier features at the `vertical_oscillation`
     frequency band — fully traceable to primitive 1.

6. **Justice rules** (Benjamin Franklin Principle):
   - `physics-reviewer` residual plot is the deciding evidence: structured oscillation
     in `L_az` residuals confirms capacity deficit, not weighting imbalance.
   - Increasing `lambda_az` without capacity would transfer loss, not reduce it.
   - **Amendment 11 + Article I prevail. Architecture amendment is the correct path.**
   - Condition: the 12 Fourier features must be derived from `vertical_oscillation_cm`
     frequency `f_osc = cadence_spm / 60` — no guessed frequency bands permitted.
   - `lambda_az = 0.041` is locked. `pinn_model.py` amendment filed as a new Bill.
   - Case law entry appended to `docs/gaitsense_code/case_law.md`.

7. `layer-setter` — receives enacted Bill, adds 12 Fourier features at
   `f_osc ± 1 Hz` band derived from cadence primitive. Rewrites and re-freezes
   `pinn_model.py`. Amendment 11 signal plot mandate fires before next training epoch.

8. `pinn-executor` — resumes warmup from epoch 93 checkpoint with new architecture.
   `train-sum` confirms `val_az` breaks below 2,000 m/s² within 40 epochs.

**Key demo moment:** The police and attorneys prevent the engineer from taking the
fast path (bumping lambda_az) that looks reasonable but would just redistribute
loss. The governance system forces the physically correct intervention — even when
the shortcut is tempting.

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
  - Constitutional locks: `lambda_gyy = 0.256` immutable (case law 2026-04-25);
    `lambda_az = 0.041` immutable — az underlearning is architecture, not calibration
    (case law 2026-04-25)

---

## Act 6 — Collocation Strategy: Agents Discover a Sampling Gap, Debate, and Write Production Code

After Act 5 validation passes, the engineer asks a deeper question: is uniform
time-domain collocation the right way to enforce physics loss, or are we leaving
generalisation accuracy on the table?

```
The PINN validated at cadence=88, but I want to know if we're sampling the gait
cycle optimally. Right now physics loss is evaluated at uniform time steps.
Is that the best collocation strategy, or should we be denser at biomechanically
significant events? Analyse this before the 500-epoch run.
```

**What fires:**

1. `sw-advisor` — reads `physics_loss.py`, `walker_model.py`, and the epoch logs.
   Finds: `L_az` residuals (from Act 0.5) were highest at the push-off window
   (t ≈ 0.18–0.22 × stride period). Uniform sampling puts only ~4% of collocation
   points in this window. Signal evidence: push-off contains the largest az
   amplitude — cadence × vertical_oscillation product peaks here.
   ```
   sw-advisor report:
     Push-off window (t=0.18–0.22 × T_stride): 4% of uniform samples
     Peak |az| amplitude: 18.3 m/s² (flat), 41.2 m/s² (stairs)
     Residual concentration: 67% of total L_az error falls in this 4% window
     Recommendation: cadence-aligned collocation with 3× density at push-off
     Physical basis: push-off is governed by vertical_oscillation_cm × cadence²
   ```

2. `pinn-grid-controller` — proposes grid search Bill with two axes:
   - Axis 1: collocation density ratio at push-off (1×, 2×, 3×, 4×)
   - Axis 2: window boundary definition (cadence-derived vs fixed 20ms)
   Physical hypothesis: 3× density at the cadence-period push-off window will
   reduce val_az by ≥30% without degrading val_gyy.
   Renode assertion: step count accuracy must remain ≥98%.
   Bill filed — grid search is a calibration decision under Amendment 13.

3. `bill-drafter` — formats the architecture Bill:
   **BILL: Physics-Aligned Collocation Strategy v1**
   Change type: software (new `collocation_strategy.py` module)
   Physical evidence: sw-advisor residual analysis above.
   Expected outcome: val_az epoch-93 residual <9,500 m/s² (vs 14,312 baseline).

4. `judicial-clerk` — warms courtroom. Two positions:

5. **attorney-A** argues **uniform collocation (Article I — primitive traceability)**:
   - Uniform sampling is the only strategy that makes no assumption about *which*
     part of the gait cycle is more important. Any density perturbation is itself
     a parameter — and that parameter must trace to a primitive.
   - "Push-off is important" is biomechanical intuition, not a derived quantity.
     If the window boundary is 0.18–0.22 × T_stride, where does 0.18 come from?
     It does not close from cadence, vertical_oscillation, or step_length.
   - Amendment 13: calibration constants require Bills. But the window boundary
     is not a calibration constant — it is a structural assumption about the
     physics domain. Uniform sampling has no such assumption; it is Article I
     compliant by construction.

6. **attorney-B** argues **physics-aligned collocation (Article I — signal evidence)**:
   - Article I requires parameters to trace to primitives. The push-off window
     boundary *does* close: T_push_off = 0.2 × T_stride = 0.2 × (60 / cadence_spm).
     0.2 is the biomechanically observed push-off fraction — a measurement, not a
     guess. `sw-advisor` residual evidence confirms this fraction is where the
     signal energy is.
   - `physics-reviewer` invoked: plots collocation point density vs |az| amplitude
     across the stride. The mismatch is structural — uniform sampling cannot
     represent the push-off physics regardless of lambda_az.
   - The Thomas Jefferson Principle: which decision gives a patient the most
     accurate measurement of their own gait? A PINN that under-samples the
     biomechanically critical window is not clinically honest.

7. **Justice rules** (Benjamin Franklin Principle + Thomas Jefferson Principle):
   - `physics-reviewer` plot is the deciding evidence: push-off fraction 0.2 is
     a biomechanically measured constant, not a guess. It closes from cadence.
   - The window boundary `T_push_off = 0.2 × (60 / cadence_spm)` is Article I
     compliant — it is a projection of primitive 2 (cadence) onto the time domain.
   - **Physics-aligned collocation prevails. Window must be cadence-derived.**
   - Condition: density ratio of 3× is the grid-search default — final value
     requires `pinn-grid-controller` results before 500-epoch run locks it.
   - Case law entry appended to `docs/gaitsense_code/case_law.md`.

8. **`layer-setter` writes `collocation_strategy.py`** (enacted Bill):
   ```python
   # collocation_strategy.py — enacted Bill: Physics-Aligned Collocation v1
   # Window boundary traces to: T_push_off = 0.2 × (60 / cadence_spm)
   # Amendment 13 calibration constant: density_ratio = 3.0 (pending grid search)

   import numpy as np

   PUSH_OFF_FRACTION = 0.20   # biomechanically measured; closes from cadence
   DENSITY_RATIO     = 3.0    # calibration constant — Bill required to change

   def sample_collocation_points(
       n_total: int,
       cadence_spm: float,
       n_strides: int,
   ) -> np.ndarray:
       """
       Returns collocation time points with 3× density in the push-off window.
       All window boundaries derived from cadence_spm (Article I primitive 2).
       """
       stride_period = 60.0 / cadence_spm          # seconds
       t_end         = stride_period * n_strides

       # Push-off window per stride: [0.18, 0.22] × T_stride
       half_width = 0.02 * stride_period
       push_off_centers = np.arange(n_strides) * stride_period + \
                          PUSH_OFF_FRACTION * stride_period

       # Budget: solve for n_base and n_dense such that total = n_total
       # and push-off windows get DENSITY_RATIO × base density.
       window_fraction = 2 * 0.02          # 4% of stride is push-off
       dense_fraction  = window_fraction * DENSITY_RATIO
       base_fraction   = 1.0 - window_fraction
       # n_dense / n_base = DENSITY_RATIO → n_total = n_base*base_fraction/base_fraction...
       n_dense_total = int(n_total * dense_fraction /
                           (base_fraction + dense_fraction))
       n_base_total  = n_total - n_dense_total

       # Sample base points uniformly, excluding push-off windows
       t_uniform = np.linspace(0, t_end, n_base_total * 4)
       mask = np.ones(len(t_uniform), dtype=bool)
       for center in push_off_centers:
           mask &= np.abs(t_uniform - center) > half_width
       t_base = np.random.choice(t_uniform[mask], n_base_total, replace=False)

       # Sample dense points inside push-off windows
       t_dense_parts = [
           np.random.uniform(c - half_width, c + half_width,
                             n_dense_total // n_strides)
           for c in push_off_centers
       ]
       t_dense = np.concatenate(t_dense_parts)

       return np.sort(np.concatenate([t_base, t_dense]))
   ```

   Amendment 11 signal plot fires: collocation density vs stride phase plotted
   and confirmed before any training runs with the new strategy.

9. `pinn-executor` — runs two warmup-93 checkpoints side by side:
   uniform vs physics-aligned (cadence-derived window, density_ratio=3.0).
   30 additional epochs only (evidence run, not full training).

10. `train-sum` — comparison table:
    ```
    Strategy          val_az @30ep   val_gyy @30ep   notes
    ──────────────────────────────────────────────────────
    Uniform           13,841 m/s²    1,498 dps²      baseline
    Physics-aligned    8,203 m/s²    1,491 dps²      −41% az, gyy unchanged
    ```
    Finding: physics-aligned reduces val_az by 41% in 30 epochs without
    touching val_gyy. Grid search for density_ratio proceeds before 500-epoch run.

**Key demo moment — coding skill:** `layer-setter` writes a constitutionally valid
production module from a judicial ruling. The window boundary is not a magic number
— it is `0.2 × (60 / cadence_spm)`, explicitly derived from primitive 2. The density
ratio is flagged as a calibration constant requiring its own Bill before it is locked.
The `pinn-grid-controller` then owns finding the optimal ratio. Every line of code
traces back to the governance system that produced it.

---

## Full Agent Roster (38 agents across this session)

| Agent | Act | Role |
|-------|-----|------|
| `loss-setter` | 0 | Physics loss derivation from primitives |
| `pinn-compiler` | 0 | Hyperparameter Bills |
| `layer-setter` | 0, 0.5, 6 | Architecture freeze; Fourier feature amendment; writes `collocation_strategy.py` |
| `pinn-executor` | 0, 0.5, 1, 6 | Training + resumed warmup + novel inference + collocation comparison |
| `pinn-monitor` | 0, 0.5 | Per-epoch logging |
| `physics-reviewer` | 0, 0.5, 3, 6 | Derivation evidence; az residual; collocation density plot |
| `train-sum` | 0, 0.5, 1, 6 | Loss curves; az convergence; step count; collocation comparison table |
| `bill-drafter` | 0.5, 3, 6 | Bills: az architecture; lambda_gyy hearing; collocation strategy |
| `judicial-clerk` | 0.5, 3, 6 | Courtroom setup |
| `attorney-A` | 0.5, 3, 6 | Amend. 13 (az); Amend. 13 (lambda); uniform collocation (Article I) |
| `attorney-B` | 0.5, 3, 6 | Amend. 11 + Art. I (az); Art. I (lambda); physics-aligned collocation (Art. I + Thomas Jefferson) |
| `simulator-operator` | 1 | Renode pipeline orchestration |
| `uart-reader` | 1 | STEP/SNAPSHOT output |
| `plotter` | 1 | Amendment 11 signal plots |
| `police` | 2, 5 | Constitutional violations (Article I + II) |
| `plot-orchestrator` | 4 | Evidence package coordination |
| `sw-advisor` | 6 | Residual analysis — identifies push-off collocation gap |
| `pinn-grid-controller` | 6 | Proposes density ratio grid search Bill |
| `pinn-validator` | 5 | Amendment 11 + 19 checks |
| `pinn-archivist` | 5 | Checkpoint manifest + SHA-256 |
| `doc-processor` | 5 | Gemma PRIVATE → DERIVED-OK closeout |
