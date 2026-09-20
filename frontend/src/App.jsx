import React from 'react'
import {Navigate,Route,Routes} from 'react-router-dom'
import {useAuth} from './context/AuthContext'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Tickets from './pages/Tickets'
import TicketDetail from './pages/TicketDetail'
import Customers from './pages/Customers'
import Knowledge from './pages/Knowledge'
import ActivityPage from './pages/ActivityPage'
import Team from './pages/Team'
function Guard({children}){const {user}=useAuth();return user?children:<Navigate to="/login" replace/>}
function Shell({children}){return <Guard><Layout>{children}</Layout></Guard>}
export default function App(){return <Routes>
 <Route path="/login" element={<Login/>}/>
 <Route path="/" element={<Shell><Dashboard/></Shell>}/>
 <Route path="/tickets" element={<Shell><Tickets/></Shell>}/>
 <Route path="/tickets/:id" element={<Shell><TicketDetail/></Shell>}/>
 <Route path="/customers" element={<Shell><Customers/></Shell>}/>
 <Route path="/knowledge" element={<Shell><Knowledge/></Shell>}/>
 <Route path="/activity" element={<Shell><ActivityPage/></Shell>}/>
 <Route path="/team" element={<Shell><Team/></Shell>}/>
 <Route path="*" element={<Navigate to="/" replace/>}/>
 </Routes>}
