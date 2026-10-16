import hashlib
import json
from pathlib import Path
import pytest

CONTRACT = Path(__file__).parents[1] / "contracts" / "param_seal.py"
A = bytes.fromhex("11" * 20)
B = bytes.fromhex("22" * 20)
C = bytes.fromhex("33" * 20)
DEPLOYER = bytes.fromhex("99" * 20)
COMMIT = "a" * 40
SOURCE = "# Risk policy\nParameter debt_ceiling may increase when change is at most 20 and resulting value remains between 50 and 200.\n"
DIGEST = hashlib.sha256(SOURCE.encode()).hexdigest()

def deploy(vm, direct_deploy):
    vm.strict_mocks = True
    vm.check_pickling = True
    with vm.prank(DEPLOYER):
        return direct_deploy(CONTRACT, sdk_version="v0.2.16")

def create(c, vm, actor=A, **changes):
    args = dict(slug="demo-risk", repository="example/policies", commit=COMMIT, path="risk.md", source_digest=DIGEST, parameter="debt_ceiling", minimum=50, maximum=200, max_delta=20, initial_value=100)
    args.update(changes)
    with vm.prank(actor):
        return c.create_namespace(**args)

def propose(c, vm, key, actor=B, value=115, rationale="Increase is within the published bounded policy."):
    with vm.prank(actor):
        cid = c.propose_change(key, value, rationale)
        digest = c.get_change(cid)["payload_digest"]
        c.seal_change(cid, digest)
    return cid, digest

def mocks(vm, facts=None, status=200, source=SOURCE, commit=None):
    vm.mock_web(r"^https://api\.github\.com/repos/example/policies/commits/" + COMMIT + "$", {"method":"GET", "status":200, "body":json.dumps(commit or {"sha":COMMIT})})
    vm.mock_web(r"^https://raw\.githubusercontent\.com/example/policies/" + COMMIT + r"/risk\.md$", {"method":"GET", "status":status, "body":source})
    vm.mock_llm("PARAM_SEAL_V1", facts or {"policy_addresses_parameter":"YES", "change_permitted":"YES", "conditions_satisfied":"YES", "verdict":"COMPLIANT"})

def snapshot(c, key=None):
    out = {"counts": c.get_counts()}
    if key:
        out["policy"] = c.get_policy(key, 1)
        out["registry"] = c.get_registry_value(key, "debt_ceiling")
        out["changes"] = [c.get_change(i) for i in range(1, out["counts"]["changes"] + 1)]
    return out

def happy(c, vm):
    key = create(c, vm)
    cid, digest = propose(c, vm, key)
    mocks(vm)
    with vm.prank(C):
        assert c.evaluate_change(cid, digest) == "APPROVED"
    with vm.prank(B):
        assert c.consume_permit(cid, digest) == "CONSUMED"
    return key, cid, digest

def test_happy_path_changes_protected_registry(direct_vm, direct_deploy):
    c = deploy(direct_vm, direct_deploy)
    key, cid, _ = happy(c, direct_vm)
    assert c.get_registry_value(key, "debt_ceiling") == 115
    assert c.get_change(cid)["state"] == "CONSUMED"

def test_deployer_has_no_operational_authority(direct_vm, direct_deploy):
    c = deploy(direct_vm, direct_deploy)
    key = create(c, direct_vm)
    assert c.get_policy(key, 1)["publisher"].lower() == "0x" + A.hex()
    cid, digest = propose(c, direct_vm, key)
    before = snapshot(c, key)
    with direct_vm.prank(DEPLOYER), direct_vm.expect_revert("PROPOSER_ONLY"):
        c.cancel_change(cid)
    assert snapshot(c, key) == before

def test_any_wallet_can_create_own_namespace(direct_vm, direct_deploy):
    c = deploy(direct_vm, direct_deploy)
    ka = create(c, direct_vm, A)
    kb = create(c, direct_vm, C, slug="judge-demo")
    assert ka != kb and c.get_counts()["policies"] == 2

@pytest.mark.parametrize("value,reason", [(49,"HARD_BOUND_VIOLATION"),(201,"HARD_BOUND_VIOLATION"),(121,"MAX_DELTA_VIOLATION")])
def test_deterministic_bounds_override_model(direct_vm, direct_deploy, value, reason):
    c = deploy(direct_vm, direct_deploy); key = create(c, direct_vm); cid,digest = propose(c,direct_vm,key,value=value); mocks(direct_vm)
    assert c.evaluate_change(cid,digest) == "REJECTED"
    assert c.get_change(cid)["reason"] == reason and c.get_registry_value(key,"debt_ceiling") == 100

@pytest.mark.parametrize("facts", [
    {"policy_addresses_parameter":"NO","change_permitted":"YES","conditions_satisfied":"YES","verdict":"COMPLIANT"},
    {"policy_addresses_parameter":"YES","change_permitted":"NO","conditions_satisfied":"YES","verdict":"CONFLICTING"},
    {"policy_addresses_parameter":"YES","change_permitted":"YES","conditions_satisfied":"UNKNOWN","verdict":"INSUFFICIENT"},
])
def test_semantic_non_positive_never_issues_permit(direct_vm,direct_deploy,facts):
    c=deploy(direct_vm,direct_deploy); key=create(c,direct_vm); cid,digest=propose(c,direct_vm,key); mocks(direct_vm,facts)
    assert c.evaluate_change(cid,digest) in {"REJECTED","INSUFFICIENT"}
    before=snapshot(c,key)
    with direct_vm.prank(B),direct_vm.expect_revert("PERMIT_NOT_ACTIVE"): c.consume_permit(cid,digest)
    assert snapshot(c,key)==before

