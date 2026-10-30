import React from "react";
import {createRoot} from "react-dom/client";
import {ReactFlow,Background,Controls,type Node,type Edge} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

const nodes:Node[]=[
 {id:"analyzer",position:{x:30,y:110},data:{label:"Analyzer"}},
 {id:"supervisor",position:{x:280,y:110},data:{label:"Supervisor"}},
 {id:"critic",position:{x:530,y:110},data:{label:"Critic"}}
];
const edges:Edge[]=[
 {id:"a-s",source:"analyzer",target:"supervisor"},
 {id:"s-c",source:"supervisor",target:"critic"}
];
function App(){
 return <main style={{fontFamily:"system-ui",background:"#09121e",color:"#ecf3ff",minHeight:"100vh",padding:24}}>
 <h1>AgentMesh V2 — module optionnel</h1>
 <p>Explorateur expérimental. L'interface historique reste disponible séparément sur le serveur Python.</p>
 <section style={{height:500,border:"1px solid #324966",borderRadius:12}}>
 <ReactFlow nodes={nodes} edges={edges} fitView><Background/><Controls/></ReactFlow></section>
 </main>;
}
createRoot(document.getElementById("root")!).render(<React.StrictMode><App/></React.StrictMode>);
