# Test resource manifest

## Demonstration policy

- File: `samples/risk-policy.md`
- Authority: the creator of a ParamSeal namespace is authoritative only for that namespace.
- Purpose: define an explicit `debt_ceiling` parameter, hard range and maximum delta.
- Limitation: synthetic demonstration policy; it does not represent or control a third-party production protocol.
- Live binding: before deployment, replace placeholders with the full Git commit, exact repository/path and SHA-256 digest of these bytes.

## GitHub observations

ParamSeal uses GitHub-controlled commit identity plus raw bytes at the full commit. This establishes repository object and exact source content. It does not prove production runtime behavior. Runtime claims require StudioNet transactions and protected-registry readback.

## Model fixture

Local LLM mocks exercise contract outcome derivation. They are synthetic and are not reported as validator consensus. Live evidence must use the exact deployed source on StudioNet.

