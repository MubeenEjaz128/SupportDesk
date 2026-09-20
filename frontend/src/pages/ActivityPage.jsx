import React,{useEffect,useState} from 'react'
import {Activity as ActivityIcon} from 'lucide-react'
import {api} from '../lib/api'
import {Empty,Loader,PageHeader} from '../components/UI'
export default function ActivityPage(){const [items,setItems]=useState(null),[err,setErr]=useState('');useEffect(()=>{api('/activity/').then(setItems).catch(e=>setErr(e.message))},[]);return <><PageHeader title="Activity" subtitle="Audit trail of important support actions."/>{err&&<div className="error-box">{err}</div>}{!items?<Loader/>:items.length===0?<Empty title="No activity yet"/>:<section className="panel"><div className="timeline">{items.map(a=><div className="timeline-item" key={a.id}><div className="timeline-icon"><ActivityIcon size={15}/></div><div><strong>{a.summary}</strong><p>{a.actor||'System'} · <span>{a.action}</span></p><small>{new Date(a.created_at).toLocaleString()}</small></div></div>)}</div></section>}</>}
