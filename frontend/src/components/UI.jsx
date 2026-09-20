import React from 'react'
export function Badge({children,tone='gray'}){return <span className={`badge badge-${tone}`}>{children}</span>}
export const toneForStatus=s=>({open:'blue',pending:'amber',resolved:'green',closed:'gray'}[s]||'gray')
export const toneForPriority=s=>({low:'gray',medium:'blue',high:'amber',urgent:'red'}[s]||'gray')
export function Loader({label='Loading...'}){return <div className="loader"><span className="spinner"/>{label}</div>}
export function Empty({title='Nothing here yet',text='Create your first record to get started.'}){return <div className="empty"><div className="empty-icon">◎</div><h3>{title}</h3><p>{text}</p></div>}
export function Modal({open,onClose,title,children,wide=false}){if(!open)return null;return <div className="modal-backdrop" onMouseDown={onClose}><div className={`modal ${wide?'modal-wide':''}`} onMouseDown={e=>e.stopPropagation()}><div className="modal-head"><h2>{title}</h2><button className="icon-btn" onClick={onClose}>×</button></div>{children}</div></div>}
export function PageHeader({title,subtitle,action}){return <div className="page-head"><div><h1>{title}</h1>{subtitle&&<p>{subtitle}</p>}</div>{action}</div>}
export function Field({label,children}){return <label className="field"><span>{label}</span>{children}</label>}
