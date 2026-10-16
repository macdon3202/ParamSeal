# Deployment handoff

Deploy exactly `contracts/param_seal.py` on StudioNet from the main wallet.

- Contract version: `PARAM_SEAL_V1`
- Runner: `v0.2.16`
- Exact local source SHA-256: `d148bde64e91938f01f6f1e2f114cbc0800881c6efcd059f1d78af6117610c6c`
- Constructor arguments: none
- Main-wallet behavior after deployment: none

After deployment, record the address in `deployments/candidate.json` and set `VITE_CONTRACT_ADDRESS` in `frontend/.env.production`.

The live lifecycle must use the two auxiliary wallets:

- Auxiliary A: creates the namespace and therefore becomes its policy publisher.
- Auxiliary B: proposes, seals and consumes the exact change permit.
- Auxiliary A or any unrelated wallet: calls `evaluate_change`, proving evaluation is permissionless.

Before creating a live namespace, push `samples/risk-policy.md` to the public project repository. Use its full commit SHA and recompute the SHA-256 of the exact raw bytes at that commit. Never use a branch URL as evidence.

Do not describe the project as live-verified until `docs/STUDIONET_E2E.md` contains finalized Explorer-linked transactions and authoritative pre/post readbacks for happy, failure, conflict, stale, replay and cancellation paths.

