# ParamSeal — AI-Assisted Governance Parameter Change Gate

Live application: https://paramseal.pages.dev

ParamSeal binds a Web3 parameter proposal to an immutable policy revision, asks GenLayer validators to independently assess the exact source, and issues a single-use permit only when semantic and deterministic constraints both pass. The permit updates a protected on-contract registry, so the verdict has a real downstream consequence rather than producing a decorative receipt.

## Why GenLayer

The hard bounds, actor checks, revision checks and replay protection are deterministic. The remaining question—whether a natural-language policy actually permits the exact change and whether its stated conditions are satisfied—requires semantic judgment over externally fetched evidence. Missing, ambiguous or conflicting evidence fails closed.

## Authority model

- The deployment wallet receives no admin or operational authority.
- Any wallet can create its own isolated policy namespace.
- The namespace key binds the publisher address and slug.
- Only that namespace publisher may issue a new policy revision.
- Any wallet can propose and evaluate a change.
- Only the proposer can consume its exact approved permit.
- A steward can therefore create and test a completely independent namespace with their own wallet.

This is a demonstration policy registry. A publisher is authoritative only for its own namespace; ParamSeal does not infer authority over an unrelated third-party protocol.

## Lifecycle

```text
create namespace + initial registry value
→ propose exact old/new payload
→ seal payload digest
→ validators re-fetch commit-pinned policy
→ APPROVED | REJECTED | INSUFFICIENT
→ consume exact permit once
→ protected registry value changes
```

Policy revision, stale registry value, wrong payload digest, wrong actor, terminal replay and source failure all reject without changing protected state.

## Local verification

```powershell
pytest -q tests -p no:cacheprovider
python scripts/verify.py
cd frontend
npm test
npm run build
```

Local GenVM tests execute the submitted public contract entrypoints with sender contexts, web/LLM mocks and complete pre/post snapshots. They do not replace StudioNet evidence. Live transaction hashes and authoritative readbacks will be recorded only after the exact source is deployed.

## Repository map

- `contracts/param_seal.py` — Intelligent Contract and protected registry.
- `tests/test_contract.py` — GenVM lifecycle, rollback and adversarial tests.
- `frontend/` — React + `genlayer-js` inspection terminal.
- `samples/risk-policy.md` — bounded demonstration policy fixture.
- `docs/TEST_MATRIX.md` — claim-to-invariant coverage.
- `docs/TEST_RESOURCE_MANIFEST.md` — source authority and fixture limits.
- `docs/STUDIONET_E2E.md` — live evidence entry point, populated only after deployment.

## Current status

V3 is deployed and the StudioNet live suite has passed using two auxiliary wallets. The production frontend is deployed at `https://paramseal.pages.dev` and its served bundle was verified against the V3 contract address and version marker. See `docs/STUDIONET_E2E.md` for the sole current deployment and Explorer-linked transaction evidence. Historical V1 and V2 deployments are retained only for the audit trail.

