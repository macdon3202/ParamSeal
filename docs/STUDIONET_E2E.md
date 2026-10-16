# StudioNet E2E evidence

Status: **PENDING EXACT-SOURCE DEPLOYMENT**

This file intentionally contains no fabricated contract address or transaction hash. It becomes the single reviewer entry point after deployment.

Required live sections:

1. Exact deployed contract address, Explorer link and source SHA-256.
2. Wallet-role table proving the deployer wallet performed deployment only.
3. Commit-pinned policy resource and independently recomputed digest.
4. Happy path: namespace, proposal, seal, evaluation, permit consumption and registry readback.
5. Failure path: wrong source digest/unavailable source and no positive state.
6. Conflict path: semantic conflict plus deterministic hard-bound rejection.
7. Adversarial path: prompt injection, wrong actor, wrong digest, stale policy and stale registry.
8. Replay/cancellation: double consume and post-cancel evaluation.
9. Complete pre/post equality snapshots for every rejected transaction.
10. Frontend reconciliation evidence distinguished from browser-wallet signing evidence.

