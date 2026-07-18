import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { GitBranch, Play, RotateCcw } from 'lucide-react';

export function SimulationLab() {
  const [simulating, setSimulating] = useState(false);

  return (
    <div className="space-y-6">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-text">Simulation Lab</h1>
        <p className="text-textMuted">Run "What-If" scenarios on branched states</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-6">
          <div className="glass-panel p-6">
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
              <GitBranch className="text-blue-400" /> New Branch
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-textMuted mb-2">Scenario Action</label>
                <select className="input-field">
                  <option>Block Vendor</option>
                  <option>Delay Payment</option>
                  <option>Replace Approver</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-textMuted mb-2">Target ID</label>
                <input type="text" className="input-field" placeholder="e.g. VEN-102" />
              </div>
              <button className="btn-primary w-full flex items-center justify-center gap-2" onClick={() => setSimulating(true)}>
                <Play className="w-4 h-4" /> Execute Simulation
              </button>
            </div>
          </div>

          <div className="glass-card p-4 flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Active Branch</p>
              <p className="text-xs text-emerald-400 mt-1">Sim: Block Vendor VEN-102</p>
            </div>
            <button className="p-2 hover:bg-slate-700 rounded-lg transition-colors text-textMuted hover:text-white">
              <RotateCcw className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="lg:col-span-2 glass-panel p-6">
          <h3 className="text-lg font-bold mb-4">Simulation Diff Impact</h3>
          {simulating ? (
            <div className="space-y-4">
              <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl">
                <p className="font-medium text-red-400">- 4 Pending Transactions Blocked</p>
              </motion.div>
              <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 }} className="p-4 bg-amber-500/10 border border-amber-500/20 rounded-xl">
                <p className="font-medium text-amber-400">! Department Spend Velocity drops by 14%</p>
              </motion.div>
              <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }} className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
                <p className="font-medium text-emerald-400">+ 0 Compliance Violations remaining</p>
              </motion.div>
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center text-textMuted border-2 border-dashed border-surfaceBorder rounded-xl">
              Execute a scenario to view structural diffs
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
