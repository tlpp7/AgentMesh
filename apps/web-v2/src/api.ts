export type TraceEvent={agent?:string;status?:string;attempt?:number;duration_ms?:number;error_type?:string};
export type RunResult={accepted:boolean;output:string;attempts:number;violations:string[];trace:TraceEvent[];metrics?:Record<string,unknown>};
export type RunInput={objective:string;attempts:number;contains?:string};
let token="";
export function setToken(value:string){token=value.trim()}
export async function api<T>(path:string,options:RequestInit={}):Promise<T>{
 const headers=new Headers(options.headers);
 if(options.body)headers.set("Content-Type","application/json");
 if(token)headers.set("Authorization","Bearer "+token);
 const response=await fetch(path,{...options,headers,cache:"no-store"});
 const body=await response.json().catch(()=>({error:"invalid_json"}));
 if(!response.ok)throw new Error(String(body.error||body.detail||"HTTP "+response.status));
 return body as T;
}
export const health=()=>api<{status:string;adapter:string}>("/api/health");
export const execute=(payload:RunInput)=>api<RunResult>("/api/v2/run",{method:"POST",body:JSON.stringify(payload)});
