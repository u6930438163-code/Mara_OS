import React, {useState} from "react";

const agents=["Aria","Alex","Astyria","Aurelius"];
export default function IntegrationsPanel() {
  const [token,setToken]=useState("");
  const [agent,setAgent]=useState("Aria");
  const [message,setMessage]=useState("");
  const [reply,setReply]=useState("");
  const [question,setQuestion]=useState("Co widać na tym zrzucie ekranu? Wskaż błędy GUI.");
  const [image,setImage]=useState("");
  const [repo,setRepo]=useState("u6930438163-code/Mara_OS");
  const [repoResult,setRepoResult]=useState(null);
  const [busy,setBusy]=useState("");
  const [error,setError]=useState("");
  const auth={Authorization:"Bearer "+token};
  async function call(url,payload,kind) {
    setError("");setBusy(kind);
    try {
      const res=await fetch(url,{method:"POST",headers:{"Content-Type":"application/json",...auth},body:JSON.stringify(payload)});
      const data=await res.json();
      if(!res.ok) throw Error(data.error||"Błąd serwera");
      setReply(data.text||JSON.stringify(data));
    }catch(e){setError(e.message)}finally{setBusy("")}
  }
  function loadImage(e){
    const file=e.target.files?.[0];
    if(!file)return;
    if(!["image/png","image/jpeg","image/webp"].includes(file.type)||file.size>2500000){setError("Wybierz JPG, PNG lub WEBP do 2,5 MB.");return}
    const reader=new FileReader();
    reader.onload=()=>setImage(String(reader.result));
    reader.readAsDataURL(file);
  }
  async function checkRepo(){
    setBusy("github");setError("");
    try{
      const res=await fetch("/api/github/repo?name="+encodeURIComponent(repo),{headers:auth});
      const data=await res.json();
      if(!res.ok)throw Error(data.error||"Błąd GitHub");
      setRepoResult(data);
    }catch(e){setError(e.message)}finally{setBusy("")}
  }
  return <section className="glass-card integrations">
    <h2>Integracje AI i GitHub</h2>
    <p className="hint">Połączenia rzeczywiste, gdy serwer działa i ma skonfigurowane klucze. Żadne konto nie jest podłączane automatycznie.</p>
    <label className="setting">Token sesji Mara_OS<input type="password" autoComplete="off" value={token} onChange={e=>setToken(e.target.value)} placeholder="Token z konfiguracji serwera"/></label>
    <div className="integration-grid">
      <div className="integration-card"><h3>AI · czterej agenci</h3>
        <label className="setting">Agent<select value={agent} onChange={e=>setAgent(e.target.value)}>{agents.map(a=><option key={a}>{a}</option>)}</select></label>
        <textarea aria-label="Wiadomość do agenta" value={message} onChange={e=>setMessage(e.target.value)} placeholder="Napisz do agenta…"/>
        <button disabled={!token||!message.trim()||!!busy} onClick={()=>call("/api/ai/chat",{agent,message},"chat")}>{busy==="chat"?"Odpowiadanie…":"Wyślij do AI"}</button>
      </div>
      <div className="integration-card"><h3>Real Vision</h3><p>Analiza zrzutów ekranu i zdjęć przez OpenAI.</p>
        <input aria-label="Wybierz obraz" type="file" accept="image/png,image/jpeg,image/webp" onChange={loadImage}/>
        <textarea aria-label="Pytanie o obraz" value={question} onChange={e=>setQuestion(e.target.value)}/>
        <button disabled={!token||!image||!question.trim()||!!busy} onClick={()=>call("/api/ai/vision",{question,image},"vision")}>{busy==="vision"?"Analizowanie…":"Analizuj obraz"}</button>
      </div>
      <div className="integration-card"><h3>GitHub</h3><p>Odczyt metadanych repozytorium. Bez zapisu i zmian kodu.</p>
        <label className="setting">Repozytorium<input value={repo} onChange={e=>setRepo(e.target.value)}/></label>
        <button disabled={!token||!repo.trim()||!!busy} onClick={checkRepo}>{busy==="github"?"Sprawdzanie…":"Sprawdź repozytorium"}</button>
        {repoResult&&<pre className="result">{JSON.stringify(repoResult,null,2)}</pre>}
      </div>
    </div>
    {error&&<p role="alert" className="integration-error">{error}</p>}
    {reply&&<div className="integration-reply"><h3>Odpowiedź AI</h3><p>{reply}</p></div>}
  </section>;
}
