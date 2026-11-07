import {useEffect,useRef,useState} from "react";

/** Cursor-based near-real-time sync; replays missed events after reconnect. */
export default function useGlobalSync(authToken,onEvents) {
  const [status,setStatus]=useState("offline");
  const [lastEvent,setLastEvent]=useState(0);
  const cursor=useRef(0);
  const callback=useRef(onEvents);
  useEffect(()=>{callback.current=onEvents;},[onEvents]);
  useEffect(()=>{
    if(!authToken){setStatus("offline");return;}
    let closed=false,controller=null,timer=null,failures=0;
    async function poll(){
      if(closed)return;
      controller=new AbortController();
      try {
        const r=await fetch("/api/sync/events?since="+cursor.current,{headers:{Authorization:"Bearer "+authToken},cache:"no-store",signal:controller.signal});
        if(!r.ok)throw new Error("HTTP "+r.status);
        const data=await r.json();
        const events=Array.isArray(data.events)?data.events:[];
        if(closed)return;
        if(events.length){
          callback.current?.(events);
          cursor.current=events[events.length-1].id;
          setLastEvent(cursor.current);
        }
        failures=0;setStatus("online");
        timer=setTimeout(poll,events.length>=100?0:1500);
      }catch(e){
        if(closed)return;
        failures+=1;setStatus("reconnecting");
        timer=setTimeout(poll,Math.min(15000,1000*2**Math.min(failures,4)));
      }
    }
    poll();
    return ()=>{closed=true;clearTimeout(timer);controller?.abort();};
  },[authToken]);
  return {status,lastEvent};
}
