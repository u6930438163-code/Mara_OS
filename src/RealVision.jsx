import React, {useState, useRef, useEffect} from "react";
import VideoRecorder from "./VideoRecorder.jsx";

/** Compact, user-initiated Real Vision image analysis panel. */
export default function RealVision({authToken=""}) {
  const [image,setImage]=useState("");
  const [question,setQuestion]=useState("Opisz obraz i wskaż ewentualne problemy.");
  const [result,setResult]=useState("");
  const [error,setError]=useState("");
  const [busy,setBusy]=useState(false);
  const [filename,setFilename]=useState("");
  const [captureBusy,setCaptureBusy]=useState(false);
  const [agent,setAgent]=useState("Aria");
  const [history,setHistory]=useState([]);
  const [persist,setPersist]=useState(false);
  const [dispatch,setDispatch]=useState(false);
  const [jobId,setJobId]=useState(null);
  const [jobStatus,setJobStatus]=useState("");
  async function refreshJob() {
    if (!authToken || !jobId) return;
    try {const r=await fetch("/api/worker-jobs",{headers:{"Authorization":"Bearer "+authToken}});
      if (!r.ok) throw new Error("Nie można sprawdzić workera.");
      const data=await r.json();const job=data.jobs.find(j=>j.id===jobId);
      setJobStatus(job?(job.state==="done"?("Zakończono: "+job.result):job.state==="failed"?("Błąd: "+job.result):job.state):"Zadanie nie jest już na liście.");
    } catch(err) {setError(err.message);}
  }
  async function loadHistory() {
    if (!authToken) return;
    try {const response=await fetch("/api/vision/history",{headers:{"Authorization":"Bearer "+authToken}});
      if (!response.ok) throw new Error("Nie można pobrać historii.");
      const data=await response.json();
      setHistory(data.items.map(x=>({id:x.id,agent:x.agent,date:x.created_at,source:x.source,text:x.result})));
    } catch(err) {setError(err.message);}
  }
  async function clearHistory() {
    if (!authToken || !window.confirm("Usunąć całą zapisaną historię Real Vision?")) return;
    try {const response=await fetch("/api/vision/history/clear",{method:"POST",headers:{"Authorization":"Bearer "+authToken,"Content-Type":"application/json"},body:"{}"});
      if (!response.ok) throw new Error("Nie można usunąć historii.");setHistory([]);
    } catch(err) {setError(err.message);}
  }
  const [videoFrames,setVideoFrames]=useState([]);
  const [progress,setProgress]=useState("");
  const captureStream=useRef(null);
  useEffect(()=>()=>{captureStream.current?.getTracks().forEach(track=>track.stop());},[]);
  async function capture(kind) {
    if (captureBusy) return;
    setCaptureBusy(true);setError("");setResult("");setVideoFrames([]);
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
  async function chooseVideo(event) {
    const file=event.target.files?.[0];
    setVideoFrames([]);setError("");setProgress("");
    if (!file) return;
    if (!file.type.startsWith("video/") || file.size>100*1024*1024) {setError("Wideo musi mieć maksymalnie 100 MB.");return;}
    setCaptureBusy(true);
    const url=URL.createObjectURL(file);
    const video=document.createElement("video");video.muted=true;video.preload="auto";video.src=url;
    try {
      await new Promise((resolve,reject)=>{video.onloadedmetadata=resolve;video.onerror=()=>reject(new Error("Nie można odczytać wideo."));});
      if (!Number.isFinite(video.duration)||video.duration<=0) throw new Error("Nieprawidłowy czas wideo.");
      const positions=[0.1,0.5,0.9].map(f=>Math.min(Math.max(0,video.duration*f),Math.max(0,video.duration-0.05)));
      const frames=[];
      for (const time of positions) {
        await new Promise((resolve,reject)=>{video.onseeked=resolve;video.onerror=()=>reject(new Error("Błąd klatki wideo."));video.currentTime=time;});
        const canvas=document.createElement("canvas");const scale=Math.min(1,960/Math.max(video.videoWidth,video.videoHeight));
        canvas.width=Math.max(1,Math.round(video.videoWidth*scale));canvas.height=Math.max(1,Math.round(video.videoHeight*scale));
        canvas.getContext("2d").drawImage(video,0,0,canvas.width,canvas.height);
        const frame=canvas.toDataURL("image/jpeg",0.65);
        if (frame.length>3500000) throw new Error("Klatka jest za duża.");
        frames.push({time:Math.round(time*10)/10,image:frame});
      }
      setVideoFrames(frames);setFilename(file.name);setImage(frames[0].image);
    } catch(err) {setError(err.message||"Nie udało się odczytać wideo.");}
    finally {video.removeAttribute("src");video.load();URL.revokeObjectURL(url);setCaptureBusy(false);}
  }
  async function choose(event) {
    const file=event.target.files?.[0];
    setResult(""); setError(""); setImage(""); setFilename("");setVideoFrames([]);
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
    setBusy(true);setError("");setResult("");setJobId(null);setJobStatus("");
    try {
      const frames=videoFrames.length?videoFrames:[{time:null,image}];
      const reports=[];
      for (let i=0;i<frames.length;i++) {
        setProgress(frames.length>1?`Klatka ${i+1}/${frames.length}`:"Analizowanie obrazu");
        const response=await fetch("/api/ai/vision",{
          method:"POST",
          headers:{"Content-Type":"application/json","Authorization":"Bearer "+authToken},
          body:JSON.stringify({question:question+" Analiza przypisana do agenta "+agent+".",image:frames[i].image,agent,source:videoFrames.length?"video":"image",save_history:persist})
        });
        if (!response.ok) throw new Error("Błąd usługi Vision (HTTP "+response.status+").");
        const data=await response.json();
        reports.push((frames[i].time===null?"Obraz":"Klatka "+frames[i].time+" s")+": "+(data.text||"Brak odpowiedzi"));
      }
      const text=reports.join("\n\n");
      setResult(text);
      if (dispatch) {
        setProgress("Przekazywanie agentowi…");
        const r=await fetch("/api/worker-jobs",{method:"POST",headers:{"Content-Type":"application/json","Authorization":"Bearer "+authToken},body:JSON.stringify({agent,kind:"vision_report",payload:("Przeanalizuj raport Real Vision i zaproponuj dalsze działania. Nie twierdź, że wykonałeś działania w systemie. Pytanie: "+question+"\\n"+text).slice(0,8000)})});
        if (!r.ok) throw new Error("Analiza ukończona, ale nie udało się dodać zadania workera.");
        const job=await r.json();setJobId(job.id);setJobStatus("Zadanie w kolejce");
      }
      setHistory(h=>[{id:Date.now(),agent,date:new Date().toLocaleString("pl-PL"),source:videoFrames.length?"Wideo":filename||"Obraz",text},...h].slice(0,20));
    } catch(err) {setError(err.message || "Nie udało się połączyć z Vision.");}
    finally {setBusy(false);setProgress("");}
  }
  return <div style={{display:"grid",gap:12}}><VideoRecorder/><section className="glass-card" style={{width:"100%",boxSizing:"border-box"}}>
    <div className="panel-header"><div><h2>Real Vision + Ollama</h2><p>Llama 3.2 Vision 11B · analiza na żądanie</p></div><span className="pill">{busy?"Analiza…":"Gotowy do przesłania"}</span></div>
    <div style={{display:"flex",gap:8,flexWrap:"wrap",alignItems:"center"}}>
      <label>Zdjęcie / zrzut ekranu <input type="file" accept="image/png,image/jpeg,image/webp" onChange={choose}/></label>
      <button type="button" disabled={captureBusy||busy} onClick={()=>capture("camera")}>{captureBusy?"Przechwytywanie…":"📷 Kamera"}</button>
      <button type="button" disabled={captureBusy||busy} onClick={()=>capture("screen")}>🖥️ Ekran</button>
      <label>Wideo <input type="file" accept="video/*" disabled={captureBusy||busy} onChange={chooseVideo}/></label>
      <span style={{fontSize:12}}>{filename || "Nie wybrano pliku"}</span>
    </div>
    {image&&<img src={image} alt="Obraz wybrany do analizy" style={{maxWidth:"100%",maxHeight:220,objectFit:"contain",borderRadius:8}}/>}
    <label>Agent <select value={agent} onChange={e=>setAgent(e.target.value)}>{["Aria","Alex","Astyria","Aurelius"].map(a=><option key={a}>{a}</option>)}</select></label>
    <label style={{display:"block"}}>Pytanie do Vision <input style={{width:"100%",boxSizing:"border-box"}} value={question} maxLength={4000} onChange={e=>setQuestion(e.target.value)}/></label>
    <label><input type="checkbox" checked={dispatch} onChange={e=>setDispatch(e.target.checked)}/> Przekaż wynik wybranemu agentowi (worker w tle)</label>
    <label><input type="checkbox" checked={persist} onChange={e=>setPersist(e.target.checked)}/> Zapisuj wyniki na serwerze (bez obrazów)</label>
    {!authToken&&<p role="status">Ustaw token sesji w zakładce Czat, aby wysłać obraz.</p>}
    <button type="button" disabled={!image||!question.trim()||!authToken||busy} onClick={analyze}>{busy?(progress||"Analizowanie…"):"Analizuj obraz"}</button>
    {jobId!==null&&<div role="status">Zadanie #{jobId}: {jobStatus} <button type="button" disabled={!authToken||busy} onClick={refreshJob}>Odśwież status</button></div>}
    {error&&<p role="alert">{error}</p>}
    {result&&<div aria-live="polite" style={{whiteSpace:"pre-wrap",overflowWrap:"anywhere"}}><strong>Wynik analizy</strong><p>{result}</p></div>}
    <div style={{display:"flex",gap:8,flexWrap:"wrap"}}><button type="button" disabled={!authToken||busy} onClick={loadHistory}>Wczytaj historię</button><button type="button" disabled={!authToken||busy} onClick={clearHistory}>Usuń historię serwera</button></div>
    {history.length>0&&<details><summary>Historia analiz ({history.length}) — tylko w bieżącej sesji</summary>{history.map(h=><article key={h.id} style={{padding:8,borderBottom:"1px solid #7775"}}><strong>{h.agent} · {h.date} · {h.source}</strong><p style={{whiteSpace:"pre-wrap"}}>{h.text}</p></article>)}</details>}
    <p style={{fontSize:12,opacity:.7}}>Przechwytywana jest pojedyncza klatka po udzieleniu zgody przeglądarce. Strumień kamery lub ekranu jest następnie zatrzymywany. Wysyłanie do modelu następuje dopiero po kliknięciu Analizuj; Wideo jest analizowane jako trzy klatki (10%, 50%, 90% czasu), nie jako strumień na żywo. Historia może być opcjonalnie zapisana w lokalnej bazie serwera (bez obrazów). Wybór agenta określa odbiorcę raportu; po zaznaczeniu opcji worker dostaje wyłącznie tekst analizy. Worker musi być osobno uruchomiony, aby wykonać zadanie.</p>
  </section></div>;
}