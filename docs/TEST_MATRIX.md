# Test matrix

| Area | Sequence | Expected result |
|---|---|---|
| Happy path | publisher creates namespace → proposer seals → evaluator evaluates → proposer consumes | `CONSUMED`; registry `100 → 115` |
| Bounds | propose `49`, `201` or delta `21` | `REJECTED`; registry unchanged |
| Source | unavailable bytes, changed bytes or wrong commit identity | `INSUFFICIENT`; no permit |
| Semantic | uncovered parameter, explicit conflict or unknown condition | non-positive state; no permit |
| Digest | evaluate/consume with wrong payload digest | finalized revert; complete state equality |
| Actor | unrelated wallet revises policy, cancels or consumes | finalized revert; complete state equality |
| Revision | revise policy after proposal seal | stale rejection; no evaluation effect |
| Replay | consume a consumed permit again | finalized revert; registry unchanged |
| Cancellation | proposer cancels sealed packet then evaluates | terminal rejection; state unchanged |
| Retry | source unavailable twice then third evaluation | attempts exhausted; no positive effect |
| Frontend | account/chain changes, invalid hash, incomplete finality | success is not shown |
| Reconciliation | finalized write readback bound to exact ID/digest/actor | mismatches throw and remain visible |

For each rejected live sequence, `docs/STUDIONET_E2E.md` must include the transaction hash, leader result and complete relevant pre/post state.

