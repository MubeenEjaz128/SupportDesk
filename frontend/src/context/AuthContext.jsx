import React,{createContext,useContext,useMemo,useState} from 'react'
import {api,clearAuth,loginRequest} from '../lib/api'
const Ctx=createContext(null)
export function AuthProvider({children}){
 const [user,setUser]=useState(()=>{try{return JSON.parse(localStorage.getItem('user'))}catch{return null}})
 const login=async(u,p)=>{const me=await loginRequest(u,p);setUser(me);return me}
 const logout=()=>{clearAuth();setUser(null)}
 const refreshMe=async()=>{const me=await api('/auth/me/');localStorage.setItem('user',JSON.stringify(me));setUser(me);return me}
 const value=useMemo(()=>({user,login,logout,refreshMe}),[user])
 return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}
export const useAuth=()=>useContext(Ctx)
