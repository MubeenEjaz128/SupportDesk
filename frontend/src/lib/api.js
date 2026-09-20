const BASE=(import.meta.env.VITE_API_URL || 'http://localhost:8000/api').replace(/\/$/,'')
export const API_BASE=BASE
const getToken=()=>localStorage.getItem('access')
const saveTokens=(access,refresh)=>{ if(access)localStorage.setItem('access',access); if(refresh)localStorage.setItem('refresh',refresh) }
async function refreshAccess(){
  const refresh=localStorage.getItem('refresh'); if(!refresh) return false
  const r=await fetch(`${BASE}/auth/token/refresh/`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({refresh})})
  if(!r.ok) return false
  const data=await r.json(); saveTokens(data.access,data.refresh); return true
}
export async function api(path,options={},retry=true){
  const headers={...(options.body instanceof FormData?{}:{'Content-Type':'application/json'}),...(options.headers||{})}
  const token=getToken(); if(token) headers.Authorization=`Bearer ${token}`
  const r=await fetch(`${BASE}${path.startsWith('/')?path:`/${path}`}`,{...options,headers})
  if(r.status===401 && retry && await refreshAccess()) return api(path,options,false)
  let data=null; try{ data=await r.json() }catch{ data=null }
  if(!r.ok){ const msg=data?.detail || Object.values(data||{}).flat().join(' ') || `Request failed (${r.status})`; throw new Error(msg) }
  return data
}
export async function loginRequest(username,password){
  const r=await fetch(`${BASE}/auth/token/`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username,password})})
  const data=await r.json(); if(!r.ok) throw new Error(data.detail||'Invalid username or password')
  saveTokens(data.access,data.refresh); localStorage.setItem('user',JSON.stringify(data.user)); return data.user
}
export function clearAuth(){ localStorage.removeItem('access'); localStorage.removeItem('refresh'); localStorage.removeItem('user') }
