import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import DashboardLayout from './components/DashboardLayout'
import Home from './pages/Home'
import CircularExplorer from './pages/CircularExplorer'
import ComplianceCopilot from './pages/ComplianceCopilot'
import BlockchainTrust from './pages/BlockchainTrust'
import RoleWorkspace from './pages/RoleWorkspace'
import SecurityTrust from './pages/SecurityTrust'

function AnimatedRoutes() {
  const location = useLocation()

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<Home />} />
        <Route path="/circular-explorer" element={<CircularExplorer />} />
        <Route path="/compliance-copilot" element={<ComplianceCopilot />} />
        <Route path="/blockchain-trust" element={<BlockchainTrust />} />
        <Route path="/role-workspace" element={<RoleWorkspace />} />
        <Route path="/security-trust" element={<SecurityTrust />} />
      </Routes>
    </AnimatePresence>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <DashboardLayout>
        <AnimatedRoutes />
      </DashboardLayout>
    </BrowserRouter>
  )
}
