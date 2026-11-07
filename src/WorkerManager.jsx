import React,{useState} from "react";
export default function WorkerManager(){
 const [token,setToken]=useState("");
 const [agent,setAgent]=useState("Aria");
 const [kind,setKind]=useState("chat");
 const [workers,setWorkers]=useState([]);
 const [message,setMessage]=useState("Połącz z backendem, aby zobaczyć rzeczywiste workery.");
 const [busy,setBusy]=useState(false);
 async function request(path,body){
   const res=await fetch(path,{method:body?"POST":"GET",headers:{"Authorization":"Bearer "+token,...(body?{"Content-Type":"application/json"}:{})},...(body?{body:JSON.stringify(body)}:{})});
   const data=await res.json();if(!res.ok)throw new Error(data.error||"Błąd API");return data;
 }
 async function refresh(){setBusy(true);try{const d=await request("/api/workers");setWorkers(d.workers||[]);setMessage("Dane z serwera.");}catch(e){setMessage(e.message);}finally{setBusy(false)}}
 async function create(){setBusy(true);try{await request("/api/workers/create",{agent,kind});const d=await request("/api/workers");setWorkers(d.workers||[]);setMessage("Dodano slot workera. Uruchomiona usługa przejmie go automatycznie.");}catch(e){setMessage(e.message)}finally{setBusy(false)}}
 async function remove(id){setBusy(true);try{await request("/api/workers/remove",{id});const d=await request("/api/workers");setWorkers(d.workers||[]);setMessage("Zlecono zatrzymanie workera.");}catch(e){setMessage(e.message)}finally{setBusy(false)}}
 return <section className="glass-card"><div className="panel-header"><div><h2>Menedżer workerów</h2><p>Tworzenie i zatrzymywanie jednostek agentów</p></div></div>
 <label className="setting">Token sesji<input type="password" autoComplete="off" value={token} onChange={e=>setToken(e.target.value)} placeholder="MARA_SESSION_TOKEN"/></label>
 <div className="composer"><select aria-label="Agent" value={agent} onChange={e=>setAgent(e.target.value)}>{["Aria","Alex","Astyria","Aurelius"].map(a=><option key={a}>{a}</option>)}</select><select aria-label="Typ workera" value={kind} onChange={e=>setKind(e.target.value)}><option value="chat">AI / czat</option><option value="diagnostics">Diagnostyka</option></select><button disabled={busy||!token} onClick={create}>+ Worker</button><button disabled={busy||!token} onClick={refresh}>Odśwież</button></div>
 <p role="status">{message}</p><div className="task-list">{workers.map(w=><div className="task-row" key={w.id}><span><strong>{w.agent}</strong> · {w.kind} · {w.desired}<br/><small>{w.id.slice(0,12)}…</small></span><button disabled={busy||w.desired!=="running"} onClick={()=>remove(w.id)}>Zatrzymaj</button></div>)}</div>
 <p className="hint">Lista pokazuje żądany stan slotów, nie potwierdza aktywnego procesu. Zatrzymanie podczas zadania może spowodować ponowne wykonanie po restarcie.</p></section>;
