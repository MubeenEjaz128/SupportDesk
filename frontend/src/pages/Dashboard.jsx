import React,{useEffect,useState} from 'react'
import {Ticket,Clock3,CheckCircle2,Users,Inbox,ArrowUpRight} from 'lucide-react'
import {Link} from 'react-router-dom'
import {api} from '../lib/api'
import {Badge,Loader,PageHeader,toneForPriority,toneForStatus} from '../components/UI'
export default function Dashboard(){
 const [d,setD]=useState(null); const [err,setErr]=useState('')
 useEffect(()=>{api('/dashboard/stats/').then(setD).catch(e=>setErr(e.message))},[])
 if(!d&&!err)return <Loader label="Loading support metrics..."/>
 if(err)return <div className="error-box">{err}</div>
 const cards=[['Total tickets',d.total_tickets,Ticket],['Open',d.open_tickets,Inbox],['Pending',d.pending_tickets,Clock3],['Resolved',d.resolved_tickets,CheckCircle2],['Customers',d.customers,Users]]
 const max=Math.max(1,...Object.values(d.by_priority||{}))
 return <><PageHeader title="Dashboard" subtitle="A live snapshot of customer support operations."/><div className="stat-grid">{cards.map(([l,v,I])=><div className="stat-card" key={l}><div className="stat-icon"><I size={20}/></div><div><span>{l}</span><strong>{v}</strong></div></div>)}</div><div className="dashboard-grid"><section className="panel"><div className="panel-head"><div><h2>Ticket priority</h2><p>Current workload distribution</p></div></div><div className="bars">{Object.entries(d.by_priority||{}).map(([k,v])=><div className="bar-row" key={k}><span className="bar-label">{k}</span><div className="bar-track"><div className={`bar-fill bar-${toneForPriority(k)}`} style={{width:`${Math.max(4,v/max*100)}%`}}/></div><strong>{v}</strong></div>)}</div><div className="mini-kpi"><span>Assigned to you and active</span><strong>{d.my_open_tickets}</strong></div></section><section className="panel span-2"><div className="panel-head"><div><h2>Recent tickets</h2><p>Most recently updated conversations</p></div><Link className="text-link" to="/tickets">View all <ArrowUpRight size={15}/></Link></div><div className="table-wrap"><table><thead><tr><th>Ticket</th><th>Customer</th><th>Status</th><th>Priority</th><th>Updated</th></tr></thead><tbody>{d.recent_tickets.map(t=><tr key={t.id}><td><Link className="ticket-link" to={`/tickets/${t.id}`}><strong>{t.ticket_number}</strong><span>{t.subject}</span></Link></td><td>{t.customer?.name}</td><td><Badge tone={toneForStatus(t.status)}>{t.status}</Badge></td><td><Badge tone={toneForPriority(t.priority)}>{t.priority}</Badge></td><td>{new Date(t.updated_at).toLocaleString()}</td></tr>)}</tbody></table></div></section></div></>
}
