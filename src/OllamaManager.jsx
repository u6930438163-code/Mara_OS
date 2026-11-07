import React, {useState} from "react";

export default function OllamaManager({authToken}) {
  const [data,setData] = useState(null);
  const [busy,setBusy] = useState(false);
  const [error,setError] = useState("");
  async function refresh() {
    if (!authToken) {setError("Podaj token sesji w zakładce Czat.");return;}
    setBusy(true);setError("");
    try {
      const response=await fetch("/api/ollama/status",{headers:{Authorization:"Bearer "+authToken}});
      if(!response.ok) throw new Error("HTTP "+response.status);
      setData(await response.json());
    }catch(err){setError("Nie udało się pobrać statusu: "+err.message);}
    finally{setBusy(false);}
  }
  return <section className="glass-card">
    <div className="panel-header"><div><h2>Menedżer Ollama i modeli</h2><p>Stan rzeczywisty z lokalnego API, bez symulowania danych</p></div><button type="button" disabled={busy} onClick={refresh}>{busy?"Sprawdzanie…":"Odśwież status"}</button></div>
    {error&&<p role="alert">{error}</p>}
    {!data?<p>Wybierz „Odśwież status”, aby pobrać listę modeli i stan serwera.</p>:<>
      <p><strong>Serwer Ollama:</strong> {data.reachable?"Dostępny":"Niedostępny"}</p>
      <h3>Zainstalowane modele ({data.installed_models?.length||0})</h3>
      {(data.installed_models||[]).length?<ul>{data.installed_models.map((m,i)=><li key={m.name||i}>{m.name} — {m.size!=null?(m.size/1073741824).toFixed(2)+" GiB":"rozmiar nieznany"}</li>)}</ul>:<p>Brak danych o modelach.</p>}
      <h3>Modele w pamięci ({data.loaded_models?.length||0})</h3>
      {(data.loaded_models||[]).length?<ul>{data.loaded_models.map((m,i)=><li key={m.name||i}>{m.name} — VRAM: {m.size_vram!=null?(m.size_vram/1073741824).toFixed(2)+" GiB":"brak danych"}; wygaśnięcie: {m.expires_at||"brak danych"}</li>)}</ul>:<p>Żaden model nie jest obecnie raportowany jako załadowany.</p>}
      <h3>Fallback</h3>
      <p>{data.fallback?.provider} — {data.fallback?.model}</p>
      <p>Włączony: {data.fallback?.enabled?"tak":"nie"} · Klucz skonfigurowany: {data.fallback?.configured?"tak":"nie"} · Połączenie zweryfikowane: {data.fallback?.verified?"tak":"nie"}</p>
      {(data.errors||[]).map((message,i)=><p role="alert" key={i}>{message}</p>)}
    </>}
    <p className="hint">Ten panel jest diagnostyczny. Instalowanie i usuwanie modeli oraz sterowanie usługą wymagają osobnych, kontrolowanych operacji backendu.</p>
  </section>;
}
