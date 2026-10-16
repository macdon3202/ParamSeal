import {createClient} from 'genlayer-js';
import {studionet} from 'genlayer-js/chains';
import {isAddress,normalize,normalizeHash,receiptState,sameAddress} from './transactions.js';
export const EXPLORER='https://explorer-studio.genlayer.com';
export const reader=()=>createClient({chain:studionet});
export function providers(){return [...new Set([...(window.ethereum?.providers||[]),window.ethereum].filter(p=>typeof p?.request==='function'))];}
export async function connect(provider){
  if(!provider)throw Error('Choose an installed EIP-1193 wallet.');
  const accounts=await provider.request({method:'eth_requestAccounts'});if(!isAddress(accounts?.[0]))throw Error('Wallet did not return an account.');
  const chainId=`0x${studionet.id.toString(16)}`;
  if(BigInt(await provider.request({method:'eth_chainId'}))!==BigInt(studionet.id)){
    try{await provider.request({method:'wallet_switchEthereumChain',params:[{chainId}]});}
    catch(error){if(Number(error.code??error.data?.originalError?.code)!==4902)throw error;await provider.request({method:'wallet_addEthereumChain',params:[{chainId,chainName:studionet.name,nativeCurrency:studionet.nativeCurrency,rpcUrls:studionet.rpcUrls.default.http,blockExplorerUrls:[EXPLORER]}]});await provider.request({method:'wallet_switchEthereumChain',params:[{chainId}]});}
  }
  const current=await provider.request({method:'eth_accounts'});if(!sameAddress(current?.[0],accounts[0]))throw Error('Wallet changed during connection. Reconnect.');
  return {account:accounts[0],provider,client:createClient({chain:studionet,account:accounts[0],provider})};
}
export async function read(address,method,args=[]){if(!isAddress(address))throw Error('Enter a deployed ParamSeal address.');return normalize(await reader().readContract({address,functionName:method,args}));}
export async function send(wallet,address,method,args){
  const accounts=await wallet.provider.request({method:'eth_accounts'});if(!sameAddress(accounts?.[0],wallet.account))throw Error('Account changed. Reconnect before signing.');
  if(BigInt(await wallet.provider.request({method:'eth_chainId'}))!==BigInt(studionet.id))throw Error('Switch to StudioNet before signing.');
  return normalizeHash(await wallet.client.writeContract({address,functionName:method,args,value:0n}));
}
export async function finalize(hash,onStatus=()=>{}){
  for(let i=0;i<160;i++){
    let tx;try{tx=await reader().getTransaction({hash});}catch{onStatus('RPC interrupted · checking the same hash');await new Promise(r=>setTimeout(r,3000));continue;}
    const state=receiptState(tx);onStatus(state.finalized?'Finalized · authoritative readback':'Validator consensus pending');
    if(state.failure)throw Object.assign(Error(`Finalized without successful execution: ${state.consensus} / ${state.execution}`),{finalizedFailure:true});
    if(state.verified)return tx;await new Promise(r=>setTimeout(r,3000));
  }
  throw Error('Still pending. Reconcile this hash; do not resubmit.');
}

