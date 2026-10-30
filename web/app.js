const $=id=>document.getElementById(id);
const panels=[...document.querySelectorAll("[data-panel]")];
let latest=null;let history=[];let graphModel=null;
const escapeHTML=s=>String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
function show(name){panels.forEach(p=>p.hidden=p.dataset.panel!==name);document.querySelectorAll(".nav").forEach(b=>b.classList.toggle("active",b.dataset.view===name));$("pageTitle").textContent=({"overview":"Vue générale","graph":"Graphe d'agents","inverse":"Inversion croisée","traces":"Traces et métriques","hybrid":"Laboratoire hybride"})[name];}
document.querySelectorAll(".nav").forEach(b=>b.addEventListener("click",()=>show(b.dataset.view)));
async function request(path,payload){const init=payload===undefined?{}:{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)};init.headers={...(init.headers||{}),...((window.agentmeshToken||"")?{"Authorization":"Bearer "+window.agentmeshToken}:{})};const res=await fetch(path,init);let data;try{data=await res.json()}catch{throw Error("Réponse API invalide")}if(!res.ok)throw Error(data.message||data.error||"Erreur HTTP "+res.status);return data;}
async function health(){try{const data=await request("/api/health");$("health").textContent="● API "+data.status+" / "+data.version;$("connection").textContent="● API CONNECTÉE";}catch(e){$("health").textContent="● API indisponible";$("connection").textContent="● HORS LIGNE";}}
let replayTimer=null,replayIndex=0,replayEvents=[],selectedNode=null;
function stopReplay(){if(replayTimer!==null){clearTimeout(replayTimer);replayTimer=null;}}
function graphEvents(data){if(Array.isArray(data?.trace))return data.trace;if(Array.isArray(data?.output?.trace))return data.output.trace;if(Array.isArray(data?.output?.output?.trace))return data.output.output.trace;return [];}
function renderGraph(host,model,selectable=false,trace=[],active=null){
 const nodes=model.nodes||[],cx=300,cy=270,radius=187;
 const positions={};
 const core=nodes.includes("Supervisor")?"Supervisor":nodes[Math.floor(nodes.length/2)];
 const satellite=nodes.filter(x=>x!==core);
 positions[core]=[cx,cy];
 satellite.forEach((name,i)=>{const angle=-Math.PI/2+2*Math.PI*i/satellite.length;positions[name]=[cx+radius*Math.cos(angle),cy+radius*Math.sin(angle)]});
 const activated=new Set(trace.flatMap(e=>[e.agent,e.supervisor?"Supervisor":null]).filter(Boolean).map(v=>String(v).toLowerCase()));
 const activeName=active?(active.agent|| (active.supervisor?"Supervisor":active.decision?"Supervisor":null)):"";
 const edgeList=model.edges||[];
 let svg='<svg viewBox="0 0 600 550" role="img" aria-label="Réseau centré sur la supervision et les agents">';
 svg+='<defs><filter id="meshGlow"><feGaussianBlur stdDeviation="4"/></filter></defs>';
 for(const [a,b] of edgeList){if(!positions[a]||!positions[b])continue;const [x1,y1]=positions[a],[x2,y2]=positions[b];svg+='<line x1="'+x1+'" y1="'+y1+'" x2="'+x2+'" y2="'+y2+'" stroke="#3b668a" stroke-width="2" stroke-opacity=".6" stroke-dasharray="7 5"/>';}
 for(const name of satellite){const [x,y]=positions[name];svg+='<line x1="'+cx+'" y1="'+cy+'" x2="'+x+'" y2="'+y+'" stroke="#204861" stroke-width="1.5" stroke-opacity=".65"/>';}
 for(const name of nodes){const [x,y]=positions[name],focused=String(activeName).toLowerCase()===name.toLowerCase(),done=activated.has(name.toLowerCase()),selected=selectedNode===name;
 const fill=focused?"#17655c":name===core?"#29376a":done?"#174e52":"#152a45";
 const stroke=focused?"#79ffe4":selected?"#a08fff":done?"#47d6c8":"#4b779d";
 const w=name===core?148:126,h=46;
 svg+='<g class="graph-node'+(focused?" graph-running":"")+'" data-node="'+escapeHTML(name)+'" tabindex="0" role="button" aria-label="Inspecter '+escapeHTML(name)+'"><rect x="'+(x-w/2)+'" y="'+(y-h/2)+'" width="'+w+'" height="'+h+'" rx="13" fill="'+fill+'" stroke="'+stroke+'" stroke-width="'+(focused?3:1.5)+'"/><text x="'+x+'" y="'+(y+5)+'" font-size="13" font-weight="'+(name===core?700:500)+'" fill="#eaf7ff" text-anchor="middle">'+escapeHTML(name)+'</text></g>';
 }
 svg+='</svg>';host.innerHTML=svg;
 if(selectable)host.querySelectorAll(".graph-node").forEach(el=>{const action=()=>{selectedNode=el.dataset.node;const related=trace.filter(e=>String(e.agent|| (e.supervisor?"Supervisor":"")).toLowerCase()===selectedNode.toLowerCase());$("nodeDetails").textContent=selectedNode+" — "+(related.length?JSON.stringify(related,null,2):"Aucun événement disponible");renderGraph(host,model,true,trace,active)};el.addEventListener("click",action);el.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();action()}})});
}
function replayFrame(){
 if(!graphModel||!replayEvents.length)return;
 const event=replayEvents[Math.min(replayIndex,replayEvents.length-1)];
 const prefix=replayEvents.slice(0,replayIndex+1);
 renderGraph($("agentGraph"),graphModel,true,prefix,event);
 renderGraph($("overviewGraph"),graphModel,false,prefix,event);
 const label=(event.agent|| (event.supervisor?"Supervisor":"Réviseur"))+" · "+(event.status||event.supervisor||event.decision||"traitement")+" · étape "+(replayIndex+1)+"/"+replayEvents.length;
 $("graphEvent").textContent=label;
 $("graphReplayStatus").textContent="● "+(replayTimer!==null?"Lecture":"Étape "+(replayIndex+1));
 $("graphLiveStatus").textContent="● Replay "+(replayIndex+1)+"/"+replayEvents.length;
}
function advanceReplay(){
 if(!replayEvents.length)return;
 if(replayIndex>=replayEvents.length-1){stopReplay();replayFrame();return}
 replayIndex++;replayFrame();
 replayTimer=setTimeout(advanceReplay,Number($("replaySpeed").value)||900);
}
function startReplay(){stopReplay();replayEvents=graphEvents(latest);if(!replayEvents.length){$("graphEvent").textContent="Aucune trace disponible.";return}replayIndex=0;replayFrame();replayTimer=setTimeout(advanceReplay,Number($("replaySpeed").value)||900);}
$("replayOverview").addEventListener("click",()=>{startReplay();show("graph")});
$("replayGraph").addEventListener("click",startReplay);
$("pauseReplay").addEventListener("click",()=>{stopReplay();$("graphReplayStatus").textContent="● Pause"});
$("stepReplay").addEventListener("click",()=>{stopReplay();if(!replayEvents.length)replayEvents=graphEvents(latest);replayIndex=Math.min(replayIndex+1,Math.max(0,replayEvents.length-1));replayFrame()});
async function loadGraph(){try{graphModel=await request("/api/architecture");renderGraph($("agentGraph"),graphModel,true,latest?.trace||[]);renderGraph($("overviewGraph"),graphModel,false,latest?.trace||[]);}catch(e){$("agentGraph").textContent="Échec de chargement : "+e.message;}}
function fmt(n){return Number(n).toExponential(3)}
let lastResidualSeries=[];
function plot(values){
 if(!Array.isArray(values)||!values.length)return;
 lastResidualSeries=values;
 const logScale=$("logScale")?.checked??false;
 const transformed=values.map(v=>logScale?Math.log10(Math.max(v,1e-14)):v);
 const w=600,h=255,p=35,hi=Math.max(...transformed),lo=Math.min(...transformed),range=Math.max(1e-12,hi-lo);
 const coords=transformed.map((v,i)=>[p+i*(w-2*p)/Math.max(values.length-1,1),h-p-(v-lo)/range*(h-2*p)]);
 const path=coords.map(([x,y],i)=>(i?"L":"M")+x.toFixed(2)+","+y.toFixed(2)).join(" ");
 const lines=[0,.25,.5,.75,1].map(f=>'<line x1="'+p+'" x2="'+(w-p)+'" y1="'+(p+f*(h-2*p))+'" y2="'+(p+f*(h-2*p))+'" stroke="#304660" stroke-dasharray="3 4"/>').join("");
 $("chart").innerHTML='<svg viewBox="0 0 '+w+' '+h+'" role="img" aria-label="Résidu sur échelle '+(logScale?"logarithmique":"linéaire")+'">'+lines+'<path d="'+path+'" fill="none" stroke="#5eead4" stroke-width="3"/><text x="35" y="18" fill="#c0d7f4" font-size="14">Résidu final : '+fmt(values.at(-1))+'</text><text x="35" y="250" fill="#87a5c8" font-size="12">0</text><text x="460" y="250" fill="#87a5c8" font-size="12">'+(values.length-1)+' itérations</text></svg>';
}
$("logScale")?.addEventListener("change",()=>plot(lastResidualSeries));
function inspectTrace(data){
 const diagnostic=data?.observability||null;
 const summary=$("traceSummary"), timeline=$("traceTimeline"), select=$("traceAgentFilter");
 if(!diagnostic){summary.textContent="Aucun diagnostic structuré disponible pour cette exécution.";timeline.textContent="Aucun événement.";return;}
 const entries=diagnostic.events||[];
 summary.innerHTML=[["Événements",diagnostic.event_count],["Défaillances observées",diagnostic.failure_count],["Agents",Object.keys(diagnostic.agents||{}).length],["Tracé limité",diagnostic.truncated?"Oui":"Non"]].map(([k,v])=>'<div class="analysis-cell"><small>'+escapeHTML(k)+'</small><strong>'+escapeHTML(v)+'</strong></div>').join("");
 select.innerHTML='<option value="">Tous les agents</option>'+Object.keys(diagnostic.agents||{}).map(n=>'<option value="'+escapeHTML(n)+'">'+escapeHTML(n)+'</option>').join("");
 const render=()=>{const value=select.value;const filtered=entries.filter(e=>!value||e.agent===value);timeline.innerHTML=filtered.map(e=>'<div class="step"><strong>'+escapeHTML(e.agent)+'</strong> · '+escapeHTML(e.status)+' · tentative '+escapeHTML(e.attempt??"—")+' · '+escapeHTML(e.duration_ms??"—")+' ms'+(e.error_type?'<p>Erreur : '+escapeHTML(e.error_type)+'</p>':'')+(e.violations?.length?'<p>Contraintes : '+escapeHTML(e.violations.join(", "))+'</p>':'')+'</div>').join("")||"Aucun événement correspondant.";};
 select.onchange=render;render();
}
function record(kind,data){latest=data;stopReplay();replayEvents=graphEvents(data);replayIndex=0;inspectTrace(data);history.unshift({kind,time:new Date().toLocaleTimeString("fr-FR"),accepted:kind==="inverse"?data.feedback.converged:data.accepted,data});history=history.slice(0,40);$("output").textContent=JSON.stringify(data,null,2);$("status").textContent=kind==="inverse"?(data.feedback.converged?"Convergé":"Non convergé"):(data.accepted?"Accepté":"Rejeté");$("calls").textContent=data.metrics?.agent_calls??"—";$("duration").textContent=data.metrics?.duration_ms===undefined?"—":data.metrics.duration_ms+" ms";$("checks").textContent=data.metrics?.constraint_checks??"—";$("history").innerHTML=history.map((r,i)=>'<button class="history-entry" data-i="'+i+'"><strong>'+escapeHTML(r.kind)+'</strong> '+escapeHTML(r.time)+' · '+(r.accepted?"OK":"Non validé")+'</button>').join("");$("history").querySelectorAll("button").forEach(b=>b.addEventListener("click",()=>{$("output").textContent=JSON.stringify(history[Number(b.dataset.i)].data,null,2)}));if(graphModel){renderGraph($("overviewGraph"),graphModel,false,data.trace||[]);renderGraph($("agentGraph"),graphModel,true,data.trace||[]);}}
$("runAgents").addEventListener("click",async()=>{const b=$("runAgents");b.disabled=true;$("agentNotice").textContent="Exécution en cours";try{const data=await request("/api/run",{mode:"agents",objective:$("objective").value,contains:$("contains").value,attempts:Number($("attempts").value)});record("agents",data);$("steps").innerHTML=(data.trace||[]).map(e=>'<div class="step">'+escapeHTML(e.agent||"Supervisor")+" · "+escapeHTML(e.status||e.supervisor)+" · "+escapeHTML(e.duration_ms===undefined?"":e.duration_ms+" ms")+'</div>').join("");$("agentOutput").textContent=data.output;$("agentNotice").textContent="Exécution terminée";}catch(e){$("agentNotice").textContent="Erreur : "+e.message;}finally{b.disabled=false;}});
$("runAdaptive").addEventListener("click",async()=>{const b=$("runAdaptive");b.disabled=true;$("agentNotice").textContent="Correction réflexive en cours…";try{const requirements=$("adaptiveRequirements").value.split(";").map(s=>s.trim()).filter(Boolean);const data=await request("/api/run",{mode:"adaptive",objective:$("objective").value,requirements,attempts:Number($("attempts").value)});record("adaptive",data);$("steps").innerHTML=(data.trace||[]).map(e=>'<div class="step">Itération '+e.attempt+' · '+escapeHTML(e.decision)+' · score '+Math.round(100*e.score)+'% · violations : '+escapeHTML(e.violations.join(", ")||"aucune")+'</div>').join("");$("agentOutput").textContent=data.output;$("agentNotice").textContent=data.accepted?"Révision acceptée":"Révision rejetée : contraintes restantes";}catch(e){$("agentNotice").textContent="Erreur : "+e.message;}finally{b.disabled=false;}});
$("gain").addEventListener("input",()=>$("gainLabel").value=$("gain").value);
$("runInverse").addEventListener("click",async()=>{const b=$("runInverse");b.disabled=true;$("inverseNotice").textContent="Calcul en cours";try{const matrix=[[$("w00").valueAsNumber,$("w01").valueAsNumber],[$("w10").valueAsNumber,$("w11").valueAsNumber]];const target=[$("targetA").valueAsNumber,$("targetB").valueAsNumber];if(!matrix.flat().concat(target).every(Number.isFinite))throw Error("Valeurs numériques invalides");const data=await request("/api/run",{mode:"inverse",matrix,target,gain:Number($("gain").value)});record("inverse",data);plot(data.feedback.history);$("inverseStats").innerHTML=[["Iterations",data.feedback.iterations],["Résidu",fmt(data.feedback.residual)],["Norme ∞",data.stability.norm_upper_bound.toFixed(4)],["Solution régularisée",data.inverse.map(v=>v.toFixed(4)).join(" / ")],["Statut faisabilité",data.feasibility.status],["Contraction suffisante",data.stability.sufficient_contraction?"Oui":"Non certifiée"]].map(([k,v])=>'<div class="analysis-cell"><small>'+escapeHTML(k)+'</small><strong>'+escapeHTML(v)+'</strong></div>').join("");$("inverseComment").textContent=(data.feedback.converged?"La boucle a atteint sa tolérance de résidu. ":"La boucle n’a pas convergé dans le budget. ")+(data.feasibility.status==="undetermined"?"Les intervalles ne prouvent PAS la faisabilité. ":"Cible hors des bornes : impossibilité certifiée dans ce modèle. ")+(data.stability.sufficient_contraction?"La borne de norme certifie une contraction du modèle non projeté.":"Absence de certificat de contraction, sans preuve d'instabilité.");$("inverseNotice").textContent="Diagnostic calculé";}catch(e){$("inverseNotice").textContent="Erreur : "+e.message;}finally{b.disabled=false;}});
$("refreshGraph").addEventListener("click",loadGraph);
$("clearHistory").addEventListener("click",()=>{history=[];latest=null;$("history").textContent="Aucune exécution";$("output").textContent='{"message":"Aucune exécution"}';});
$("downloadJson").addEventListener("click",()=>{if(!latest){$("output").textContent="Aucun résultat à exporter";return;}const blob=new Blob([JSON.stringify(latest,null,2)],{type:"application/json"});const link=document.createElement("a");link.href=URL.createObjectURL(blob);link.download="agentmesh-result.json";link.click();URL.revokeObjectURL(link.href);});
health();loadGraph();show("overview");

