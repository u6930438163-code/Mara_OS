import React,{useState} from "react";
import "./AgentActivity.css";
const sample=[
 {id:"a1",agent:"Aria",title:"Diagnostyka usług",state:"demo",progress:60,step:"Sprawdzanie statusu usług",script:"systemctl --failed\njournalctl -p err -n 30 --no-pager",description:"Wyświetla usługi systemd w stanie awarii i 30 ostatnich błędów dziennika. Polecenia są tylko przykładem; nie zostały wykonane.",logs:[{type:"info",text:"Przykład: pobieranie listy usług"},{type:"ok",text:"Przykład: zakończono etap 1"},{type:"info",text:"Przykład: analiza logów"}]},
 {id:"a2",agent:"Alex",title:"Kontrola API",state:"demo",progress:35,step:"Test endpointu health",script:"curl -fsS --max-time 10 http://localhost:8000/api/health",description:"Weryfikuje odpowiedź endpointu zdrowia z limitem 10 sekund. Adres i wynik wymagają potwierdzenia w rzeczywistym środowisku.",logs:[{type:"info",text:"Przykład: przygotowano zapytanie HTTP"}]},
 {id:"a3",agent:"Astyria",title:"Audyt repozytorium",state:"demo",progress:80,step:"Przegląd zmian Git",script:"git status --short\ngit log -5 --oneline",description:"Wyświetla zmienione pliki i pięć ostatnich commitów, bez modyfikowania repozytorium.",logs:[{type:"info",text:"Przykład: analiza zmian"},{type:"ok",text:"Przykład: odczyt historii"}]},
 {id:"a4",agent:"Aurelius",title:"Stan KDE Plasma",state:"demo",progress:15,step:"Sprawdzenie wersji",script:"plasmashell --version\nkwin_wayland --version",description:"Sprawdza wersje powłoki Plasma i kompozytora KWin, jeśli narzędzia są dostępne w natywnym Linux.",logs:[{type:"info",text:"Przykład: oczekiwanie na środowisko KDE"}]}
];
export default function AgentActivity({events=null}) {
 const [expanded,setExpanded]=useState({});
 const [filter,setFilter]=useState("Wszyscy");
 const [tab,setTab]=useState({});
 const live=Array.isArray(events);
 const items=(live?events:sample).filter(x=>filter==="Wszyscy"||x.agent===filter);
 return <section className="activity-root">
 <div className="activity-head"><div><h2>Praca agentów AI</h2><small>{live?"Zdarzenia z podłączonego źródła":"TRYB DEMO — przykładowe zadania, bez wykonywania poleceń"}</small></div><select aria-label="Filtr agenta" value={filter} onChange={e=>setFilter(e.target.value)}>{["Wszyscy","Aria","Alex","Astyria","Aurelius"].map(n=><option key={n}>{n}</option>)}</select></div>
 <div className="activity-list">{items.length===0?<p>Brak zadań dla wybranego agenta.</p>:items.map(item=><article key={item.id} className="activity-task">
 <div className="activity-top"><span className="activity-avatar">{item.agent?.[0]||"AI"}</span><div className="activity-summary"><strong>{item.agent} · {item.title}</strong><small>{item.step||"Brak informacji o etapie"}</small></div><span className="activity-state">{live?(item.state||"nieznany"):"DEMO"}</span></div>
 <div className="activity-progress" role="progressbar" aria-label={"Postęp: "+item.title} aria-valuemin={0} aria-valuemax={100} aria-valuenow={typeof item.progress==="number"?Math.max(0,Math.min(100,item.progress)):undefined}><div style={{width:typeof item.progress==="number"?Math.max(0,Math.min(100,item.progress))+"%":"0%"}}/></div>
 <div className="activity-actions"><span>{typeof item.progress==="number"?item.progress+"% (etapy)":"Postęp nieznany"}</span><button aria-expanded={!!expanded[item.id]} onClick={()=>setExpanded(v=>({...v,[item.id]:!v[item.id]}))}>{expanded[item.id]?"Zwiń":"Rozwiń szczegóły"} {expanded[item.id]?"▴":"▾"}</button></div>
 {expanded[item.id]&&<div className="activity-details"><div className="activity-tabs">{[["description","Opis"],["script","Pełny skrypt"],["logs","Logi"]].map(([key,label])=><button key={key} className={(tab[item.id]||"description")===key?"active":""} onClick={()=>setTab(v=>({...v,[item.id]:key}))}>{label}</button>)}</div>
 {(tab[item.id]||"description")==="description"&&<p>{item.description||"Opis nie został jeszcze przesłany przez workera."}</p>}
 {tab[item.id]==="script"&&<div className="activity-code"><div><span>bash · tylko podgląd</span><button onClick={()=>navigator.clipboard?.writeText(item.script||"")}>Kopiuj</button></div><pre><code>{item.script||"Skrypt niedostępny"}</code></pre></div>}
 {tab[item.id]==="logs"&&<div className="activity-logs">{(item.logs||[]).length?(item.logs||[]).map((log,i)=><div key={i} className={"activity-log "+(log.type||"info")}><span>{log.type==="ok"?"✓":log.type==="error"?"✕":"›"}</span>{log.text}</div>):<p>Brak logów.</p>}</div>}
 </div>}
 </article>)}</div>
 <p className="activity-foot">Rzeczywisty postęp wymaga identyfikatora zadania, zdarzeń z workera, czasu i kodu zakończenia. Panel nie uruchamia skryptów.</p>
 </section>;
}
