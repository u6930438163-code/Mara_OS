import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import Dalle3Studio from "../ui/Dalle3Studio.jsx";
import "../ui/dalle3-studio.css";
import "./style.css";

const agents = ["Aria", "Alex", "Astyria", "Aurelius"];
function App() {
  const [page, setPage] = useState("studio");
  const [selected, setSelected] = useState("Aria");
  const [messages, setMessages] = useState([]);
  const [draft, setDraft] = useState("");
  const [jobs, setJobs] = useState([]);
  const [jobDraft, setJobDraft] = useState("");
  const [token, setToken] = useState("");
  const [health, setHealth] = useState("Nie sprawdzono");

  async function checkHealth() {
    try {
      const res = await fetch("/api/health");
      if (!res.ok) throw Error();
      setHealth("API odpowiada");
    } catch { setHealth("API niedostępne"); }
  }
  function send(e) {
    e.preventDefault();
    if (!draft.trim()) return;
    setMessages(m => [...m, { who: "Ty", text: draft.trim(), at: new Date().toLocaleTimeString("pl-PL") }]);
    setDraft("");
  }
  function addJob(e) {
    e.preventDefault();
    if (!jobDraft.trim()) return;
    setJobs(j => [...j, { id: Date.now(), text: jobDraft.trim(), state: "Oczekuje" }]);
    setJobDraft("");
  }
  return <main className="shell">
    <header className="top"><div className="brand"><strong>M</strong><div><h1>Mara_OS</h1><small>Panel rozwojowy · wersja 0.1.0</small></div></div><span className="status">{health}</span></header>
    <nav aria-label="Moduły Mara_OS">
      {[["studio","Grafika AI"],["chat","Czat"],["agents","Agenci"],["jobs","Zadania"],["system","System"]].map(([key,label]) =>
        <button key={key} className={page===key?"active":""} onClick={()=>setPage(key)}>{label}</button>)}
    </nav>
    {page==="studio" && <><p className="hint">Jedyny generator obrazów: DALL·E 3. Wygenerowanie grafiki wymaga aktywnego API i może wiązać się z opłatą.</p>
      <label className="token">Token sesji API (nie jest zapisywany)<input type="password" autoComplete="off" value={token} onChange={e=>setToken(e.target.value)} placeholder="MARA_SESSION_TOKEN"/></label>
      <Dalle3Studio authToken={token}/></>}
    {page==="chat" && <section className="panel"><h2>Czat Mara_OS</h2><p className="hint">Lokalny interfejs demonstracyjny. Wysyłanie do agentów wymaga osobnej integracji.</p>
      <div className="messages" aria-live="polite">{messages.map((m,i)=><article key={i}><b>{m.who}</b><small>{m.at}</small><p>{m.text}</p></article>)}</div>
      <form onSubmit={send} className="compose"><input aria-label="Wiadomość" value={draft} onChange={e=>setDraft(e.target.value)} placeholder="Napisz wiadomość…"/><button>Wyślij</button></form></section>}
    {page==="agents" && <section className="panel"><h2>Agenci AI</h2><p className="hint">Karty konfiguracyjne — nie oznaczają uruchomionych workerów.</p>
      <div className="agents">{agents.map(a=><button className={selected===a?"active":""} key={a} onClick={()=>setSelected(a)}>✦ {a}</button>)}</div>
      <p>Wybrany agent: <strong>{selected}</strong></p><p>Status: niepołączony</p></section>}
    {page==="jobs" && <section className="panel"><h2>Kolejka zadań</h2><p className="hint">Lista lokalna w pamięci przeglądarki. Nie wykonuje poleceń.</p>
      <form onSubmit={addJob} className="compose"><input aria-label="Nowe zadanie" value={jobDraft} onChange={e=>setJobDraft(e.target.value)} placeholder="Opis zadania…"/><button>Dodaj</button></form>
      {jobs.map(j=><div className="job" key={j.id}><span>{j.text} · {j.state}</span><button onClick={()=>setJobs(v=>v.filter(x=>x.id!==j.id))}>Usuń</button></div>)}</section>}
    {page==="system" && <section className="panel"><h2>Diagnostyka API</h2><p>Stan: {health}</p><button onClick={checkHealth}>Sprawdź połączenie</button>
      <p className="hint">Brak dostępu do rzeczywistych procesów systemowych w tym panelu.</p></section>}
  </main>;
}
createRoot(document.getElementById("root")).render(<App/>);
