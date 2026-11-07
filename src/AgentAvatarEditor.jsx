import React, { useState } from "react";

/** GUI-only avatar editor. Connect onSave to an authenticated avatar API for agent autonomy. */
export default function AgentAvatarEditor({ agent, initialUrl = "", onSave = () => {} }) {
  const [url, setUrl] = useState(initialUrl);
  const [preview, setPreview] = useState(initialUrl);
  const [error, setError] = useState("");
  function save(e) {
    e.preventDefault();
    const next = url.trim();
    if (next && !/^https:\/\/[^\s]+$/i.test(next)) {
      setError("Podaj poprawny adres HTTPS");
      return;
    }
    setError("");
    setPreview(next);
    onSave(agent, next);
  }
  return <section className="agent-avatar-editor" aria-label={`Awatar agenta ${agent}`}>
    <div className="avatar-preview">{preview ? <img src={preview} alt={`Awatar ${agent}`} referrerPolicy="no-referrer" onError={()=>setError("Nie można załadować zdjęcia")}/> : <span>{agent[0]}</span>}</div>
    <h3>{agent}</h3>
    <form onSubmit={save}>
      <label>Dowolny obraz HTTPS<input value={url} onChange={e=>setUrl(e.target.value)} placeholder="https://example.com/avatar.png" /></label>
      <button type="submit">Zmień zdjęcie</button>
      <button type="button" onClick={()=>{setUrl("");setPreview("");setError("");onSave(agent,"");}}>Przywróć</button>
    </form>
    {error&&<p role="alert">{error}</p>}
  </section>;
}
