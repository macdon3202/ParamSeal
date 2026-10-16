# ParamSeal proof obligations

| Claim | Required invariant | Evidence |
|---|---|---|
| No deployer authority | constructor stores no deployer/admin capability | source audit + non-deployer lifecycle |
| Exact policy source | commit identity and fetched bytes match stored SHA-256 | source-failure GenVM tests + live transaction |
| Bounded parameter update | new value is in range and delta does not exceed policy maximum | table-driven tests + readback |
| Fail closed | unknown, source error or malformed observation never yields `APPROVED` | adversarial cases + registry equality |
| Exact permit | protocol, version, parameter, old/new values and proposer are digest-bound | wrong-digest and cross-payload rollback |
| Revision safety | newer policy invalidates proposals bound to prior version | stale-policy rollback |
| Downstream effect | permit consumption changes protected registry value | finalized transaction + registry readback |
| Single use | consumed permit cannot be replayed | terminal replay + complete state equality |
| Reviewer reproducibility | any wallet can create its own namespace | independent steward walkthrough |

