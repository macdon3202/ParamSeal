# StudioNet E2E evidence

Status: **V3 LIVE SUITE PASS**

- Current contract: [`0x8437c9d9FecbEcC8d0E4cdEDa6Fcbb4f0e5170b8`](https://explorer-studio.genlayer.com/address/0x8437c9d9FecbEcC8d0E4cdEDa6Fcbb4f0e5170b8)
- Version: `PARAM_SEAL_V3`
- Contract source SHA-256: `e6502085a205ceed7eff646f232e34a5f6bd9f89e20432eea028688cd87a577f`
- Source commit: [`97c13dc9355898adf13b03271457f83c0e608b28`](https://github.com/macdon3202/ParamSeal/tree/97c13dc9355898adf13b03271457f83c0e608b28)
- Policy source: [risk-policy.md at the same commit](https://raw.githubusercontent.com/macdon3202/ParamSeal/97c13dc9355898adf13b03271457f83c0e608b28/samples/risk-policy.md)
- Policy SHA-256: `e2090bbd7a8d537d66f95cb1475bd9f094e5aa3b2dec1f6f2351d9da6ff021e0`

Auxiliary A `0xFeD97e2aE1A8C1983b7cA206B3545e6A2c685E43` acted as publisher and evaluator. Auxiliary B `0xc67532aeF9D2879cBA9375a02E6217A3524657B8` acted as proposer, sealer and consumer. The main wallet deployed only.

## V3 happy path and replay

| Step | Finalized transaction | Result |
|---|---|---|
| Create namespace | [`0xebf9…92bc`](https://explorer-studio.genlayer.com/tx/0xebf9e97e854a64b5ad87eda4d6e18d4546402f10ab0efaf6541821b371c692bc) | publisher A |
| Propose exact update | [`0x01e7…39df`](https://explorer-studio.genlayer.com/tx/0x01e7baf590780d3f138aed2f3eee53369de26575197638fb31e4c1166c4e39df) | old `100`, new `115` |
| Seal payload | [`0xbcf4…22f8`](https://explorer-studio.genlayer.com/tx/0xbcf40a9cf63fb341ae287f88883073f0753e87c81c22f13f290e47522d4722f8) | exact payload frozen |
| Semantic evaluation | [`0x2795…2d17`](https://explorer-studio.genlayer.com/tx/0x279548bef88e28a639f125fced7a91b282a768fce11849914bc3f381c7922d17) | majority agree; `APPROVED` |
| Consume permit | [`0xfaee…3ce5`](https://explorer-studio.genlayer.com/tx/0xfaeeee8243dd66a81bad6e2f0d4bcee7fc61e00b2263077e6af49de4aeb43ce5) | `CONSUMED`; registry `100 → 115` |
| Replay consume | [`0x7252…9f36`](https://explorer-studio.genlayer.com/tx/0x7252acf9190a4c975d12cdd2b6983f8fe5117aa7a5bc2823c9886fadbef79f36) | finalized error; state unchanged |

## V3 source failure

- Wrong digest rollback: [`0x6b3f…09a7`](https://explorer-studio.genlayer.com/tx/0x6b3fd70747577853b1b0c8cdeb7ca66d8e2aa466222dadc1a26f8c239dbc09a7) — complete pre/post equality.
- Missing source evaluation: [`0xa73e…2136`](https://explorer-studio.genlayer.com/tx/0xa73e909df5a4078c30b9350e59071fdc08cc75c52dede5950f9563c9a21f2136) — `INSUFFICIENT / SEMANTIC_FACT_UNKNOWN`; registry stays `100`.

## V3 conflict, stale policy and cancellation

- Hard bound rejection evaluation: [`0x0d1d…06c7`](https://explorer-studio.genlayer.com/tx/0x0d1d5017b07ce131b67acaaed495194107fd6cecfca8205d726e02e5d09c06c7); blocked consume: [`0x8921…de81`](https://explorer-studio.genlayer.com/tx/0x8921690b153b3b0e997c077dd77936f1106201a4eeebc79a40314e8b336ade81). Registry stayed unchanged.
- Policy revision: [`0x1d3a…c3b4`](https://explorer-studio.genlayer.com/tx/0x1d3add79d8802d753d10806924c9f94727d7f7bf4a415269ede2fedad1edc3b4); stale evaluation: [`0x3eb5…1400`](https://explorer-studio.genlayer.com/tx/0x3eb552310dc129ed64668f6a1132d2be40628961eac564959e16272bc6e21400) failed with pre/post equality.
- Wrong actor cancel: [`0x13d4…9990`](https://explorer-studio.genlayer.com/tx/0x13d4c06ae1af49803ef2e57c4990d5dc4b867b53f4e6fd06da1d3566663f9990) failed with no mutation. Proposer cancel: [`0xfb5f…8c51`](https://explorer-studio.genlayer.com/tx/0xfb5fa9d063f70bfae9985e8819179d7fc29db513d06fe6188ba37cac6d278c51); post-cancel evaluation: [`0xc575…0a12`](https://explorer-studio.genlayer.com/tx/0xc575f361bf8a9c54d298eabbc098771c179848ee9e9a4a00eed752fb1aeb0a12) failed with no mutation.

## V3 rationale digest binding

Different rationales for otherwise identical proposals were submitted in [`0x77bb…be10`](https://explorer-studio.genlayer.com/tx/0x77bbcbd5cfd5010b57415d7e84d65e31d33c7ed2b14d2778c7fe705bb654be10) and [`0x844b…9926`](https://explorer-studio.genlayer.com/tx/0x844b3638e1b6879aabd68178d0c6caf796c6f10356b38d2d79ab629428839926). Readback confirms distinct payload digests.

Complete receipts and rollback snapshots: [happy](./evidence/0x8437c9d9fecbecc8d0e4cdeda6fcbb4f0e5170b8-happy.json), [failure](./evidence/0x8437c9d9fecbecc8d0e4cdeda6fcbb4f0e5170b8-failure.json), [guards](./evidence/0x8437c9d9fecbecc8d0e4cdeda6fcbb4f0e5170b8-guards.json), [digest binding](./evidence/0x8437c9d9fecbecc8d0e4cdeda6fcbb4f0e5170b8-digest.json).

## Historical audit trail

- V1 `0x78a7f78078A7f6BaF2D7cD764E9295B85a9fd6eB` had live majority disagreement because the nondeterministic callback read storage-backed dataclasses.
- V2 `0x1154Cfa6981eF0736298fd3a2EC447d7CAA7Bc8A` passed lifecycle, then audit found rationale was not payload-bound.
- V3 addresses both findings and is the only current submission deployment.
