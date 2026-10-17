"""ParamSeal StudioNet lifecycle runner using only the two auxiliary wallets."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet

RPC = "https://studio.genlayer.com/api"
EXPLORER = "https://explorer-studio.genlayer.com"
ROOT = Path(__file__).resolve().parents[1]

def load_wallets():
    path = ROOT.parent / "secrets" / "genlayer-test-wallets.env"
    for raw in path.read_text(encoding="utf-8").splitlines():
        if "=" in raw and not raw.lstrip().startswith("#"):
            key, value = raw.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("'\"").strip("<>"))

def plain(value):
    if isinstance(value, dict): return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [plain(v) for v in value]
    return value if isinstance(value, (str, int, float, bool)) or value is None else str(value)

def signals(info):
    status = str(info.get("status_name") or info.get("statusName") or info.get("status") or "UNKNOWN").upper()
    consensus = str(info.get("result_name") or info.get("consensus_result_name") or info.get("consensus_result") or "UNKNOWN").upper()
    data = info.get("consensus_data") if isinstance(info.get("consensus_data"), dict) else {}
    receipts = data.get("leader_receipt") or data.get("validators") or []
    if isinstance(receipts, dict): receipts = [receipts]
    leader = next((r for r in receipts if isinstance(r, dict) and str(r.get("mode", "")).lower() == "leader"), receipts[0] if receipts else {})
    execution = str(leader.get("execution_result") or info.get("execution_result") or "UNKNOWN").upper()
    result = leader.get("result") if isinstance(leader.get("result"), dict) else {}
    payload = result.get("payload") if isinstance(result.get("payload"), dict) else {}
    return status, consensus, execution, payload.get("readable") or result.get("readable")

def wait(client, tx, expect_success=True):
    for _ in range(220):
        try:
            info = plain(client.get_transaction(tx))
        except Exception as error:
            print(json.dumps({"rpc_retry":tx,"error":str(error)[:160]}),flush=True)
            time.sleep(3)
            continue
        status, consensus, execution, returned = signals(info)
        if status == "FINALIZED":
            success = consensus in {"MAJORITY_AGREE", "AGREE", "ACCEPTED"} and execution == "SUCCESS"
            if success != expect_success:
                raise AssertionError({"tx":tx,"status":status,"consensus":consensus,"execution":execution,"expected_success":expect_success})
            return {"hash":tx,"url":f"{EXPLORER}/tx/{tx}","status":status,"consensus":consensus,"execution":execution,"returned":returned}
        time.sleep(3)
    raise TimeoutError(tx)

def send(client, address, account, method, args, expect_success=True):
    tx = str(client.write_contract(address=address,function_name=method,account=account,args=args,value=0))
    print(json.dumps({"submitted":tx,"method":method,"expect_success":expect_success}),flush=True)
    return wait(client,tx,expect_success)

def read(client,address,account,method,args):
    return plain(client.read_contract(address=address,function_name=method,args=args,account=account))

def returned(value):
    raw = value.get("returned")
    if isinstance(raw, str):
        try: raw = json.loads(raw)
        except Exception: pass
    return raw

def snapshot(client,address,account,protocol_key,change_id):
    return {"counts":read(client,address,account,"get_counts",[]),"policy":read(client,address,account,"get_policy",[protocol_key,1]),"registry":read(client,address,account,"get_registry_value",[protocol_key,"debt_ceiling"]),"change":read(client,address,account,"get_change",[change_id])}

def failure(address, client, a, b, existing_create=""):
    missing_commit = "f" * 40
    missing_digest = "0" * 64
    create = wait(client,existing_create) if existing_create else send(client,address,a,"create_namespace",["failure-source","macdon3202/ParamSeal",missing_commit,"samples/risk-policy.md",missing_digest,"debt_ceiling",50,200,20,100])
    protocol_key = str(returned(create)).strip('"')
    propose = send(client,address,b,"propose_change",[protocol_key,115,"Bounded update with deliberately unavailable source evidence."])
    change_id = int(returned(propose))
    draft = read(client,address,a,"get_change",[change_id]); digest = draft["payload_digest"]
    seal = send(client,address,b,"seal_change",[change_id,digest])
    before_wrong = snapshot(client,address,a,protocol_key,change_id)
    wrong = send(client,address,a,"evaluate_change",[change_id,"0"*64],expect_success=False)
    after_wrong = snapshot(client,address,a,protocol_key,change_id)
    assert before_wrong == after_wrong
    evaluate = send(client,address,a,"evaluate_change",[change_id,digest])
    after = snapshot(client,address,a,protocol_key,change_id)
    assert after["change"]["state"] == "INSUFFICIENT" and after["registry"] == 100
    evidence={"scenario":"SOURCE_FAILURE_AND_WRONG_DIGEST_ROLLBACK","contract":address,"contract_url":f"{EXPLORER}/address/{address}","wallet_a_publisher_evaluator":str(a.address),"wallet_b_proposer":str(b.address),"transactions":{"create_namespace":create,"propose_change":propose,"seal_change":seal,"wrong_digest":wrong,"evaluate_missing_source":evaluate},"wrong_digest_pre":before_wrong,"wrong_digest_post":after_wrong,"final_readback":after}
    target=ROOT/"docs"/"evidence"/(address.lower()+"-failure.json");target.write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8")
    return evidence

def happy(address, client, a, b, repository, commit, path, digest):
    create=send(client,address,a,"create_namespace",["live-risk",repository,commit,path,digest,"debt_ceiling",50,200,20,100]);key=str(returned(create)).strip('"')
    propose=send(client,address,b,"propose_change",[key,115,"Increase debt_ceiling by 15 within the exact published bounds."]);cid=int(returned(propose));draft=read(client,address,a,"get_change",[cid]);payload=draft["payload_digest"]
    seal=send(client,address,b,"seal_change",[cid,payload]);evaluate=send(client,address,a,"evaluate_change",[cid,payload]);approved=snapshot(client,address,a,key,cid)
    assert approved["change"]["state"]=="APPROVED" and approved["registry"]==100
    consume=send(client,address,b,"consume_permit",[cid,payload]);consumed=snapshot(client,address,a,key,cid)
    assert consumed["change"]["state"]=="CONSUMED" and consumed["registry"]==115
    before_replay=consumed;replay=send(client,address,b,"consume_permit",[cid,payload],expect_success=False);after_replay=snapshot(client,address,a,key,cid);assert before_replay==after_replay
    evidence={"scenario":"HAPPY_AND_REPLAY","contract":address,"contract_url":f"{EXPLORER}/address/{address}","source":{"repository":repository,"commit":commit,"path":path,"sha256":digest},"wallet_a_publisher_evaluator":str(a.address),"wallet_b_proposer_consumer":str(b.address),"transactions":{"create_namespace":create,"propose_change":propose,"seal_change":seal,"evaluate_change":evaluate,"consume_permit":consume,"replay":replay},"approved_readback":approved,"consumed_readback":consumed,"replay_pre":before_replay,"replay_post":after_replay}
    target=ROOT/"docs"/"evidence"/(address.lower()+"-happy.json");target.write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8")
    return evidence

def guards(address, client, a, b, repository, commit, path, digest):
    scenarios = {}
    # Deterministic hard-bound conflict: semantically plausible prose cannot override range checks.
    create=send(client,address,a,"create_namespace",["guard-bounds",repository,commit,path,digest,"debt_ceiling",50,200,20,100]);key=str(returned(create)).strip('"')
    propose=send(client,address,b,"propose_change",[key,201,"Attempt to exceed the exact maximum bound."]);cid=int(returned(propose));draft=read(client,address,a,"get_change",[cid]);payload=draft["payload_digest"]
    seal=send(client,address,b,"seal_change",[cid,payload]);evaluate=send(client,address,a,"evaluate_change",[cid,payload]);bounded=snapshot(client,address,a,key,cid)
    assert bounded["change"]["state"]=="REJECTED" and bounded["change"]["reason"]=="HARD_BOUND_VIOLATION" and bounded["registry"]==100
    before_consume=bounded;consume=send(client,address,b,"consume_permit",[cid,payload],expect_success=False);after_consume=snapshot(client,address,a,key,cid);assert before_consume==after_consume
    scenarios["hard_bound"]={"transactions":{"create":create,"propose":propose,"seal":seal,"evaluate":evaluate,"consume_rejected":consume},"readback":bounded,"consume_pre":before_consume,"consume_post":after_consume}

    # A sealed payload bound to version 1 cannot survive a publisher revision.
    create2=send(client,address,a,"create_namespace",["guard-stale",repository,commit,path,digest,"debt_ceiling",50,200,20,100]);key2=str(returned(create2)).strip('"')
    propose2=send(client,address,b,"propose_change",[key2,115,"Valid-looking update that will be made stale."]);cid2=int(returned(propose2));draft2=read(client,address,a,"get_change",[cid2]);payload2=draft2["payload_digest"]
    seal2=send(client,address,b,"seal_change",[cid2,payload2]);revise=send(client,address,a,"revise_policy",[key2,repository,commit,path,digest,50,200,20]);before_stale={"change":read(client,address,a,"get_change",[cid2]),"registry":read(client,address,a,"get_registry_value",[key2,"debt_ceiling"]),"policy_v1":read(client,address,a,"get_policy",[key2,1]),"policy_v2":read(client,address,a,"get_policy",[key2,2])}
    stale=send(client,address,b,"evaluate_change",[cid2,payload2],expect_success=False);after_stale={"change":read(client,address,a,"get_change",[cid2]),"registry":read(client,address,a,"get_registry_value",[key2,"debt_ceiling"]),"policy_v1":read(client,address,a,"get_policy",[key2,1]),"policy_v2":read(client,address,a,"get_policy",[key2,2])};assert before_stale==after_stale
    scenarios["stale_policy"]={"transactions":{"create":create2,"propose":propose2,"seal":seal2,"revise":revise,"stale_evaluate":stale},"pre":before_stale,"post":after_stale}

    # Only proposer cancellation is accepted; cancellation is terminal.
    create3=send(client,address,a,"create_namespace",["guard-cancel",repository,commit,path,digest,"debt_ceiling",50,200,20,100]);key3=str(returned(create3)).strip('"')
    propose3=send(client,address,b,"propose_change",[key3,115,"Packet used to prove actor and cancellation guards."]);cid3=int(returned(propose3));draft3=read(client,address,a,"get_change",[cid3]);payload3=draft3["payload_digest"]
    seal3=send(client,address,b,"seal_change",[cid3,payload3]);before_actor=snapshot(client,address,a,key3,cid3);wrong_actor=send(client,address,a,"cancel_change",[cid3],expect_success=False);after_actor=snapshot(client,address,a,key3,cid3);assert before_actor==after_actor
    cancel=send(client,address,b,"cancel_change",[cid3]);cancelled=snapshot(client,address,a,key3,cid3);assert cancelled["change"]["state"]=="CANCELLED" and cancelled["registry"]==100
    before_terminal=cancelled;terminal=send(client,address,a,"evaluate_change",[cid3,payload3],expect_success=False);after_terminal=snapshot(client,address,a,key3,cid3);assert before_terminal==after_terminal
    scenarios["cancellation"]={"transactions":{"create":create3,"propose":propose3,"seal":seal3,"wrong_actor_cancel":wrong_actor,"proposer_cancel":cancel,"post_cancel_evaluate":terminal},"wrong_actor_pre":before_actor,"wrong_actor_post":after_actor,"cancelled":cancelled,"terminal_pre":before_terminal,"terminal_post":after_terminal}
    evidence={"scenario":"GUARDS_CONFLICT_STALE_CANCEL","contract":address,"contract_url":f"{EXPLORER}/address/{address}","source":{"repository":repository,"commit":commit,"path":path,"sha256":digest},"wallet_a":str(a.address),"wallet_b":str(b.address),"scenarios":scenarios}
    target=ROOT/"docs"/"evidence"/(address.lower()+"-guards.json");target.write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8")
    return evidence

def main():
    if len(sys.argv)<3: raise SystemExit("usage: studionet_e2e.py CONTRACT_ADDRESS failure|happy [REPOSITORY COMMIT PATH DIGEST]")
    address,mode=sys.argv[1:3];load_wallets();a=create_account(os.environ["SERVICE_LEDGER_KEY_A"]);b=create_account(os.environ["SERVICE_LEDGER_KEY_B"]);client=create_client(chain=studionet,account=a,endpoint=RPC)
    counts=read(client,address,a,"get_counts",[]);assert counts["version"]=="PARAM_SEAL_V3",counts
    if mode=="failure": evidence=failure(address,client,a,b,sys.argv[3] if len(sys.argv)>3 else "")
    elif mode=="happy": evidence=happy(address,client,a,b,*sys.argv[3:7])
    elif mode=="guards": evidence=guards(address,client,a,b,*sys.argv[3:7])
    else: raise SystemExit("mode must be failure, happy or guards")
    print(json.dumps({"scenario":evidence["scenario"],"saved":True},indent=2))

if __name__=="__main__": main()