$("runHybrid").addEventListener("click",async()=>{const b=$("runHybrid");b.disabled=true;$("hybridNotice").textContent="Comparaison en cours…";try{
const requirements=$("hybridRequirements").value.split(";").map(s=>s.trim()).filter(Boolean);
const text=await request("/api/run",{mode:"hybrid",branch:"text",objective:$("hybridObjective").value,requirements});
const matrix=[[$("w00").valueAsNumber,$("w01").valueAsNumber],[$("w10").valueAsNumber,$("w11").valueAsNumber]], target=[$("targetA").valueAsNumber,$("targetB").valueAsNumber];
const numeric=await request("/api/run",{mode:"hybrid",branch:"numeric",matrix,target,gain:Number($("gain").value)});
const diagnostic=await request("/api/run",{mode:"diagnostics",matrix,state:numeric.output.state,target});
$("hybridComparison").innerHTML=[
["Conformité textuelle",Math.round(text.diagnostics.fraction_passing*100)+" %"],
["Révisions",text.output.metrics.revision_calls],
["Résidu numérique",numeric.output.residual.toExponential(3)],
["Itérations",numeric.output.iterations],
["Contraction suffisante",numeric.diagnostics.contraction_sufficient?"Oui":"Non certifiée"],
["Conditionnement estimé",diagnostic.conditioning.condition_number===null?"Singulier / indéterminé":Number(diagnostic.conditioning.condition_number).toFixed(4)]
].map(([a,v])=>'<div class="analysis-cell"><small>'+escapeHTML(a)+'</small><strong>'+escapeHTML(v)+'</strong></div>').join("");
$("conditionDetails").textContent=JSON.stringify(diagnostic.conditioning,null,2);
$("hybridJson").textContent=JSON.stringify({text,numeric,diagnostic},null,2);
$("hybridNotice").textContent="Comparaison terminée (métriques distinctes, non agrégées).";
record("hybrid",{accepted:text.accepted&&numeric.accepted,text,numeric,diagnostic});
}catch(e){$("hybridNotice").textContent="Erreur : "+e.message}finally{b.disabled=false}});

