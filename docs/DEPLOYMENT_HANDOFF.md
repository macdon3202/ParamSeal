# Deployment handoff

The V1 deployment exposed a live validator disagreement caused by storage-backed dataclasses being read in nondeterministic mode. V2 snapshots bounded primitive values before nondeterministic execution and requires a new exact-source deployment.

- Contract version: `PARAM_SEAL_V2`
- Runner: `v0.2.16`
- Exact V2 source SHA-256: `29a6ee8e882d084fb9f4ec2149b745d21f7a0f517534f23104743b31300d9347`
- Historical V1 contract: `0x78a7f78078A7f6BaF2D7cD764E9295B85a9fd6eB` (do not submit as current)
- Constructor arguments: none
- Main-wallet behavior after deployment: none

The deployment manifest and production frontend intentionally have no active V2 address until redeployment.

The live lifecycle must use the two auxiliary wallets:

- Auxiliary A: creates the namespace and therefore becomes its policy publisher.
- Auxiliary B: proposes, seals and consumes the exact change permit.
- Auxiliary A or any unrelated wallet: calls `evaluate_change`, proving evaluation is permissionless.

Before creating a live namespace, push `samples/risk-policy.md` to the public project repository. Use its full commit SHA and recompute the SHA-256 of the exact raw bytes at that commit. Never use a branch URL as evidence.

Do not describe the project as live-verified until `docs/STUDIONET_E2E.md` contains finalized Explorer-linked transactions and authoritative pre/post readbacks for happy, failure, conflict, stale, replay and cancellation paths.

