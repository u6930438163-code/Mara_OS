import React,{useEffect,useState} from "react";
const defaults=["chat","terminal","logs"];
const labels={chat:"Czat agentów",terminal:"Terminal",logs:"Logi",workers:"Workery",files:"Pliki",resources:"Zasoby"};
export default function LiveDesktop(){
 const [token,setToken]=useState("");
 const [windows,setWindows]=useState(defaults);
 const [cursor,setCursor]=useState(0);
 const [message,setMessage]=useState("Tryb lokalny: połącz API, aby odbierać zdarzenia agentów.");
 const [connected,setConnected]=useState(false);
 const [activity,setActivity]=useState("diagnostics");
 const [pinned,setPinned]=useState(["chat"]);
 const [autoLayout,setAutoLayout]=useState(false);
 useEffect(()=>{
   if(!connected||!token)return;
   let cancelled=false;let timer;
   async function poll(){
     try{
       const response=await fetch("/api/desktop/events?since="+cursor,{headers:{Authorization:"Bearer "+token}});
       if(!response.ok)throw new Error("API: "+response.status);
       const data=await response.json();
       if(cancelled)return;
       if(data.events?.length){
         setWindows(current=>{let next=[...current];for(const e of data.events){if(e.action==="show"&&!next.includes(e.window))next.push(e.window);if(e.action==="hide"&&!pinned.includes(e.window))next=next.filter(x=>x!==e.window);}return next});
         setCursor(data.events[data.events.length-1].id);
       }
       setMessage("Połączono z kanałem zdarzeń interfejsu.");
     }catch(e){if(!cancelled)setMessage(e.message)}
     if(!cancelled)timer=setTimeout(poll,2000);
   }
   poll();return()=>{cancelled=true;clearTimeout(timer)};
 },[connected,token,cursor,pinned]);
 async function applyLayout(){
   if(!token){setMessage("Podaj token sesji.");return;}
   try{
     const q=new URLSearchParams({activity});pinned.forEach(x=>q.append("pinned",x));
     const res=await fetch("/api/desktop/layout?"+q.toString(),{headers:{Authorization:"Bearer "+token}});
     if(!res.ok)throw new Error("API: "+res.status);
     const data=await res.json();setWindows(data.visible);setMessage("Zastosowano sugerowany układ: "+data.activity);
   }catch(e){setMessage(e.message)}
 }
 useEffect(()=>{if(connected&&autoLayout)applyLayout()},[activity,connected,autoLayout]);
 function toggle(id){setWindows(old=>old.includes(id)?old.filter(x=>x!==id):[...old,id])}
 return <section className="glass-card"><div className="panel-header"><div><h2>Live AI Desktop</h2><p>Dynamiczne okna według zdarzeń agentów</p></div><span className="pill">{connected?"Kanał API":"Podgląd lokalny"}</span></div>
 <label className="setting">Token sesji<input type="password" autoComplete="off" value={token} onChange={e=>setToken(e.target.value)} placeholder="MARA_SESSION_TOKEN"/></label>
 <div className="composer"><button disabled={!token} onClick={()=>setConnected(v=>!v)}>{connected?"Rozłącz":"Połącz zdarzenia"}</button><button onClick={()=>setWindows(defaults)}>Przywróć układ</button></div>
 <div className="composer"><select aria-label="Tryb pracy" value={activity} onChange={e=>setActivity(e.target.value)}>{["idle","chat","diagnostics","development","monitoring"].map(x=><option key={x} value={x}>{({idle:"Spoczynek",chat:"Czat",diagnostics:"Diagnostyka",development:"Programowanie",monitoring:"Monitorowanie"})[x]}</option>)}</select><button disabled={!token} onClick={applyLayout}>Dopasuj okna</button><label><input type="checkbox" checked={autoLayout} onChange={e=>setAutoLayout(e.target.checked)}/> Auto układ</label></div>
 <p role="status">{message}</p><div className="agent-grid">{Object.keys(labels).map(id=><div className="agent-card" key={id}><strong>{labels[id]}</strong><p>{windows.includes(id)?"Widoczne":"Ukryte"}</p><label><input type="checkbox" checked={pinned.includes(id)} onChange={e=>setPinned(old=>e.target.checked?[...old,id]:old.filter(x=>x!==id))}/> Przypnij</label><button onClick={()=>toggle(id)}>{windows.includes(id)?"Ukryj":"Pokaż"}</button></div>)}</div>
 <p className="hint">Sterowanie dotyczy paneli Mara_OS w przeglądarce. Nie zamyka natywnych okien KDE i nie wykonuje poleceń systemowych.</p></section>;
