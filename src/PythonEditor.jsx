import React, {useState} from "react";

const EXAMPLE = 'import platform\nprint("Mara_OS Python")\nprint(platform.python_version())\n';

/** Browser editor compiles syntax only. Download and run locally for execution. */
export default function PythonEditor({authToken=""}) {
  const [source,setSource]=useState(EXAMPLE);
  const [result,setResult]=useState(null);
  const [busy,setBusy]=useState(false);
  const [error,setError]=useState("");
  async function check() {
    setError("");setResult(null);setBusy(true);
    try {
      if(!authToken) throw new Error("Wprowadź token sesji w zakładce Czat.");
      const response=await fetch("/api/python/compile",{method:"POST",headers:{"Content-Type":"application/json","Authorization":"Bearer "+authToken},body:JSON.stringify({source})});
      if(!response.ok) throw new Error("Błąd API kompilacji (HTTP "+response.status+").");
      setResult(await response.json());
    } catch(err){setError(err.message||"Błąd połączenia");}
    finally{setBusy(false);}
  }
  function download() {
    const url=URL.createObjectURL(new Blob([source],{type:"text/x-python;charset=utf-8"}));
    const a=document.createElement("a");a.href=url;a.download="mara_program.py";a.click();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  return <section className="glass-card" style={{display:"grid",gap:12}}>
    <div className="panel-header"><div><h2>Python Console</h2><p>Edytor Python · kompilacja składni · uruchamianie lokalne</p></div><span className="pill">Python 3</span></div>
    <label htmlFor="mara-python-source">Kod źródłowy</label>
    <textarea id="mara-python-source" spellCheck={false} value={source} onChange={e=>setSource(e.target.value)} rows={16} maxLength={100000} style={{width:"100%",boxSizing:"border-box",fontFamily:"monospace",fontSize:14,tabSize:4,background:"#101827",color:"#e8f2ff",padding:12,borderRadius:10}}/>
    <div style={{display:"flex",gap:8,flexWrap:"wrap"}}>
      <button type="button" disabled={busy||!source.trim()} onClick={check}>{busy?"Sprawdzanie…":"Sprawdź / kompiluj"}</button>
      <button type="button" onClick={download}>Pobierz .py</button>
      <button type="button" onClick={()=>{setSource(EXAMPLE);setResult(null);}}>Przykład</button>
    </div>
    {result&&<div role="status" style={{whiteSpace:"pre-wrap"}}>{result.ok?"✓ Składnia poprawna · instrukcje: "+result.statements:"✕ Błąd w wierszu "+result.line+", kolumna "+result.column+": "+result.error}</div>}
    {error&&<p role="alert">{error}</p>}
    <p style={{fontSize:12,opacity:.8}}>Ten panel nie uruchamia kodu na serwerze. Po pobraniu pliku możesz wykonać go w lokalnym terminalu Mara_OS: <code>python3 -m shell.python_console mara_program.py</code>. Administrator może świadomie użyć <code>sudo</code> dla uprawnień root.</p>
  </section>;
}
