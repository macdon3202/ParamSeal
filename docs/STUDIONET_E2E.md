# StudioNet E2E evidence

Status: **DEPLOYED — LIVE LIFECYCLE PENDING**

- Contract: [`0x78a7f78078A7f6BaF2D7cD764E9295B85a9fd6eB`](https://explorer-studio.genlayer.com/address/0x78a7f78078A7f6BaF2D7cD764E9295B85a9fd6eB)
- Candidate source SHA-256: `d148bde64e91938f01f6f1e2f114cbc0800881c6efcd059f1d78af6117610c6c`

No lifecycle transaction hash will be added until the corresponding transaction has finalized and its authoritative state has been read back.

## Verified source-failure and rollback path

Roles used:

- Auxiliary A — namespace publisher and permissionless evaluator: `0xFeD97e2aE1A8C1983b7cA206B3545e6A2c685E43`
- Auxiliary B — proposer and sealer: `0xc67532aeF9D2879cBA9375a02E6217A3524657B8`
- Deployment wallet — no lifecycle transaction.

| Step | Finalized transaction | Expected result |
|---|---|---|
| Create isolated failure namespace | [`0x5afc…6a21`](https://explorer-studio.genlayer.com/tx/0x5afcf8a15fd96e99bb71239a02131fa835b1f5139060195c12708ec9f1316a21) | namespace created by auxiliary A |
| Propose bounded change | [`0xd204…ba0e`](https://explorer-studio.genlayer.com/tx/0xd20414e2362e0248c0acc7b81a05ad71c36423e60b95b362d21453c6ccffba0e) | draft bound to auxiliary B and current value `100` |
| Seal exact payload | [`0x56f4…157c`](https://explorer-studio.genlayer.com/tx/0x56f442e1e71d24b2805617bb3fa39ac0296a0c5a2aaea3e407186d67f6de157c) | state `SEALED` |
| Evaluate using wrong digest | [`0xc7a8…ee43`](https://explorer-studio.genlayer.com/tx/0xc7a8607c9b7faf2b22b00648e4a64c767418d5feffc115826ff1fe2d4b1bee43) | finalized failure; full pre/post snapshot equality |
| Evaluate unavailable source | [`0xe747…044e`](https://explorer-studio.genlayer.com/tx/0xe7472568fb10ee60277262240ab2b62a9d828c598022c4690126aea10a19044e) | `INSUFFICIENT / SEMANTIC_FACT_UNKNOWN` |

Authoritative final readback: registry remains `100`; no permit was activated. The full machine-readable receipt and snapshots are in [`docs/evidence/0x78a7...-failure.json`](./evidence/0x78a7f78078a7f6baf2d7cd764e9295b85a9fd6eb-failure.json).

This proves source failure and wrong-digest rollback only. It does not prove the happy path, which remains pending a public commit-pinned policy resource.

## V1 consensus regression discovered live

The first exact-source evaluation [`0xff63…9fe7`](https://explorer-studio.genlayer.com/tx/0xff630f97f7b36a44f661c6da64b0787c733056d7f943cb32a7ef2e8c990b9fe7) finalized as `MAJORITY_DISAGREE`. Authoritative readback remained `SEALED`, with `attempts=0` and registry `100`; no permit existed and no consumption was attempted.

Validator diagnostics reported that reading storage-backed dataclasses in nondeterministic mode is unsupported. V2 therefore copies only bounded primitive policy/change fields during deterministic execution and passes those snapshots into the nondeterministic closure. A static regression assertion and the GenVM suite enforce this boundary. The historical V1 address is retained only as transparent failure evidence and must not be submitted as the current deployment.

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

