import React, {useState, useRef, useEffect} from "react";

/** Compact, user-initiated Real Vision image analysis panel. */
export default function RealVision({authToken=""}) {
  const [image,setImage]=useState("");
  const [question,setQuestion]=useState("Opisz obraz i wskaż ewentualne problemy.");
  const [result,setResult]=useState("");
  const [error,setError]=useState("");
  const [busy,setBusy]=useState(false);
  const [filename,setFilename]=useState("");
  const [captureBusy,setCaptureBusy]=useState(false);
  const captureStream=useRef(null);
  useEffect(()=>()=>{captureStream.current?.getTracks().forEach(track=>track.stop());},[]);
  async function capture(kind) {
    if (captureBusy) return;
    setCaptureBusy(true);setError("");setResult("");
    let stream;
    try {
      if (!window.isSecureContext) throw new Error("Kamera i ekran wymagają HTTPS lub localhost.");
      if (!navigator.mediaDevices) throw new Error("Przeglądarka nie obsługuje przechwytywania obrazu.");
      if (kind==="screen" && !navigator.mediaDevices.getDisplayMedia) throw new Error("Udostępnianie ekranu jest niedostępne.");
      stream=kind==="screen"
        ? await navigator.mediaDevices.getDisplayMedia({video:true,audio:false})
        : await navigator.mediaDevices.getUserMedia({video:true,audio:false});
      captureStream.current=stream;
      const video=document.createElement("video");
      video.muted=true;video.playsInline=true;video.srcObject=stream;
      await new Promise((resolve,reject)=>{
        const timeout=setTimeout(()=>reject(new Error("Przekroczono czas oczekiwania na obraz.")),10000);
        video.onloadedmetadata=()=>{clearTimeout(timeout);resolve();};
        video.onerror=()=>{clearTimeout(timeout);reject(new Error("Nie udało się odczytać obrazu."));};
      });
      await video.play();
      const w=video.videoWidth,h=video.videoHeight;
      if (!w||!h) throw new Error("Źródło nie zwróciło obrazu.");
      const scale=Math.min(1,1280/Math.max(w,h));
      const canvas=document.createElement("canvas");
      canvas.width=Math.round(w*scale);canvas.height=Math.round(h*scale);
      canvas.getContext("2d").drawImage(video,0,0,canvas.width,canvas.height);
      const frame=canvas.toDataURL("image/jpeg",0.78);
      if (frame.length>3500000) throw new Error("Klatka jest zbyt duża.");
      setImage(frame);setFilename(kind==="screen"?"Zrzut ekranu":"Klatka kamery");
      video.pause();video.srcObject=null;
    } catch(err) {setError(err.message || "Nie udało się przechwycić obrazu.");}
    finally {stream?.getTracks().forEach(track=>track.stop());captureStream.current=null;setCaptureBusy(false);}
  }
  async function choose(event) {
    const file=event.target.files?.[0];
    setResult(""); setError(""); setImage(""); setFilename("");
    if (!file) return;
    if (!["image/png","image/jpeg","image/webp"].includes(file.type) || file.size > 2700000) {
      setError("Wybierz PNG, JPEG lub WEBP do 2,7 MB."); return;
    }
    const reader=new FileReader();
    reader.onload=()=>{setImage(String(reader.result));setFilename(file.name);};
    reader.onerror=()=>setError("Nie udało się odczytać pliku.");
    reader.readAsDataURL(file);
  }
  async function analyze() {
    if (!image || !authToken || busy) return;
    setBusy(true);setError("");setResult("");
    try {
      const response=await fetch("/api/ai/vision",{
        method:"POST",
        headers:{"Content-Type":"application/json","Authorization":"Bearer "+authToken},
        body:JSON.stringify({question,image})
      });
      if (!response.ok) throw new Error("Błąd usługi Vision (HTTP "+response.status+").");
      const data=await response.json();
      setResult(data.text || "Model nie zwrócił opisu.");
    } catch(err) {setError(err.message || "Nie udało się połączyć z Vision.");}
    finally {setBusy(false);}
  }
  return <section className="glass-card" style={{width:"100%",boxSizing:"border-box"}}>
    <div className="panel-header"><div><h2>Real Vision + Ollama</h2><p>Llama 3.2 Vision 11B · analiza na żądanie</p></div><span className="pill">{busy?"Analiza…":"Gotowy do przesłania"}</span></div>
    <div style={{display:"flex",gap:8,flexWrap:"wrap",alignItems:"center"}}>
      <label>Zdjęcie / zrzut ekranu <input type="file" accept="image/png,image/jpeg,image/webp" onChange={choose}/></label>
      <button type="button" disabled={captureBusy||busy} onClick={()=>capture("camera")}>{captureBusy?"Przechwytywanie…":"📷 Kamera"}</button>
      <button type="button" disabled={captureBusy||busy} onClick={()=>capture("screen")}>🖥️ Ekran</button>
      <span style={{fontSize:12}}>{filename || "Nie wybrano pliku"}</span>
    </div>
    {image&&<img src={image} alt="Obraz wybrany do analizy" style={{maxWidth:"100%",maxHeight:220,objectFit:"contain",borderRadius:8}}/>}
    <label style={{display:"block"}}>Pytanie do Vision <input style={{width:"100%",boxSizing:"border-box"}} value={question} maxLength={4000} onChange={e=>setQuestion(e.target.value)}/></label>
    {!authToken&&<p role="status">Ustaw token sesji w zakładce Czat, aby wysłać obraz.</p>}
    <button type="button" disabled={!image||!question.trim()||!authToken||busy} onClick={analyze}>{busy?"Analizowanie…":"Analizuj obraz"}</button>
    {error&&<p role="alert">{error}</p>}
    {result&&<div aria-live="polite" style={{whiteSpace:"pre-wrap",overflowWrap:"anywhere"}}><strong>Wynik analizy</strong><p>{result}</p></div>}
    <p style={{fontSize:12,opacity:.7}}>Przechwytywana jest pojedyncza klatka po udzieleniu zgody przeglądarce. Strumień kamery lub ekranu jest następnie zatrzymywany. Wysyłanie do modelu następuje dopiero po kliknięciu Analizuj; ciągłe wideo nie jest jeszcze obsługiwane.</p>
  </section>;
}
