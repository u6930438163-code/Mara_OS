import React, {useEffect,useRef,useState} from "react";

/** User-controlled, local recording. No recording is sent to any server. */
export default function VideoRecorder() {
  const [source,setSource]=useState("screen");
  const [recording,setRecording]=useState(false);
  const [seconds,setSeconds]=useState(0);
  const [error,setError]=useState("");
  const [videoUrl,setVideoUrl]=useState("");
  const [format,setFormat]=useState("");
  const recorder=useRef(null),stream=useRef(null),chunks=useRef([]),timer=useRef(null),url=useRef("");
  const stop=()=>{if(recorder.current?.state==="recording") recorder.current.stop();stream.current?.getTracks().forEach(t=>t.stop());clearInterval(timer.current);};
  useEffect(()=>()=>{stop();if(url.current) URL.revokeObjectURL(url.current);},[]);
  async function start() {
    setError("");
    if (recording) return;
    if (!window.isSecureContext || !navigator.mediaDevices || !window.MediaRecorder) {setError("Nagrywanie wymaga HTTPS lub localhost i obsługiwanej przeglądarki.");return;}
    try {
      const media=source==="screen"
        ? await navigator.mediaDevices.getDisplayMedia({video:true,audio:false})
        : await navigator.mediaDevices.getUserMedia({video:true,audio:false});
      stream.current=media;
      const types=["video/webm;codecs=vp9","video/webm;codecs=vp8","video/webm","video/mp4"];
      const mime=types.find(t=>MediaRecorder.isTypeSupported(t));
      if (!mime) throw new Error("Brak obsługi nagrywania wideo.");
      if (url.current) URL.revokeObjectURL(url.current);
      url.current="";setVideoUrl("");setFormat(mime);
      chunks.current=[];
      const rec=new MediaRecorder(media,{mimeType:mime,videoBitsPerSecond:1800000});
      recorder.current=rec;
      rec.ondataavailable=e=>{if(e.data.size) chunks.current.push(e.data);};
      rec.onstop=()=>{
        if(chunks.current.length){url.current=URL.createObjectURL(new Blob(chunks.current,{type:mime}));setVideoUrl(url.current);}
        setRecording(false);media.getTracks().forEach(t=>t.stop());clearInterval(timer.current);
      };
      rec.onerror=()=>{setError("Wystąpił błąd nagrywania.");stop();};
      media.getVideoTracks()[0]?.addEventListener("ended",stop,{once:true});
      setSeconds(0);rec.start(1000);setRecording(true);
      const began=Date.now();
      timer.current=setInterval(()=>{const elapsed=Math.floor((Date.now()-began)/1000);setSeconds(elapsed);if(elapsed>=60) stop();},500);
    } catch(err){stream.current?.getTracks().forEach(t=>t.stop());setError(err.message||"Nie udało się rozpocząć nagrywania.");}
  }
  return <section className="glass-card">
    <div className="panel-header"><div><h2>Nagraj film</h2><p>Przechwytywanie ekranu lub kamery · lokalnie · maks. 60 sekund</p></div><span className="pill">{recording?"● Nagrywanie":"Gotowy"}</span></div>
    <label>Źródło <select value={source} disabled={recording} onChange={e=>setSource(e.target.value)}><option value="screen">Ekran</option><option value="camera">Kamera</option></select></label>
    <div style={{display:"flex",gap:8,alignItems:"center",flexWrap:"wrap"}}>
      <button type="button" disabled={recording} onClick={start}>● Rozpocznij nagrywanie</button>
      <button type="button" disabled={!recording} onClick={stop}>■ Zatrzymaj</button>
      <strong aria-live="polite">{String(Math.floor(seconds/60)).padStart(2,"0")}:{String(seconds%60).padStart(2,"0")}</strong>
    </div>
    {error&&<p role="alert">{error}</p>}
    {videoUrl&&<div><video src={videoUrl} controls playsInline style={{maxWidth:"100%",maxHeight:320}}/><p><a href={videoUrl} download={"mara-os-nagranie."+ (format.includes("mp4")?"mp4":"webm")}>Pobierz nagranie</a></p></div>}
    <p style={{fontSize:12,opacity:.7}}>Nagrywanie wymaga zgody użytkownika. Wideo pozostaje w przeglądarce i nie jest automatycznie wysyłane do agentów ani na serwer. Dźwięk nie jest nagrywany.</p>
  </section>;
}