@pytest.mark.parametrize("mock_args", [
    {"status":503},
    {"source":SOURCE+"tampered"},
    {"commit":{"sha":"b"*40}},
])
def test_source_failures_are_insufficient(direct_vm,direct_deploy,mock_args):
    c=deploy(direct_vm,direct_deploy); key=create(c,direct_vm); cid,digest=propose(c,direct_vm,key); mocks(direct_vm,**mock_args)
    assert c.evaluate_change(cid,digest)=="INSUFFICIENT"
    assert c.get_registry_value(key,"debt_ceiling")==100

def test_wrong_digest_and_wrong_actor_roll_back(direct_vm,direct_deploy):
    c=deploy(direct_vm,direct_deploy); key=create(c,direct_vm); cid,digest=propose(c,direct_vm,key); before=snapshot(c,key)
    with direct_vm.expect_revert("PAYLOAD_DIGEST_MISMATCH"): c.evaluate_change(cid,"0"*64)
    assert snapshot(c,key)==before
    with direct_vm.prank(C),direct_vm.expect_revert("PROPOSER_ONLY"): c.cancel_change(cid)
    assert snapshot(c,key)==before

def test_single_use_and_stale_registry_guard(direct_vm,direct_deploy):
    c=deploy(direct_vm,direct_deploy); key,cid,digest=happy(c,direct_vm); before=snapshot(c,key)
    with direct_vm.prank(B),direct_vm.expect_revert("PERMIT_NOT_ACTIVE"): c.consume_permit(cid,digest)
    assert snapshot(c,key)==before

def test_policy_revision_invalidates_sealed_change(direct_vm,direct_deploy):
    c=deploy(direct_vm,direct_deploy); key=create(c,direct_vm); cid,digest=propose(c,direct_vm,key)
    with direct_vm.prank(A): c.revise_policy(key,"example/policies",COMMIT,"risk.md",DIGEST,50,220,25)
    before=snapshot(c,key)
    with direct_vm.expect_revert("POLICY_VERSION_STALE"): c.evaluate_change(cid,digest)
    assert snapshot(c,key)==before

def test_only_publisher_can_revise(direct_vm,direct_deploy):
    c=deploy(direct_vm,direct_deploy); key=create(c,direct_vm); before=snapshot(c,key)
    with direct_vm.prank(B),direct_vm.expect_revert("PUBLISHER_ONLY"): c.revise_policy(key,"example/policies",COMMIT,"risk.md",DIGEST,50,220,25)
    assert snapshot(c,key)==before

def test_cancel_is_terminal(direct_vm,direct_deploy):
    c=deploy(direct_vm,direct_deploy); key=create(c,direct_vm); cid,digest=propose(c,direct_vm,key)
    with direct_vm.prank(B): assert c.cancel_change(cid)=="CANCELLED"
    before=snapshot(c,key)
    with direct_vm.expect_revert("CHANGE_NOT_EVALUATABLE"): c.evaluate_change(cid,digest)
    assert snapshot(c,key)==before

def test_bounded_retry(direct_vm,direct_deploy):
    c=deploy(direct_vm,direct_deploy); key=create(c,direct_vm); cid,digest=propose(c,direct_vm,key); mocks(direct_vm,status=503)
    assert c.evaluate_change(cid,digest)=="INSUFFICIENT"
    assert c.evaluate_change(cid,digest)=="INSUFFICIENT"
    before=snapshot(c,key)
    with direct_vm.expect_revert("ATTEMPTS_EXHAUSTED"): c.evaluate_change(cid,digest)
    assert snapshot(c,key)==before

@pytest.mark.parametrize("kwargs,error", [
    ({"slug":"bad slug"},"INVALID_SLUG"),
    ({"repository":"bad"},"INVALID_REPOSITORY"),
    ({"commit":"main"},"INVALID_COMMIT"),
    ({"source_digest":"f"*63},"INVALID_SOURCE_DIGEST"),
    ({"minimum":110},"INITIAL_OUT_OF_BOUNDS"),
    ({"max_delta":0},"INVALID_MAX_DELTA"),
])
def test_invalid_namespace_inputs_no_mutation(direct_vm,direct_deploy,kwargs,error):
    c=deploy(direct_vm,direct_deploy); before=snapshot(c)
    with direct_vm.prank(A),direct_vm.expect_revert(error): create(c,direct_vm,A,**kwargs)
    assert snapshot(c)==before

def test_exact_runner_and_no_admin_surface():
    source=CONTRACT.read_text()
    assert source.splitlines()[:2]==["# v0.2.16", '# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }']
    assert "self.admin" not in source.lower() and "self.owner" not in source.lower()
