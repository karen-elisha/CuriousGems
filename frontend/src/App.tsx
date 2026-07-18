import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';

// Placeholder Pages
import { Dashboard } from './pages/Dashboard';
import { DigitalTwinExplorer } from './pages/DigitalTwinExplorer';
import { SimulationLab } from './pages/SimulationLab';
import { EvidenceGraph } from './pages/EvidenceGraph';
import { AIInvestigation } from './pages/AIInvestigation';
import { Reports } from './pages/Reports';
import { Transactions } from './pages/Transactions';
import { Policies } from './pages/Policies';

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen bg-background">
        <Sidebar />
        <main className="flex-1 ml-64 p-8 overflow-y-auto">
          <div className="max-w-7xl mx-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/explorer" element={<DigitalTwinExplorer />} />
              <Route path="/simulation" element={<SimulationLab />} />
              <Route path="/evidence" element={<EvidenceGraph />} />
              <Route path="/investigation" element={<AIInvestigation />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/transactions" element={<Transactions />} />
              <Route path="/policies" element={<Policies />} />
            </Routes>
          </div>
        </main>
      </div>
    </BrowserRouter>
  );
}
