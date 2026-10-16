# Reviewer walkthrough

1. Open the deployed frontend and verify StudioNet plus the active contract address.
2. Connect any EIP-1193 wallet. The app does not call `wallet_getSnaps`.
3. In **Policy publisher**, create an isolated namespace using an exact commit-pinned policy file and its SHA-256 digest.
4. Copy the returned protocol key from the finalized transaction and inspect policy version 1.
5. In **Proposal lab**, propose a value within the published bounds.
6. Inspect the exact returned change ID, then seal its displayed payload digest.
7. Evaluate the sealed packet. Wait for finality and authoritative readback.
8. If approved, consume the permit. Confirm that the registry value changes and packet becomes `CONSUMED`.
9. Try the same consume again or use a wrong digest. The transaction must fail and the registry must remain identical.

The steward uses their own namespace and therefore needs no deployer permission.

