import React, { useState } from "react";
const templates = [
  ["Awatar Aria", "Portret futurystycznej agentki AI Aria, elegancki styl sci-fi, neonowy fiolet, realistyczne światło, kwadratowy awatar."],
  ["Awatar Alex", "Portret futurystycznego agenta AI Alex, nowoczesny styl technologiczny, fioletowe i grafitowe akcenty, kwadratowy awatar."],
  ["Awatar Astyria", "Portret futurystycznej agentki AI Astyria, subtelne świetlne detale, elegancki styl cyberpunk, kwadratowy awatar."],
  ["Awatar Aurelius", "Portret futurystycznego agenta AI Aurelius, grafitowa zbroja technologiczna, fioletowe oświetlenie, kwadratowy awatar."],
  ["Tapeta", "Filmowa tapeta pulpitu Mara_OS, ciemny grafit, neonowy fiolet, elegancka futurystyczna sceneria, bez napisów i ikon."],
  ["Ikony GUI", "Spójny zestaw ikon interfejsu Mara_OS, minimalistyczny futurystyczny styl, fiolet i srebro, ciemne tło, bez tekstu."],
  ["Panel GUI", "Koncepcja graficzna półprzezroczystego panelu Mara_OS, szkło, delikatny fioletowy neon, nowoczesny design, bez tekstu."]
];
export default function ChatDallePrompts({ authToken = "", onImage = () => {} }) {
  const [prompt, setPrompt] = useState(templates[0][1]);
  const [size, setSize] = useState("1024x1024");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  async function generate() {
    if (!prompt.trim() || busy) return;
    setBusy(true); setError("");
    try {
      const res = await fetch("/api/images/generate", {
        method: "POST", credentials: "same-origin",
        headers: {"Content-Type":"application/json","Authorization":`Bearer ${authToken}`},
        body: JSON.stringify({prompt:prompt.trim(),size,quality:"hd",style:"vivid"})
      });
      if (!res.ok) throw new Error(`Błąd API (HTTP ${res.status})`);
      const data = await res.json();
      if (!data.url) throw new Error("Brak obrazu w odpowiedzi");
      onImage({who:"DALL·E 3",to:"Czat",text:prompt.trim(),image:data.url,time:new Date().toLocaleTimeString("pl-PL")});
    } catch (e) { setError(e.message || "Generowanie nie powiodło się"); }
    finally { setBusy(false); }
  }
  return <div className="chat-dalle">
    <div className="chat-dalle-title"><strong>✦ Prompty DALL·E 3</strong><small>Generowanie obrazu przez OpenAI API może być płatne</small></div>
    <div className="prompt-chips">{templates.map(([label,value])=><button key={label} type="button" onClick={()=>setPrompt(value)}>{label}</button>)}</div>
    <textarea aria-label="Prompt DALL·E 3" rows={2} maxLength={4000} value={prompt} onChange={e=>setPrompt(e.target.value)}/>
    <div className="prompt-actions"><select aria-label="Rozmiar obrazu" value={size} onChange={e=>setSize(e.target.value)}><option value="1024x1024">Kwadrat</option><option value="1024x1792">Pionowy</option><option value="1792x1024">Panorama</option></select><button disabled={busy || !prompt.trim() || !authToken} onClick={generate}>{busy?"Generowanie…":"Generuj obraz ✦"}</button></div>
    {!authToken&&<small>Wpisz token sesji w zakładce DALL·E 3.</small>}
    {error&&<p role="alert">{error}</p>}
  </div>;
}