$("runGainSearch").addEventListener("click",async()=>{
 const b=$("runGainSearch");b.disabled=true;$("gainResults").textContent="Optimisation en cours…";
 try{
  const matrix=[[$("w00").valueAsNumber,$("w01").valueAsNumber],[$("w10").valueAsNumber,$("w11").valueAsNumber]];
  const target=[$("targetA").valueAsNumber,$("targetB").valueAsNumber];
  const tolerance=Number($("gainTolerance").value),max_steps=Number($("gainBudget").value);
  if(!matrix.flat().concat(target,tolerance,max_steps).every(Number.isFinite))throw Error("Entrées invalides");
  const data=await request("/api/run",{mode:"gain_search",matrix,target,tolerance,max_steps,gains:[.1,.25,.5,.75,1,1.25]});
  const chosen=data.best;$("gain").value=chosen.gain;$("gainLabel").value=chosen.gain;
  $("gainResults").innerHTML="<p>Gain sélectionné : <strong>"+chosen.gain+"</strong> · "+chosen.iterations+" itérations · résidu "+chosen.residual.toExponential(3)+"</p>"+
   data.candidates.map(c=>'<div class="step">η='+c.gain+' · '+c.iterations+' it. · '+c.residual.toExponential(2)+' · '+(c.converged?"Convergé":"Budget épuisé")+'</div>').join("");
  plot(chosen.history);
 }catch(e){$("gainResults").textContent="Erreur : "+e.message}finally{b.disabled=false}
});

$("loadPersistentTraces").addEventListener("click",async()=>{
 const host=$("persistentTraceList");host.textContent="Chargement…";
 try{
 const result=await request("/api/observability");
 if(!result.enabled){host.textContent="Persistance désactivée. Configure AGENTMESH_DB_PATH pour conserver les exécutions.";return;}
 host.innerHTML=(result.runs||[]).map(r=>'<button class="history-entry" data-id="'+escapeHTML(r.id)+'">'+escapeHTML(r.created)+' · '+escapeHTML(r.mode)+' · '+r.failure_count+' échecs observés</button>').join("")||"Aucune exécution conservée.";
 host.querySelectorAll("button").forEach(b=>b.addEventListener("click",async()=>{try{const run=await request("/api/runs/"+encodeURIComponent(b.dataset.id));inspectTrace(run);$("output").textContent=JSON.stringify(run,null,2);}catch(e){host.textContent="Erreur : "+e.message;}}));
 }catch(e){host.textContent="Erreur : "+e.message;}
});
