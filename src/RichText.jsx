import React from "react";
import "./RichText.css";

const keywords = /\b(curl|sudo|apt|systemctl|journalctl|git|python3?|npm|node|docker|podman|ssh|GET|POST|PUT|DELETE|SELECT|FROM|WHERE|const|let|function|return|import|export|async|await|if|else|true|false|null)\b/g;
function Highlight({value}) {
  return <>{String(value).split(keywords).map((part,i)=>keywords.test(part)?<span className="rt-keyword" key={i}>{part}</span>:<React.Fragment key={i}>{part}</React.Fragment>)}</>;
}
function Inline({value}) {
  const parts=String(value).split(/(\*\*[^*\n]+\*\*|\*[^*\n]+\*|`[^`\n]+`|https?:\/\/[^\s<>]+)/g);
  return <>{parts.map((p,i)=>{
    if(p.startsWith("**")&&p.endsWith("**"))return <strong key={i}>{p.slice(2,-2)}</strong>;
    if(p.startsWith("*")&&p.endsWith("*"))return <em key={i}>{p.slice(1,-1)}</em>;
    if(p.startsWith("`")&&p.endsWith("`"))return <code key={i}><Highlight value={p.slice(1,-1)}/></code>;
    if(/^https?:\/\//.test(p)){try{const u=new URL(p);if(["http:","https:"].includes(u.protocol))return <a key={i} href={u.href} target="_blank" rel="noopener noreferrer">{p}</a>}catch{}}
    return <React.Fragment key={i}>{p}</React.Fragment>;
  })}</>;
}
function Code({language,code}) {
  return <div className="rt-code"><div className="rt-code-header"><span>{language||"tekst"}</span><button type="button" onClick={()=>navigator.clipboard?.writeText(code)} aria-label="Kopiuj kod">Kopiuj</button></div><pre><code><Highlight value={code}/></code></pre></div>;
}
export default function RichText({text=""}) {
  const blocks=String(text).split(/(```[^\n]*\n[\s\S]*?```)/g);
  return <div className="rt-content">{blocks.map((block,i)=>{
    if(block.startsWith("```")&&block.endsWith("```")){const split=block.indexOf("\n");return <Code key={i} language={block.slice(3,split).trim()} code={block.slice(split+1,-3).replace(/\n$/,"")}/>;}
    return block.split("\n").map((line,j)=>{
      const key=i+"-"+j;
      if(/^#{1,3}\s/.test(line)){const n=line.match(/^#+/)[0].length;return <div key={key} className={"rt-heading rt-h"+n}><Inline value={line.replace(/^#{1,3}\s/,"")}/></div>}
      if(/^\s*[-*]\s/.test(line))return <div key={key} className="rt-list">• <Inline value={line.replace(/^\s*[-*]\s/,"")}/></div>;
      if(/^\s*\d+\.\s/.test(line))return <div key={key} className="rt-list"><Inline value={line}/></div>;
      return <div key={key} className="rt-line"><Inline value={line}/></div>;
    });
  })}</div>;
}
