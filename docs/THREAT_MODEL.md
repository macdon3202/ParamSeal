# Threat model

Protected assets are policy identity, policy revision, payload digest, permit state and the registry value.

The contract defends against:

- deployer privilege and cross-namespace policy mutation;
- source substitution, commit mismatch and changed bytes;
- prompt injection contained in policy/proposal evidence;
- semantic unknowns being promoted to approval;
- values outside deterministic range/delta constraints;
- policy revision and registry baseline races;
- actor substitution, wrong digest and cross-payload use;
- double consumption and terminal-state replay;
- frontend success before finality/readback.

Out of scope: claiming that the namespace publisher controls a real external protocol, real-time deadlines without a documented GenVM clock primitive, and arbitrary downstream contracts that do not enforce ParamSeal permits.

