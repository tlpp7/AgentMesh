import React,{useEffect,useMemo,useState} from "react";
import {createRoot} from "react-dom/client";
import {ReactFlow,Background,Controls,MarkerType,type Node,type Edge} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import "./dashboard.css";
import {health,execute,setToken,listRuns,getRun,getEvents,getTelemetry,type TelemetrySnapshot,type StoredRun,type RunResult} from "./api";

const names=["analyzer","proposer","critic"];
function App(){
 const [objective,setObjective]=useState("Analyser les contraintes d'un système multi-agents");
 const [contains,setContains]=useState("");
 const [attempts,setAttempts]=useState(3);
 const [accessToken,setAccessToken]=useState("");
 const [connection,setConnection]=useState("Vérification...");
 const [result,setResult]=useState<RunResult|null>(null);
 const [selected,setSelected]=useState("supervisor");
 const [busy,setBusy]=useState(false);
 const [error,setError]=useState("");
 const [search,setSearch]=useState("");
 const [savedRuns,setSavedRuns]=useState<StoredRun[]>([]);
 const [historyError,setHistoryError]=useState("");
 const [replayCount,setReplayCount]=useState<number|null>(null);
 const [telemetry,setTelemetry]=useState<TelemetrySnapshot|null>(null);
 const [telemetryError,setTelemetryError]=useState("");
 useEffect(()=>{health().then(data=>setConnection(data.status==="ok"?"API connectée":"API indisponible")).catch(()=>setConnection("API hors ligne"));},[]);
 const events=result?.trace??[];
 const nodes=useMemo<Node[]>(()=>{
  const statuses=new Map<string,string>();
  for(const event of events){if(event.agent)statuses.set(event.agent,event.status??"unknown")}
  const all=[...names.map((id,i)=>({id,x:65+i*245,y:i%2?200:70})),{id:"supervisor",x:310,y:340}];
  return all.map(p=>({id:p.id,position:{x:p.x,y:p.y},data:{label:p.id.toUpperCase()},style:{
   background:selected===p.id?"#1e4882":statuses.get(p.id)==="error"?"#662e3c":"#162d47",
   border:"1px solid "+(statuses.get(p.id)==="error"?"#e38787":"#5b90c8"),
   color:"#eff6ff",borderRadius:12,padding:12,minWidth:132,fontSize:12
  }}));
 },[events,selected]);
 const edges=useMemo<Edge[]>(()=>[
  {id:"a-p",source:"analyzer",target:"proposer",markerEnd:{type:MarkerType.ArrowClosed}},
  {id:"p-c",source:"proposer",target:"critic",markerEnd:{type:MarkerType.ArrowClosed}},
  {id:"c-s",source:"critic",target:"supervisor",markerEnd:{type:MarkerType.ArrowClosed}}
 ],[]);
 const filtered=events.filter(e=>[e.agent,e.status,e.error_type].join(" ").toLowerCase().includes(search.toLowerCase()));
 async function run(){
  setError("");setBusy(true);
  try{const data=await execute({objective,attempts,...(contains?{contains}:{})});setResult(data);if(data.run_id)await refreshHistory();}
  catch(exc){setError(exc instanceof Error?exc.message:String(exc));}
  finally{setBusy(false);}
 }
 async function refreshHistory(){
  try{const data=await listRuns();setSavedRuns(data.runs);setHistoryError("");}
  catch(e){setHistoryError(e instanceof Error?e.message:String(e));}
 }
 async function refreshTelemetry(){
  try{setTelemetry(await getTelemetry());setTelemetryError("");}
  catch(e){setTelemetryError(e instanceof Error?e.message:String(e));}
 }
 async function inspectRun(id:string){
  try{setHistoryError("");const [data,replay]=await Promise.all([getRun(id),getEvents(id)]);setResult(data);setReplayCount(replay.events.length);}
  catch(e){setHistoryError(e instanceof Error?e.message:String(e));}
 }
 return <div className="layout">
  <aside className="sidebar"><div className="brand">◈ AgentMesh</div><div className="side-caption">CONTROL PLANE · R2 EXPERIMENTAL</div>
   <a href="#history">Historique persistant</a><a href="#network">Réseau d'agents</a><a href="#execution">Exécutions</a><a href="#diagnostics">Diagnostics</a><a href="#telemetry">Observabilité R8</a>
   <p className="muted">Le dashboard historique reste sur le port 8000.</p>
  </aside>
  <main className="main">
   <header className="heading"><div><small className="muted">AGENTMESH / WORKSPACE</small><h1>Orchestration et diagnostic</h1></div><span className="pill">{connection}</span></header>
   <div className="grid">
    <section className="card" id="execution"><h2>Paramètres d'exécution</h2>
     <label className="field">Objectif<textarea value={objective} maxLength={5000} onChange={e=>setObjective(e.target.value)}/></label>
     <label className="field">Contrainte de présence<input value={contains} maxLength={1000} onChange={e=>setContains(e.target.value)} placeholder="Optionnelle"/></label>
     <label className="field">Tentatives (1 à 10)<input type="number" min="1" max="10" value={attempts} onChange={e=>setAttempts(Number(e.target.value))}/></label>
     <label className="field">Token API (uniquement en mémoire)<input type="password" autoComplete="off" value={accessToken} onChange={e=>{setAccessToken(e.target.value);setToken(e.target.value)}} placeholder="Si AGENTMESH_API_TOKEN est défini"/></label>
     <div className="actions"><button className="primary" disabled={busy||!objective.trim()||attempts<1||attempts>10} onClick={run}>{busy?"Exécution...":"Exécuter"}</button><button onClick={()=>{setResult(null);setError("");}}>Effacer</button></div>
     {error&&<p role="alert" className="error">Erreur API : {error}</p>}
    </section>
    <section className="card" id="network"><div className="heading"><h2>Graphe d'agents</h2><span className="muted">Sélection interactive</span></div>
     <div className="flow"><ReactFlow nodes={nodes} edges={edges} nodesDraggable={false} onNodeClick={(_,node)=>setSelected(node.id)} fitView><Background color="#27445f"/><Controls/></ReactFlow></div>
     <p className="muted">Nœud sélectionné : <strong>{selected}</strong> — représentation de la chaîne déterministe, pas un streaming temps réel.</p>
    </section>
    <section className="card span2" id="history"><div className="heading"><h2>Historique SQLite R3</h2><button onClick={refreshHistory}>Actualiser</button></div>
     <p className="muted">Historique disponible uniquement lorsque AGENTMESH_DB_PATH est configuré sur FastAPI.</p>
     {historyError&&<p className="error" role="alert">Historique : {historyError}</p>}
     {replayCount!==null&&<p className="success">Événements relus : {replayCount}</p>}
     <div className="trace-wrap"><table className="trace"><thead><tr><th>Identifiant</th><th>Date UTC</th><th>Accepté</th><th>Action</th></tr></thead><tbody>
      {savedRuns.map(item=><tr key={item.id}><td>{item.id.slice(0,12)}</td><td>{item.created}</td><td>{item.accepted?"Oui":"Non"}</td><td><button onClick={()=>inspectRun(item.id)}>Rejouer</button></td></tr>)}
      {!savedRuns.length&&<tr><td colSpan={4} className="muted">Aucune exécution chargée</td></tr>}
     </tbody></table></div>
    </section>
    <section className="card span2" id="telemetry">
     <div className="heading"><h2>Observabilité R8</h2><button onClick={refreshTelemetry}>Charger les métriques</button></div>
     <p className="muted">Mesures du processus FastAPI actif, sans contenu des objectifs ou des réponses. Elles ne sont pas conservées après redémarrage.</p>
     {telemetryError&&<p role="alert" className="error">Métriques : {telemetryError}</p>}
     {telemetry&&<><div className="stats"><div className="stat"><span className="muted">Exécutions mesurées</span><strong>{telemetry.count}</strong></div>
     <div className="stat"><span className="muted">Acceptées</span><strong>{telemetry.accepted_count}</strong></div>
     <div className="stat"><span className="muted">P95 observé</span><strong>{telemetry.p95_duration_ms===null?"—":telemetry.p95_duration_ms+" ms"}</strong></div></div>
     <div className="trace-wrap"><table className="trace"><thead><tr><th>Trace ID</th><th>Run ID</th><th>Durée</th><th>Événements</th></tr></thead><tbody>
     {telemetry.runs.map(item=><tr key={item.trace_id}><td title={item.trace_id}>{item.trace_id.slice(0,12)}</td><td>{item.run_id?.slice(0,12)??"—"}</td><td>{item.duration_ms} ms</td><td>{item.event_count}</td></tr>)}
     </tbody></table></div></>}
    </section>
    <section className="card span2" id="diagnostics"><div className="heading"><h2>Inspection et diagnostics</h2><span className="pill">{result?(result.accepted?"Accepté":"Rejeté"):"Aucune exécution"}</span></div>
     <div className="stats"><div className="stat"><span className="muted">Tentatives</span><strong>{result?.attempts??"—"}</strong></div><div className="stat"><span className="muted">Événements</span><strong>{events.length}</strong></div><div className="stat"><span className="muted">Violations</span><strong>{result?.violations?.length??"—"}</strong></div></div>
     <div className="toolbar"><input aria-label="Rechercher dans les traces" placeholder="Filtrer agent / statut / erreur" value={search} onChange={e=>setSearch(e.target.value)}/><button disabled={!result} onClick={()=>{if(result){const url=URL.createObjectURL(new Blob([JSON.stringify(result,null,2)],{type:"application/json"}));const a=document.createElement("a");a.href=url;a.download="agentmesh-r2-run.json";a.click();URL.revokeObjectURL(url);}}}>Exporter JSON</button></div>
     <div className="trace-wrap"><table className="trace"><thead><tr><th>Agent</th><th>Statut</th><th>Tentative</th><th>Durée (ms)</th></tr></thead><tbody>
      {filtered.map((e,i)=><tr key={i}><td>{e.agent??"—"}</td><td>{e.status??"—"}</td><td>{e.attempt??"—"}</td><td>{e.duration_ms??"—"}</td></tr>)}
      {!filtered.length&&<tr><td colSpan={4} className="muted">Aucune trace correspondante</td></tr>}
     </tbody></table></div>
     {result&&<details><summary>Réponse brute</summary><pre>{JSON.stringify(result,null,2)}</pre></details>}
    </section>
   </div>
  </main>
 </div>;
}
createRoot(document.getElementById("root")!).render(<React.StrictMode><App/></React.StrictMode>);
