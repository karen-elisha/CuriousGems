import React from 'react';
import { motion } from 'framer-motion';
import { BrainCircuit, Search, ShieldAlert } from 'lucide-react';

export function AIInvestigation() {
  return (
    <div className="space-y-6">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-text">AI Investigation</h1>
        <p className="text-textMuted">Gemma-powered forensic narrative generation</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-6">
          <div className="glass-panel p-6">
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
              <Search className="text-blue-400" /> Target Entity
            </h3>
            <div className="relative">
              <input type="text" className="input-field" placeholder="Entity ID (e.g., EMP-12)" />
              <button className="btn-primary w-full mt-4 flex justify-center items-center gap-2">
                <BrainCircuit className="w-4 h-4" /> Investigate
              </button>
            </div>
          </div>

          <div className="glass-card p-4 border-red-500/30">
            <h4 className="font-bold flex items-center gap-2 text-red-400 mb-2">
              <ShieldAlert className="w-4 h-4" /> Detected Rules
            </h4>
            <ul className="text-sm space-y-2 text-textMuted">
              <li>• Segregation of Duties (SOD_01)</li>
              <li>• Vendor Recently Created</li>
            </ul>
          </div>
        </div>

        <div className="lg:col-span-2 glass-panel p-8">
          <div className="flex items-center gap-3 mb-6 pb-4 border-b border-surfaceBorder">
            <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center">
              <BrainCircuit className="text-blue-400" />
            </div>
            <div>
              <h3 className="font-bold">Gemma Forensic Report</h3>
              <p className="text-sm text-textMuted">Generated from Twin Graph context</p>
            </div>
          </div>
          
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="prose prose-invert max-w-none text-textMuted space-y-4"
          >
            <p>
              Based on the extracted evidence graph, <strong>Employee EMP-12</strong> bypassed standard organizational controls.
            </p>
            <p>
              The topological analysis shows that EMP-12 directly raised <code>Purchase Order 44</code> and subsequently approved the corresponding <code>Transaction 99</code>. This forms a closed loop bypassing managerial oversight, directly violating the Segregation of Duties protocol.
            </p>
            <div className="p-4 bg-amber-500/10 border border-amber-500/20 rounded-lg text-amber-200 text-sm">
              <strong>Recommendation:</strong> Immediately freeze Transaction 99 and replace the approver on all pending workflows for EMP-12.
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
