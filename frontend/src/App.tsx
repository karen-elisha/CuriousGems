import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './pages/Dashboard';
import { DigitalTwinExplorer } from './pages/DigitalTwinExplorer';
import { SimulationLab } from './pages/SimulationLab';
import { EvidenceGraph } from './pages/EvidenceGraph';
import { AIInvestigation } from './pages/AIInvestigation';
import { Reports } from './pages/Reports';
import { Transactions } from './pages/Transactions';
import { Policies } from './pages/Policies';
import { Setup } from './pages/Setup';
import apiClient from './api/client';
import { Loader2 } from 'lucide-react';

function MainLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 p-8 ml-64 overflow-y-auto">
        <div className="max-w-7xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
}

export default function App() {
  const [initialized, setInitialized] = useState<boolean | null>(null);

  useEffect(() => {
    apiClient.get('/health').then(res => {
      setInitialized(res.data.initialized);
    }).catch(() => setInitialized(false));
  }, []);

  if (initialized === null) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="w-10 h-10 text-primary animate-spin" />
      </div>
    );
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/setup" element={initialized ? <Navigate to="/" /> : <Setup />} />
        
        {/* Protected Routes */}
        <Route path="/" element={!initialized ? <Navigate to="/setup" /> : <MainLayout><Dashboard /></MainLayout>} />
        <Route path="/explorer" element={!initialized ? <Navigate to="/setup" /> : <MainLayout><DigitalTwinExplorer /></MainLayout>} />
        <Route path="/simulation" element={!initialized ? <Navigate to="/setup" /> : <MainLayout><SimulationLab /></MainLayout>} />
        <Route path="/evidence" element={!initialized ? <Navigate to="/setup" /> : <MainLayout><EvidenceGraph /></MainLayout>} />
        <Route path="/investigation" element={!initialized ? <Navigate to="/setup" /> : <MainLayout><AIInvestigation /></MainLayout>} />
        <Route path="/reports" element={!initialized ? <Navigate to="/setup" /> : <MainLayout><Reports /></MainLayout>} />
        <Route path="/transactions" element={!initialized ? <Navigate to="/setup" /> : <MainLayout><Transactions /></MainLayout>} />
        <Route path="/policies" element={!initialized ? <Navigate to="/setup" /> : <MainLayout><Policies /></MainLayout>} />
      </Routes>
    </BrowserRouter>
  );
}
