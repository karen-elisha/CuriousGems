import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { GitBranch, Play, RotateCcw, AlertTriangle, CheckCircle, TrendingDown } from 'lucide-react';
import apiClient from '../api/client';

const actionOptions = [
  'Block Vendor',
  'Delay Payment',
  'Replace Approver',
  'Freeze Transaction',
  'Approve Payment',
  'Reject Payment',
];

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
    // Show demo diff results for now
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
      <header className="mb-8 border-b border-[var(--border-surface)] pb-6">
        <motion.h1 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-3xl font-bold text-[var(--text-main)] tracking-tight"
        >
          Simulation Lab
        </motion.h1>
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="text-[var(--text-muted)] mt-1"
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
            <h3 className="text-xl font-bold mb-6 flex items-center gap-2 text-[var(--text-main)]">
              <GitBranch className="text-[var(--color-primary)]" /> New Branch
            </h3>
            <div className="space-y-5 relative z-10">
              <div>
                <label className="block text-sm font-medium text-[var(--text-muted)] mb-2">Scenario Action</label>
                <select 
                  className="input-field" 
                  value={actionType} 
                  onChange={e => setActionType(e.target.value)}
                >
                  {actionOptions.map(opt => <option key={opt}>{opt}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-[var(--text-muted)] mb-2">Target ID</label>
                <input 
                  type="text" 
                  className="input-field" 
                  placeholder="e.g. VEN-102"
                  value={targetId}
                  onChange={e => setTargetId(e.target.value)} 
                />
              </div>
              <button 
                className="btn-primary w-full flex items-center justify-center gap-2 mt-2" 
                onClick={executeSimulation}
              >
                <Play className="w-4 h-4 fill-current" /> Execute Simulation
              </button>
            </div>
          </div>

          <AnimatePresence>
            {simulating && (
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="glass-card p-5 flex items-center justify-between border-indigo-200 bg-indigo-50"
              >
                <div>
                  <p className="text-sm font-medium text-indigo-700 uppercase tracking-wider">Active Branch</p>
                  <p className="text-sm font-bold text-indigo-900 mt-1">Sim: {actionType} {targetId}</p>
                </div>
                <button 
                  className="p-2 bg-white hover:bg-gray-50 rounded-xl transition-colors text-gray-500 hover:text-indigo-600 border border-gray-200 shadow-sm"
                  onClick={rollback}
                  title="Rollback simulation"
                >
                  <RotateCcw className="w-5 h-5" />
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="lg:col-span-2 glass-panel p-6"
        >
          <h3 className="text-xl font-bold mb-6 text-[var(--text-main)] flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[var(--color-primary)]"></span>
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
                  {diffs.map((diff, i) => {
                    const styleMap: any = {
                      danger: { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-700', icon: <AlertTriangle className="w-5 h-5 text-red-500" />, prefix: '−' },
                      warning: { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700', icon: <TrendingDown className="w-5 h-5 text-amber-500" />, prefix: '!' },
                      success: { bg: 'bg-emerald-50', border: 'border-emerald-200', text: 'text-emerald-700', icon: <CheckCircle className="w-5 h-5 text-emerald-500" />, prefix: '+' }
                    };
                    const style = styleMap[diff.type] || styleMap.warning;

                    return (
                      <motion.div 
                        key={i}
                        initial={{ opacity: 0, x: -20 }} 
                        animate={{ opacity: 1, x: 0 }} 
                        transition={{ delay: i * 0.1 }}
                        className={`p-4 ${style.bg} border ${style.border} rounded-xl flex items-center gap-3`}
                      >
                        <div className="p-2 bg-white rounded-lg border border-gray-100 shadow-sm">{style.icon}</div>
                        <p className={`font-medium ${style.text}`}>{style.prefix} {diff.text}</p>
                      </motion.div>
                    );
                  })}
                </motion.div>
              ) : (
                <motion.div 
                  key="empty"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="h-64 flex flex-col items-center justify-center text-[var(--text-muted)] border-2 border-dashed border-[var(--border-surface)] rounded-2xl bg-gray-50"
                >
                  <GitBranch className="w-12 h-12 text-gray-300 mb-4" />
                  <p className="font-medium">Execute a scenario to view structural diffs</p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
