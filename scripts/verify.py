"""Deterministic local release checks; does not claim StudioNet execution."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).parents[1]
CONTRACT = ROOT / "contracts" / "param_seal.py"
POLICY = ROOT / "samples" / "risk-policy.md"

def main():
    source = CONTRACT.read_text(encoding="utf-8")
    assert source.splitlines()[:2] == ["# v0.2.16", '# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }']
    assert source.count("@gl.public.write") == 7
    assert source.count("@gl.public.view") == 4
    assert 'VERSION = "PARAM_SEAL_V2"' in source
    assert "observe(policy, change)" not in source
    assert "wallet_getSnaps" not in (ROOT / "frontend" / "src" / "client.js").read_text(encoding="utf-8")
    documents = [ROOT / "README.md", *sorted((ROOT / "docs").rglob("*.md")), *sorted((ROOT / "samples").rglob("*.md"))]
    for document in documents:
        for line in document.read_text(encoding="utf-8", errors="ignore").splitlines():
            assert not re.search(r"(?i)(private[_ -]?key|api[_ -]?token)\s*=\s*[\"'][^\"']+", line)
    report = {
        "contract_sha256": hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),
        "sample_policy_sha256": hashlib.sha256(POLICY.read_bytes()).hexdigest(),
        "write_methods": 7,
        "view_methods": 4,
        "deployer_authority": "NONE",
        "scope": "LOCAL_SOURCE_AND_STRUCTURE_ONLY"
    }
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()

