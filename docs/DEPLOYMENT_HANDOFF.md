# Deployment handoff

V1 exposed a live validator disagreement caused by storage-backed dataclasses being read in nondeterministic mode. V2 fixed that boundary and passed the complete live lifecycle. The subsequent exact-digest audit found that semantic `rationale` was not included in `payload_digest`. V3 binds that field and is the required final candidate.

- Contract version: `PARAM_SEAL_V3`
- Runner: `v0.2.16`
- Exact V3 source SHA-256: `e6502085a205ceed7eff646f232e34a5f6bd9f89e20432eea028688cd87a577f`
- Historical V2 contract: `0x1154Cfa6981eF0736298fd3a2EC447d7CAA7Bc8A` (validated behavior; do not submit as current)
- Historical V1 contract: `0x78a7f78078A7f6BaF2D7cD764E9295B85a9fd6eB` (do not submit as current)
- Constructor arguments: none
- Main-wallet behavior after deployment: none

The deployment manifest and production frontend intentionally have no active V3 address until redeployment.

The live lifecycle must use the two auxiliary wallets:

- Auxiliary A: creates the namespace and therefore becomes its policy publisher.
- Auxiliary B: proposes, seals and consumes the exact change permit.
- Auxiliary A or any unrelated wallet: calls `evaluate_change`, proving evaluation is permissionless.

Before creating a live namespace, push `samples/risk-policy.md` to the public project repository. Use its full commit SHA and recompute the SHA-256 of the exact raw bytes at that commit. Never use a branch URL as evidence.

Do not describe the project as live-verified until `docs/STUDIONET_E2E.md` contains finalized Explorer-linked transactions and authoritative pre/post readbacks for happy, failure, conflict, stale, replay and cancellation paths.

