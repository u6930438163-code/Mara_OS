import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import Dalle3Studio from "../ui/Dalle3Studio.jsx";
import IntegrationsPanel from "./IntegrationsPanel.jsx";
import ChatDallePrompts from "./ChatDallePrompts.jsx";
import AgentAvatarEditor from "./AgentAvatarEditor.jsx";
import MobilePlasma from "./MobilePlasma.jsx";
import RichText from "./RichText.jsx";
import AgentActivity from "./AgentActivity.jsx";
import WorkerManager from "./WorkerManager.jsx";
import "../ui/dalle3-studio.css";
import "./style.css";

const people = ["Aria", "Alex", "Astyria", "Aurelius"];
const sections = [["plasma","Pulpit Plasma"],["chat","Czat"],["terminal","Terminal"],["agents","Agenci"],["desktops","Pulpity AI"],["tasks","Zadania"],["activity","Praca AI"],["workers","Workery"],["studio","DALL·E 3"],["integrations","Integracje AI"],["settings","Ustawienia"]];
function App() {
  const [section,setSection] = useState("plasma");
  const [desktopUser,setDesktopUser] = useState("Aria");
  const [avatars,setAvatars] = useState({});
  const [agent,setAgent] = useState("Wszyscy");
  const [engine,setEngine] = useState("OpenAI API");
  const [draft,setDraft] = useState("");
  const [messages,setMessages] = useState([]);
  const [terminal,setTerminal] = useState("help");
  const [history,setHistory] = useState([]);
  const [tasks,setTasks] = useState([]);
  const [task,setTask] = useState("");
  const [glass,setGlass] = useState(75);
  const [glow,setGlow] = useState(true);
  const [wallpaper,setWallpaper] = useState("");
  const [token,setToken] = useState("");
  const [sidebar,setSidebar] = useState(false);
  const [showInfo,setShowInfo] = useState(true);
  function send(e) {
    e.preventDefault();
    if (!draft.trim()) return;
    setMessages(m=>[...m,{who:"Ty",to:agent,text:draft.trim(),time:new Date().toLocaleTimeString("pl-PL")}]);
    setDraft("");
  }
  function command(e) {
    e.preventDefault();
    const value=terminal.trim();
    if (!value) return;
    const output=value==="help"?"Dostępne polecenia demonstracyjne: help, clear, agents, about":value==="agents"?people.join(" · "):value==="about"?"Mara_OS — prototyp interfejsu":value==="clear"?"":"Polecenie nie zostało wykonane — terminal nie jest połączony z systemem.";
    setHistory(h=>value==="clear"?[]:[...h,{value,output}]);
    setTerminal("");
  }
  function addTask(e) {
    e.preventDefault();
    if (!task.trim()) return;
    setTasks(t=>[...t,{id:Date.now()+Math.random(),text:task.trim(),done:false}]);
    setTask("");
  }
  return <div className={`desktop ${glow?"glow":""}`} style={{"--glass":glass/100,"--wallpaper":wallpaper?`url("${wallpaper}")`:"none"}}>
    <div className="wallpaper" aria-hidden="true"/>
    <div className="workspace">
      <aside className={`sidebar ${sidebar?"expanded":""}`}>
        <div className="logo"><span className="logo-mark">M</span><div><strong>Mara_OS</strong><small>Workspace</small></div></div>
        <nav aria-label="Główne menu">{sections.map(([key,name])=><button key={key} className={section===key?"selected":""} onClick={()=>{setSection(key);setSidebar(false)}}>{name}</button>)}</nav>
        <div className="sidebar-bottom"><span className="dot"/> Prototyp GUI</div>
      </aside>
      <div className="mainarea">
        <header className="toolbar">
          <button className="mobile-menu" onClick={()=>setSidebar(s=>!s)} aria-label="Pokaż menu">☰</button>
          <div><strong>{sections.find(s=>s[0]===section)?.[1]}</strong><small>Mara_OS / Panel główny</small></div>
          <div className="toolbar-actions"><span className="connection">● Offline demo</span><button onClick={()=>setShowInfo(v=>!v)} aria-label="Pokaż lub ukryj informacje">ⓘ</button></div>
        </header>
        {showInfo&&<div className="notice">Interaktywny szkic interfejsu. Czat, terminal i agenci nie wykonują jeszcze rzeczywistych poleceń. Tapetę ustawisz w Ustawieniach.</div>}
        {section==="plasma"&&<MobilePlasma onOpen={setSection} wallpaper={wallpaper} avatars={avatars}/>}
        {section==="chat"&&<section className="glass-card chat">
          <div className="panel-header"><div><h2>Wiadomości do agentów</h2><p>Wspólny kanał komunikacji</p></div><select aria-label="Odbiorca" value={agent} onChange={e=>setAgent(e.target.value)}>{["Wszyscy",...people].map(a=><option key={a}>{a}</option>)}</select></div>
          <div className="agent-strip">{people.map((p,i)=><button key={p} className={agent===p?"selected":""} onClick={()=>setAgent(p)}><span className={`avatar a${i}`}>{avatars[p]?<img src={avatars[p]} alt="" referrerPolicy="no-referrer"/>:p[0]}</span>{p}</button>)}</div>
          <label className="chat-token">Token sesji API <input type="password" autoComplete="off" value={token} onChange={e=>setToken(e.target.value)} placeholder="MARA_SESSION_TOKEN"/></label><ChatDallePrompts authToken={token} onImage={image=>setMessages(m=>[...m,image])}/><div className="chat-feed" aria-live="polite">{messages.length===0?<div className="empty"><span className="big-m">M</span><h3>Witaj w Mara_OS</h3><p>Tu pojawią się wiadomości i odpowiedzi agentów po podłączeniu backendu.</p></div>:messages.map((m,i)=><article key={i} className="message"><div><strong>{m.who} → {m.to}</strong><small>{m.time}</small></div><RichText text={m.text}/>{m.image&&<img src={m.image} alt={m.text} style={{maxWidth:"100%",maxHeight:440,borderRadius:12}}/>}<div className="reactions"><button onClick={e=>e.currentTarget.classList.toggle("reacted")} aria-label="Lubię">👍</button><button onClick={e=>e.currentTarget.classList.toggle("reacted")} aria-label="Nie lubię">👎</button></div></article>)}</div>
          <form className="composer" onSubmit={send}><select aria-label="Silnik AI" value={engine} onChange={e=>setEngine(e.target.value)}><option>OpenAI API</option><option>Ollama</option></select><input aria-label="Treść wiadomości" value={draft} onChange={e=>setDraft(e.target.value)} placeholder="Napisz do agentów…"/><button type="submit">Wyślij ↑</button></form>
        </section>}
        {section==="terminal"&&<section className="glass-card"><div className="panel-header"><div><h2>Terminal</h2><p>Podgląd CLI — bez wykonywania komend systemowych</p></div><span className="pill">LOCAL DEMO</span></div><div className="terminal-output"><p>$ Mara_OS terminal · tryb demonstracyjny</p>{history.map((h,i)=><div key={i}><p><b>$</b> {h.value}</p><p className="output">{h.output}</p></div>)}</div><form className="composer" onSubmit={command}><span>$</span><input aria-label="Polecenie terminala" value={terminal} onChange={e=>setTerminal(e.target.value)} placeholder="help"/><button>Uruchom</button></form></section>}
        {section==="agents"&&<section className="glass-card"><div className="panel-header"><div><h2>Czterej agenci AI</h2><p>Równorzędni współpracownicy — wizualny szkic dashboardów</p></div></div><div className="agent-grid">{people.map((p,i)=><div className="agent-card" key={p}><AgentAvatarEditor key={p} agent={p} initialUrl={avatars[p]||""} onSave={(name,url)=>setAvatars(v=>({...v,[name]:url}))}/><span className="pill">Niepołączony</span><p>Aktywność i historia będą dostępne po podłączeniu rzeczywistych logów.</p><button onClick={()=>{setAgent(p);setSection("chat")}}>Otwórz czat</button></div>)}</div></section>}
        {section==="desktops"&&<section className="glass-card"><div className="panel-header"><div><h2>Pulpity agentów — Mara_OS</h2><p>Każdy agent korzysta z tego samego motywu, menu i komponentów co właściciel.</p></div><span className="pill">Podgląd GUI</span></div><div className="agent-strip">{people.map((p,i)=><button key={p} className={desktopUser===p?"selected":""} onClick={()=>setDesktopUser(p)}><span className={`avatar a${i}`}>{avatars[p]?<img src={avatars[p]} alt=""/>:p[0]}</span>{p}</button>)}</div><div className="agent-desktop-preview"><div className="agent-desktop-top"><strong>Mara_OS / {desktopUser}</strong><span>Sesja nieuruchomiona</span></div><div className="agent-desktop-icons">{["Czat","Terminal","Pliki","Zadania","Real Vision","GitHub"].map(name=><button key={name} onClick={()=>{if(name==="Czat"){setAgent(desktopUser);setSection("chat")}else if(name==="Terminal"){setSection("terminal")}else if(name==="Zadania"){setSection("tasks")}else if(name==="GitHub"||name==="Real Vision"){setSection("integrations")}}}>{name}</button>)}</div><p>To wizualny podgląd wspólnego GUI, nie osobna aktywna sesja zdalna. Docelowo każdy agent otrzyma własną sesję i izolowane środowisko wykonawcze.</p></div></section>}
        {section==="workers"&&<WorkerManager/>}
        {section==="activity"&&<section className="glass-card"><AgentActivity/></section>}
        {section==="tasks"&&<section className="glass-card"><div className="panel-header"><div><h2>Menadżer zadań</h2><p>Lokalna demonstracja listy</p></div><span className="pill">{tasks.filter(t=>!t.done).length} oczekuje</span></div><form className="composer" onSubmit={addTask}><input aria-label="Opis zadania" value={task} onChange={e=>setTask(e.target.value)} placeholder="Dodaj nowe zadanie…"/><button>Dodaj +</button></form><div className="task-list">{tasks.map(t=><div className="task-row" key={t.id}><label><input type="checkbox" checked={t.done} onChange={()=>setTasks(v=>v.map(x=>x.id===t.id?{...x,done:!x.done}:x))}/><span className={t.done?"done":""}>{t.text}</span></label><button onClick={()=>setTasks(v=>v.filter(x=>x.id!==t.id))}>Usuń</button></div>)}</div></section>}
        {section==="studio"&&<section className="studio-layout"><div className="notice">DALL·E 3 — jedyny generator grafiki AI w Mara_OS. Do generowania potrzebny jest działający serwer i token sesji.</div><label className="setting">Token sesji (niezapisany)<input type="password" value={token} onChange={e=>setToken(e.target.value)} autoComplete="off"/></label><Dalle3Studio authToken={token}/></section>}
        {section==="integrations"&&<IntegrationsPanel/>}
        {section==="settings"&&<section className="glass-card settings"><h2>Wygląd Mara_OS</h2><p>Zmiany działają natychmiast w podglądzie.</p><label className="setting">Adres tapety (URL obrazu)<input value={wallpaper} onChange={e=>setWallpaper(e.target.value)} placeholder="https://…/tapeta.jpg"/></label><label className="setting">Przezroczystość paneli: {glass}%<input type="range" min="20" max="95" value={glass} onChange={e=>setGlass(Number(e.target.value))}/></label><label className="toggle"><input type="checkbox" checked={glow} onChange={e=>setGlow(e.target.checked)}/> Fioletowa poświata</label><button onClick={()=>{setGlass(75);setGlow(true);setWallpaper("")}}>Przywróć wygląd</button><p className="hint">Własną tapetę z projektu można docelowo umieścić jako lokalny plik w katalogu public.</p></section>}
      </div>
    </div>
  </div>;
}
createRoot(document.getElementById("root")).render(<App/>);
