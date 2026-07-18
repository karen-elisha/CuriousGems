import React, { useState } from 'react';
<<<<<<< HEAD
import { motion, AnimatePresence } from 'framer-motion';
import { GitBranch, Play, RotateCcw, AlertTriangle, CheckCircle, TrendingDown } from 'lucide-react';
=======
import { motion } from 'framer-motion';
import { GitBranch, Play, RotateCcw } from 'lucide-react';
import apiClient from '../api/client';

const actionOptions = [
  'Block Vendor',
  'Delay Payment',
  'Replace Approver',
  'Freeze Transaction',
  'Approve Payment',
  'Reject Payment',
];
>>>>>>> 632c496 (Update frontend)

export function SimulationLab() {
  const [simulating, setSimulating] = useState(false);
  const [actionType, setActionType] = useState(actionOptions[0]);
  const [targetId, setTargetId] = useState('');
  const [diffs, setDiffs] = useState<any[]>([]);

  const executeSimulation = async () => {
    if (!targetId.trim()) return;
    setSimulating(true);
    try {
      await apiClient.post('/simulation/execute', {
        action_type: actionType,
        target_id: targetId.trim(),
        parameters: {},
      });
    } catch {}
    // Show demo diff results
    setDiffs([
      { type: 'danger', text: `4 Pending Transactions Blocked for ${targetId}` },
      { type: 'warning', text: 'Department Spend Velocity drops by 14%' },
      { type: 'success', text: '0 Compliance Violations remaining after action' },
    ]);
  };

  const rollback = async () => {
    try { await apiClient.post('/simulation/rollback'); } catch {}
    setSimulating(false);
    setDiffs([]);
  };

  return (
    <div className="space-y-6">
      <header className="mb-8">
        <motion.h1 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-4xl font-bold text-text font-display tracking-tight"
        >
          Simulation Lab
        </motion.h1>
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="text-textMuted text-lg mt-2"
        >
          Run "What-If" scenarios on branched states
        </motion.p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="lg:col-span-1 space-y-6"
        >
          <div className="glass-panel p-6 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-500/10 rounded-full blur-3xl -mr-16 -mt-16"></div>
            <h3 className="text-xl font-bold mb-6 flex items-center gap-2 font-display">
              <GitBranch className="text-cyan-400 drop-shadow-[0_0_8px_rgba(6,182,212,0.8)]" /> New Branch
            </h3>
            <div className="space-y-5 relative z-10">
              <div>
<<<<<<< HEAD
                <label className="block text-sm font-medium text-textMuted mb-2 tracking-wide">Scenario Action</label>
                <select className="input-field bg-surface/50">
                  <option>Block Vendor</option>
                  <option>Delay Payment</option>
                  <option>Replace Approver</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-textMuted mb-2 tracking-wide">Target ID</label>
                <input type="text" className="input-field bg-surface/50" placeholder="e.g. VEN-102" />
              </div>
              <button 
                className="btn-primary w-full flex items-center justify-center gap-2 mt-2" 
                onClick={() => setSimulating(true)}
              >
                <Play className="w-4 h-4 fill-current" /> Execute Simulation
=======
                <label className="block text-sm font-medium text-textMuted mb-2">Scenario Action</label>
                <select className="input-field" value={actionType} onChange={e => setActionType(e.target.value)}>
                  {actionOptions.map(opt => <option key={opt}>{opt}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-textMuted mb-2">Target ID</label>
                <input 
                  type="text" 
                  className="input-field" 
                  placeholder="e.g. VEN-07"
                  value={targetId}
                  onChange={e => setTargetId(e.target.value)} 
                />
              </div>
              <button className="btn-primary w-full flex items-center justify-center gap-2" onClick={executeSimulation}>
                <Play className="w-4 h-4" /> Execute Simulation
>>>>>>> 632c496 (Update frontend)
              </button>
            </div>
          </div>

<<<<<<< HEAD
          <div className="glass-card p-5 flex items-center justify-between border-cyan-500/20 bg-cyan-500/5">
            <div>
              <p className="text-sm font-medium text-textMuted uppercase tracking-wider">Active Branch</p>
              <p className="text-sm font-bold text-cyan-400 mt-1 drop-shadow-[0_0_8px_rgba(6,182,212,0.4)]">Sim: Block Vendor VEN-102</p>
            </div>
            <button 
              className="p-2 hover:bg-surfaceHover rounded-xl transition-colors text-textMuted hover:text-white hover:shadow-glow-primary border border-transparent hover:border-surfaceBorder"
              onClick={() => setSimulating(false)}
            >
              <RotateCcw className="w-5 h-5" />
            </button>
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="lg:col-span-2 glass-panel p-6"
        >
          <h3 className="text-xl font-bold mb-6 font-display text-text flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-violet-400 shadow-glow-accent"></span>
            Simulation Diff Impact
          </h3>
          <div className="min-h-[300px] flex flex-col justify-center">
            <AnimatePresence mode="wait">
              {simulating ? (
                <motion.div 
                  key="results"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  className="space-y-4 w-full"
                >
                  <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl flex items-center gap-3 shadow-[0_0_15px_rgba(244,63,94,0.1)]">
                    <div className="p-2 bg-rose-500/20 rounded-lg"><AlertTriangle className="w-5 h-5 text-rose-400" /></div>
                    <p className="font-medium text-rose-300">- 4 Pending Transactions Blocked</p>
                  </motion.div>
                  <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 }} className="p-4 bg-amber-500/10 border border-amber-500/30 rounded-xl flex items-center gap-3 shadow-[0_0_15px_rgba(245,158,11,0.1)]">
                    <div className="p-2 bg-amber-500/20 rounded-lg"><TrendingDown className="w-5 h-5 text-amber-400" /></div>
                    <p className="font-medium text-amber-300">! Department Spend Velocity drops by 14%</p>
                  </motion.div>
                  <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }} className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl flex items-center gap-3 shadow-[0_0_15px_rgba(16,185,129,0.1)]">
                    <div className="p-2 bg-emerald-500/20 rounded-lg"><CheckCircle className="w-5 h-5 text-emerald-400" /></div>
                    <p className="font-medium text-emerald-300">+ 0 Compliance Violations remaining</p>
                  </motion.div>
                </motion.div>
              ) : (
                <motion.div 
                  key="empty"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="h-64 flex flex-col items-center justify-center text-textMuted border-2 border-dashed border-surfaceBorder rounded-2xl bg-surface/30"
                >
                  <GitBranch className="w-12 h-12 text-surfaceBorder mb-4" />
                  <p className="font-medium">Execute a scenario to view structural diffs</p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>
=======
          {simulating && (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass-card p-4 flex items-center justify-between"
            >
              <div>
                <p className="text-sm font-medium">Active Branch</p>
                <p className="text-xs text-emerald-400 mt-1">Sim: {actionType} {targetId}</p>
              </div>
              <button onClick={rollback} className="p-2 hover:bg-slate-700 rounded-lg transition-colors text-textMuted hover:text-white">
                <RotateCcw className="w-5 h-5" />
              </button>
            </motion.div>
          )}
        </div>

        <div className="lg:col-span-2 glass-panel p-6">
          <h3 className="text-lg font-bold mb-4">Simulation Diff Impact</h3>
          {diffs.length > 0 ? (
            <div className="space-y-4">
              {diffs.map((diff, i) => {
                const colors = {
                  danger: 'bg-red-500/10 border-red-500/20 text-red-400',
                  warning: 'bg-amber-500/10 border-amber-500/20 text-amber-400',
                  success: 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400',
                }[diff.type] || '';
                const prefix = { danger: '−', warning: '!', success: '+' }[diff.type] || '';
                return (
                  <motion.div 
                    key={i}
                    initial={{ opacity: 0, x: -20 }} 
                    animate={{ opacity: 1, x: 0 }} 
                    transition={{ delay: i * 0.1 }}
                    className={`p-4 border rounded-xl font-medium ${colors}`}
                  >
                    {prefix} {diff.text}
                  </motion.div>
                );
              })}
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center text-textMuted border-2 border-dashed border-surfaceBorder rounded-xl">
              Execute a scenario to view structural diffs
            </div>
          )}
        </div>
>>>>>>> 632c496 (Update frontend)
      </div>
    </div>
  );
}
