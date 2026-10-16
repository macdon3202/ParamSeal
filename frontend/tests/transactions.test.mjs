import test from 'node:test';import assert from 'node:assert/strict';
import {assertReadback,isAddress,isDigest,normalize,normalizeHash,positiveId,receiptState} from '../src/transactions.js';
const account='0x'+'11'.repeat(20),digest='a'.repeat(64);
test('strict address, digest and ID parsing',()=>{assert(isAddress(account));assert(!isAddress('0x'+'0'.repeat(40)));assert(isDigest(digest));assert.throws(()=>positiveId('0'));assert.equal(positiveId('7'),7)});
test('SDK return shapes normalize safely',()=>{assert.equal(normalize(7n),7);assert.deepEqual(normalize({x:2n}),{x:2});assert.equal(normalizeHash({txId:'0x'+'a'.repeat(64)}),'0x'+'a'.repeat(64));assert.throws(()=>normalizeHash({}))});
test('finality requires consensus and leader success',()=>{const tx={status_name:'FINALIZED',result_name:'MAJORITY_AGREE',consensus_data:{leader_receipt:{mode:'leader',execution_result:'SUCCESS'}}};assert(receiptState(tx).verified);assert(!receiptState({...tx,result_name:'MAJORITY_DISAGREE'}).verified)});
test('write readback is bound to exact payload and actor',()=>{const before={attempts:0},after={payload_digest:digest,state:'APPROVED',attempts:1,proposer:account};assert(assertReadback('evaluate_change',before,after,[1,digest],account));assert.throws(()=>assertReadback('consume_permit',after,{...after,state:'CONSUMED',payload_digest:'b'.repeat(64)},[1,digest],account),/payload/) });

