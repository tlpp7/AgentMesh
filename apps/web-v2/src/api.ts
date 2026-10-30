export type TraceEvent={agent?:string;status?:string;attempt?:number;duration_ms?:number;error_type?:string};
export type RunResult={run_id?:string;accepted:boolean;output:string;attempts:number;violations:string[];trace:TraceEvent[];metrics?:Record<string,unknown>};
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

export type StoredRun={id:string;created:string;status:string;accepted:boolean};
export type StoredEvent={sequence:number;agent:string;status:string;timestamp:string;payload:TraceEvent};
export const listRuns=()=>api<{runs:StoredRun[]}>("/api/v2/runs?limit=30");
export const getRun=(id:string)=>api<RunResult>("/api/v2/runs/"+encodeURIComponent(id));
export const getEvents=(id:string,after=0)=>api<{run_id:string;events:StoredEvent[]}>("/api/v2/runs/"+encodeURIComponent(id)+"/events?after="+after);
