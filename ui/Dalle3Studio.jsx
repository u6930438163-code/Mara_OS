import React, { useState } from "react";
import "./dalle3-studio.css";

/**
 * Mara_OS Violet Blade image studio.
 * The backend must expose an authenticated POST /api/images/generate route
 * that invokes services/dalle3.py, with server-side rate limiting.
 */
export default function Dalle3Studio({ endpoint = "/api/images/generate", authToken = "" }) {
  const [prompt, setPrompt] = useState("");
  const [size, setSize] = useState("1024x1024");
  const [quality, setQuality] = useState("hd");
  const [style, setStyle] = useState("vivid");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  async function generate(event) {
    event.preventDefault();
    if (!prompt.trim() || busy) return;
    setBusy(true);
    setError("");
    setResult(null);
    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${authToken}` },
        credentials: "same-origin",
        body: JSON.stringify({ prompt, size, quality, style })
      });
      if (!response.ok) throw new Error(`Generowanie nie powiodło się (HTTP ${response.status})`);
      const data = await response.json();
      if (!data.url) throw new Error("Serwer nie zwrócił adresu obrazu");
      setResult(data);
    } catch (err) {
      setError(err.message || "Nieznany błąd");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="mara-studio" aria-label="Studio grafiki DALL·E 3">
      <header><h2>Mara_OS · DALL·E 3</h2><span>Violet Blade</span></header>
      <form onSubmit={generate}>
        <label htmlFor="mara-prompt">Opisz grafikę</label>
        <textarea id="mara-prompt" value={prompt} maxLength={4000}
          onChange={event => setPrompt(event.target.value)}
          placeholder="Np. awatar Arii w stylu Violet Blade…" rows={4} required />
        <div className="mara-fields">
          <label>Rozmiar
            <select value={size} onChange={event => setSize(event.target.value)}>
              <option value="1024x1024">Kwadrat</option>
              <option value="1024x1792">Pionowy</option>
              <option value="1792x1024">Panoramiczny</option>
            </select>
          </label>
          <label>Jakość
            <select value={quality} onChange={event => setQuality(event.target.value)}>
              <option value="hd">HD</option><option value="standard">Standard</option>
            </select>
          </label>
          <label>Styl
            <select value={style} onChange={event => setStyle(event.target.value)}>
              <option value="vivid">Wyrazisty</option><option value="natural">Naturalny</option>
            </select>
          </label>
        </div>
        <button type="submit" disabled={busy || !prompt.trim()}>
          {busy ? "Generowanie…" : "Generuj przez DALL·E 3"}
        </button>
      </form>
      {error && <p role="alert" className="mara-error">{error}</p>}
      {result?.url && <figure>
        <img src={result.url} alt={result.revised_prompt || prompt} />
        <figcaption>Wynik DALL·E 3 · adres obrazu może wygasnąć</figcaption>
      </figure>}
    </section>
  );
}
