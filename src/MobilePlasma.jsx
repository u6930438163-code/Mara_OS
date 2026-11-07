import React, {useState} from "react";
import "./mobile-plasma.css";

const apps = [
  {id:"chat",name:"Czat AI",icon:"💬"},
  {id:"terminal",name:"Konsole",icon:"⌨️"},
  {id:"agents",name:"Agenci",icon:"🤖"},
  {id:"desktops",name:"Pulpity AI",icon:"🖥️"},
  {id:"tasks",name:"Zadania",icon:"📋"},
  {id:"studio",name:"DALL·E 3",icon:"🎨"},
  {id:"integrations",name:"Integracje",icon:"🔌"},
  {id:"settings",name:"Ustawienia",icon:"⚙️"}
];
export default function MobilePlasma({onOpen,wallpaper,avatars={}}) {
  const [launcher,setLauncher]=useState(false);
  const [search,setSearch]=useState("");
  const [clock,setClock]=useState(()=>new Date().toLocaleTimeString("pl-PL",{hour:"2-digit",minute:"2-digit"}));
  const [active,setActive]=useState(null);
  const [minimized,setMinimized]=useState(false);
  const matches=apps.filter(a=>a.name.toLowerCase().includes(search.toLowerCase()));
  function open(id) {setActive(id);setMinimized(false);setLauncher(false);}
  function go(id) {onOpen(id);setLauncher(false);}
  return <section className="plasma-shell" aria-label="Mara_OS Mobile Plasma — prototyp powłoki">
    <div className="plasma-wall" style={wallpaper?{backgroundImage:`linear-gradient(145deg,#100b2caa,#290a48aa),url("${wallpaper.replace(/["\\]/g,"")}")`}:undefined}>
      <div className="plasma-status"><strong>Mara_OS</strong><span>Plasma UI · demonstracja</span></div>
      <div className="plasma-icons">{apps.slice(0,6).map(a=><button key={a.id} onClick={()=>open(a.id)}><span aria-hidden="true">{a.icon}</span>{a.name}</button>)}</div>
      {active&&!minimized&&<div className="plasma-window" role="dialog" aria-label={apps.find(a=>a.id===active)?.name}>
        <div className="plasma-titlebar"><strong>{apps.find(a=>a.id===active)?.icon} {apps.find(a=>a.id===active)?.name}</strong><div><button onClick={()=>setMinimized(true)} aria-label="Minimalizuj">−</button><button onClick={()=>setActive(null)} aria-label="Zamknij">×</button></div></div>
        <div className="plasma-window-body"><p>Moduł Mara_OS jest dostępny w panelu głównym. To powłoka interfejsu, nie natywna sesja KDE.</p><button onClick={()=>go(active)}>Otwórz moduł</button></div>
      </div>}
      {launcher&&<div className="plasma-launcher"><label>Menu aplikacji<input autoFocus placeholder="Szukaj aplikacji…" value={search} onChange={e=>setSearch(e.target.value)}/></label><div>{matches.map(a=><button key={a.id} onClick={()=>open(a.id)}>{a.icon} {a.name}</button>)}</div></div>}
      <div className="plasma-panel"><button aria-label="Menu aplikacji" aria-expanded={launcher} onClick={()=>setLauncher(v=>!v)}>◈</button><button aria-label="Czat AI" onClick={()=>go("chat")}>💬</button><button aria-label="Terminal" onClick={()=>go("terminal")}>⌨️</button><button aria-label="Pulpity AI" onClick={()=>go("desktops")}>🖥️</button>{active&&<button aria-label="Przywróć okno" onClick={()=>setMinimized(false)}>▣</button>}<span className="plasma-clock" onClick={()=>setClock(new Date().toLocaleTimeString("pl-PL",{hour:"2-digit",minute:"2-digit"}))}>{clock}</span></div>
    </div>
    <p className="plasma-disclaimer">Interaktywny prototyp mobilnej powłoki. Prawdziwe KDE Plasma 6 (KWin, Qt, Dolphin, Konsole) wymaga zgodnego środowiska Linux; Google AI Studio nie uruchamia go natywnie.</p>
  </section>;
}
