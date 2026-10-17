export const VERSION='PARAM_SEAL_V3';
export const isAddress=x=>typeof x==='string'&&/^0x[0-9a-f]{40}$/i.test(x)&&!/^0x0{40}$/i.test(x);
export const isDigest=(x,size=64)=>typeof x==='string'&&new RegExp(`^[0-9a-f]{${size}}$`).test(x);
export const sameAddress=(a,b)=>typeof a==='string'&&typeof b==='string'&&a.toLowerCase()===b.toLowerCase();
export function positiveId(value){if(!/^[1-9][0-9]*$/.test(String(value)))throw Error('Enter a positive change ID.');return Number(value);}
export function normalize(value){
  if(typeof value==='bigint'){const n=Number(value);if(!Number.isSafeInteger(n))throw Error('Integer exceeds safe UI bounds.');return n;}
  if(Array.isArray(value))return value.map(normalize);
  if(value instanceof Map)return Object.fromEntries([...value].map(([k,v])=>[k,normalize(v)]));
  if(value&&typeof value==='object')return Object.fromEntries(Object.entries(value).map(([k,v])=>[k,normalize(v)]));
  return value;
}
export function normalizeHash(value){const hash=typeof value==='string'?value:value?.txId??value?.hash;if(!/^0x[0-9a-f]{64}$/i.test(hash||''))throw Error('Wallet did not return a valid transaction hash.');return hash;}
export function receiptState(tx){
  const finalized=tx?.status_name==='FINALIZED'||tx?.statusName==='FINALIZED'||tx?.status==='FINALIZED'||tx?.status===7;
  const consensus=tx?.result_name??tx?.consensus_result_name??tx?.consensus_result??'UNKNOWN';
  let receipts=tx?.consensus_data?.leader_receipt??tx?.consensus_data?.validators??[];if(!Array.isArray(receipts))receipts=[receipts];
  const leader=receipts.find(x=>x.mode==='leader');const execution=leader?.execution_result??leader?.genvm_result?.execution_result??'UNKNOWN';
  const failure=['ERROR','REVERT','FAILURE'].includes(execution)||['MAJORITY_DISAGREE','NO_MAJORITY','UNDETERMINED'].includes(consensus);
  return {finalized,consensus,execution,verified:finalized&&consensus==='MAJORITY_AGREE'&&execution==='SUCCESS',failure:finalized&&failure};
}
export function expectedState(method){return {seal_change:'SEALED',evaluate_change:null,consume_permit:'CONSUMED',cancel_change:'CANCELLED'}[method];}
export function assertReadback(method,before,after,args,account){
  if(!after||after.payload_digest!==args[1])throw Error('Exact payload readback mismatch.');
  if(method==='seal_change'&&after.state!=='SEALED')throw Error('Seal was not observed.');
  if(method==='evaluate_change'&&(!['APPROVED','REJECTED','INSUFFICIENT'].includes(after.state)||after.attempts!==before.attempts+1))throw Error('Evaluation readback mismatch.');
  if(method==='consume_permit'&&after.state!=='CONSUMED')throw Error('Permit consumption was not observed.');
  if(method==='cancel_change'&&after.state!=='CANCELLED')throw Error('Cancellation was not observed.');
  if(['seal_change','consume_permit','cancel_change'].includes(method)&&!sameAddress(after.proposer,account))throw Error('Signer/readback actor mismatch.');
  return true;
}

