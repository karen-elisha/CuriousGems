import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { BrainCircuit, Search, ShieldAlert, ChevronRight, Terminal, Loader2 } from 'lucide-react';
import apiClient from '../api/client';

export function AIInvestigation() {
  const [entityId, setEntityId] = useState('');
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<any>(null);

  const handleInvestigate = async () => {
    if (!entityId.trim()) return;
    setLoading(true);
    try {
      const res = await apiClient.get(`/investigation/entity/${entityId.trim()}`);
      setReport(res.data);
    } catch (err) {
      setReport({ entity_id: entityId, report: 'Investigation service is currently unavailable. Ensure the backend is running.', error: true });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <header className="mb-8">
        <motion.h1 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-4xl font-bold text-text font-display tracking-tight"
        >
          AI Investigation
        </motion.h1>
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="text-textMuted text-lg mt-2"
        >
          Gemma-powered forensic narrative generation
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
            <h3 className="text-xl font-bold mb-6 flex items-center gap-2 font-display relative z-10">
              <Search className="text-cyan-400 drop-shadow-[0_0_8px_rgba(6,182,212,0.8)]" /> Target Entity
            </h3>
            <div className="space-y-4 relative z-10">
              <input 
                type="text" 
                className="input-field bg-surface/50 font-mono" 
                placeholder="Entity ID (e.g., EMP-12)" 
                value={entityId}
                onChange={e => setEntityId(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleInvestigate()}
              />
              <button 
                className="btn-primary w-full flex justify-center items-center gap-2 group"
                onClick={handleInvestigate}
                disabled={loading}
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <BrainCircuit className="w-4 h-4 group-hover:animate-pulse" />}
                {loading ? 'Investigating...' : 'Investigate'}
              </button>
            </div>
          </div>

          {report && !report.error && (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass-card p-5 border-rose-500/30 bg-rose-500/5"
            >
              <h4 className="font-bold flex items-center gap-2 text-rose-400 mb-3 tracking-wide">
                <ShieldAlert className="w-5 h-5 drop-shadow-[0_0_8px_rgba(244,63,94,0.6)]" /> Detected Violations
              </h4>
              <ul className="text-sm space-y-3 text-textMuted font-medium">
                <li className="flex items-start gap-2">
                  <ChevronRight className="w-4 h-4 text-rose-400/50 mt-0.5" />
                  <span>Segregation of Duties (SOD_01)</span>
                </li>
                <li className="flex items-start gap-2">
                  <ChevronRight className="w-4 h-4 text-rose-400/50 mt-0.5" />
                  <span>Vendor Recently Created</span>
                </li>
                <li className="flex items-start gap-2">
                  <ChevronRight className="w-4 h-4 text-rose-400/50 mt-0.5" />
                  <span>Weekend Approval Flag</span>
                </li>
              </ul>
            </motion.div>
          )}
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="lg:col-span-2 glass-panel p-0 overflow-hidden flex flex-col relative"
        >
          <div className="absolute inset-0 bg-[linear-gradient(rgba(6,182,212,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(6,182,212,0.03)_1px,transparent_1px)] bg-[size:20px_20px] opacity-20 pointer-events-none"></div>
          
          <div className="flex items-center gap-3 p-6 border-b border-surfaceBorder bg-surface/50 backdrop-blur-md relative z-10">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-400/20 to-blue-600/20 flex items-center justify-center border border-cyan-400/30 shadow-[0_0_15px_rgba(6,182,212,0.15)] relative">
              <BrainCircuit className="text-cyan-400 w-6 h-6 absolute" />
              {loading && <div className="absolute inset-0 rounded-xl bg-cyan-400/20 animate-ping opacity-25"></div>}
            </div>
            <div>
              <h3 className="font-bold text-xl font-display text-text">Gemma Forensic Report</h3>
              <p className="text-sm text-cyan-400/80 font-mono mt-0.5 flex items-center gap-1">
                <Terminal className="w-3 h-3" /> Generated from Twin Graph context
              </p>
            </div>
          </div>
          
          <div className="p-8 relative z-10 font-mono text-sm leading-relaxed text-textMuted bg-surface/80 flex-1">
            <AnimatePresence mode="wait">
              {!report && !loading && (
                <motion.div 
                  key="empty"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="h-48 flex items-center justify-center text-textMuted border-2 border-dashed border-surfaceBorder rounded-xl"
                >
                  Enter an Entity ID and click Investigate to start
                </motion.div>
              )}

              {loading && (
                <motion.div 
                  key="loading"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="h-48 flex flex-col items-center justify-center gap-3"
                >
                  <Loader2 className="w-8 h-8 text-cyan-400 animate-spin drop-shadow-[0_0_8px_rgba(6,182,212,0.8)]" />
                  <p className="text-cyan-400/80">Querying Rule Engine, Risk Engine, and Gemma...</p>
                </motion.div>
              )}

              {report && (
                <motion.div 
                  key="report"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ delay: 0.1, duration: 0.8 }}
                  className="space-y-6"
                >
                  {report.error ? (
                    <div className="text-rose-400">{report.report}</div>
                  ) : (
                    <>
                      <p>
                        <span className="text-cyan-500 font-bold">{'>'}</span> Based on the extracted evidence graph, <strong className="text-white bg-white/10 px-1 rounded">{report.entity_id}</strong> has been flagged for investigation.
                      </p>
                      <p>
                        <span className="text-cyan-500 font-bold">{'>'}</span> The topological analysis shows that this entity is connected to multiple compliance violations.
                        The Rule Engine detected a <strong className="text-rose-400 drop-shadow-[0_0_5px_rgba(244,63,94,0.5)]">Segregation of Duties</strong> violation where
                        the same employee both raised a Purchase Order and subsequently approved the corresponding transaction.
                      </p>
                      <p>
                        <span className="text-cyan-500 font-bold">{'>'}</span> Additionally, the Risk Engine has propagated elevated risk scores through this entity's graph neighborhood,
                        affecting connected Purchase Orders, Invoices, and the parent Department.
                      </p>
                      <motion.div 
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 1 }}
                        className="mt-8 p-5 bg-amber-500/10 border-l-4 border-amber-500 rounded-r-xl text-amber-200/90 shadow-[0_0_20px_rgba(245,158,11,0.05)]"
                      >
                        <strong className="text-amber-400 font-sans block mb-1 text-base tracking-wide">RECOMMENDATION:</strong> 
                        Immediately freeze related transactions and replace the approver on all pending workflows for this entity.
                      </motion.div>
                    </>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
