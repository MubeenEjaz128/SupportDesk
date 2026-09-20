import React,{useState} from 'react'
import {NavLink,useNavigate} from 'react-router-dom'
import {LayoutDashboard,Ticket,Users,BookOpen,Activity,UserCog,LogOut,Menu,X,Sparkles} from 'lucide-react'
import {useAuth} from '../context/AuthContext'
const nav=[['/','Dashboard',LayoutDashboard],['/tickets','Tickets',Ticket],['/customers','Customers',Users],['/knowledge','Knowledge Base',BookOpen],['/activity','Activity',Activity]]
export default function Layout({children}){
 const {user,logout}=useAuth(); const navg=useNavigate(); const [open,setOpen]=useState(false)
 const doLogout=()=>{logout();navg('/login')}
 const items=user?.role==='agent'?nav:[...nav,['/team','Team',UserCog]]
 return <div className="app-shell">
  <aside className={`sidebar ${open?'sidebar-open':''}`}>
   <div className="brand"><div className="brand-mark"><Sparkles size={20}/></div><div><strong>SupportDesk</strong><span>Support Workspace</span></div><button className="mobile-close" onClick={()=>setOpen(false)}><X/></button></div>
   <nav>{items.map(([to,label,Icon])=><NavLink key={to} to={to} end={to==='/'} onClick={()=>setOpen(false)} className={({isActive})=>isActive?'nav-link active':'nav-link'}><Icon size={19}/><span>{label}</span></NavLink>)}</nav>
   <div className="side-user"><div className="avatar">{(user?.display_name||user?.username||'U').slice(0,1).toUpperCase()}</div><div className="side-user-text"><strong>{user?.display_name||user?.username}</strong><span>{user?.role}</span></div><button className="icon-btn dark" title="Log out" onClick={doLogout}><LogOut size={18}/></button></div>
  </aside>
  <main className="main"><header className="topbar"><button className="mobile-menu" onClick={()=>setOpen(true)}><Menu/></button><div className="top-title">Customer Support Operations</div><div className="top-chip"><span className="online-dot"/>API connected</div></header><div className="content">{children}</div></main>
 </div>
}
