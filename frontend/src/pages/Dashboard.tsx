import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Database, AlertTriangle, CheckCircle, ShieldAlert, FileText, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import apiClient from '../api/client';

export function Dashboard() {
  const [metrics, setMetrics] = useState<any>(null);

  useEffect(() => {
    apiClient.get('/dashboard/metrics').then(res => setMetrics(res.data.data)).catch(() => {});
  }, []);

  if (!metrics) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="relative flex h-8 w-8">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-8 w-8 bg-cyan-500 shadow-[0_0_15px_rgba(6,182,212,0.8)]"></span>
        </div>
      </div>
    );
  }

  const stats = [
    { title: 'Total Nodes Analyzed', value: metrics.total_nodes_analyzed?.toLocaleString() || 0, icon: Database, color: 'text-cyan-400', bg: 'bg-cyan-400/10', glow: 'shadow-glow-primary' },
    { title: 'Violations Found', value: metrics.total_violations_found || 0, icon: ShieldAlert, color: 'text-rose-400', bg: 'bg-rose-400/10', glow: 'shadow-glow-danger' },
    { title: 'High Risk Vendors', value: metrics.high_risk_vendors || 0, icon: AlertTriangle, color: 'text-amber-400', bg: 'bg-amber-400/10', glow: 'shadow-[0_0_20px_rgba(251,191,36,0.3)]' },
    { title: 'Test Status', value: metrics.test_status || 'Complete', icon: CheckCircle, color: 'text-emerald-400', bg: 'bg-emerald-400/10', glow: 'shadow-[0_0_20px_rgba(52,211,153,0.3)]' },
  ];

  return (
    <div className="space-y-6">
      <header className="mb-8">
        <motion.h1 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-4xl font-bold text-text font-display tracking-tight"
        >
          Test Execution Results
        </motion.h1>
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="text-textMuted text-lg mt-2"
        >
          Summary of compliance violations caught in the uploaded test case dataset.
        </motion.p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, i) => (
          <motion.div 
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className={`glass-card p-6 group hover:${stat.glow}`}
          >
            <div className="flex items-center gap-4">
              <div className={`p-3 rounded-xl ${stat.bg} transition-transform duration-300 group-hover:scale-110 group-hover:rotate-3`}>
                <stat.icon className={`w-7 h-7 ${stat.color}`} />
              </div>
              <div>
                <p className="text-sm text-textMuted font-medium uppercase tracking-wider">{stat.title}</p>
                <h3 className="text-3xl font-bold text-text mt-1 font-display">{stat.value}</h3>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div 
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="lg:col-span-1 glass-panel p-6 h-[420px] flex flex-col"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold font-display text-text flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-cyan-400 shadow-glow-primary"></span>
              Caught Violations
            </h3>
            <Link to="/evidence" className="text-sm font-medium text-cyan-400 hover:text-cyan-300 hover:underline flex items-center gap-1 transition-colors">
              View Evidence Graphs <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
          
          <div className="space-y-4 flex-1 overflow-y-auto pr-2 custom-scrollbar">
            {metrics.recent_violations?.length > 0 ? (
              metrics.recent_violations.map((v: any, idx: number) => (
                <div key={idx} className="group flex items-start gap-4 p-4 rounded-xl hover:bg-surfaceHover border border-surfaceBorder transition-all duration-300 hover:shadow-lg hover:-translate-y-0.5 cursor-pointer">
                  <div className="p-2 bg-rose-500/10 text-rose-400 rounded-lg border border-rose-500/20 group-hover:scale-110 transition-transform">
                    <ShieldAlert className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="font-bold text-text text-sm group-hover:text-cyan-300 transition-colors">{v.policy_id}: {v.policy_name}</h4>
                    <p className="text-sm text-textMuted mt-1">{v.detail}</p>
                    <div className="mt-3 flex items-center gap-2">
                      <span className="px-2 py-1 bg-rose-500/10 text-rose-400 text-xs font-bold uppercase tracking-wider rounded border border-rose-500/20">{v.severity}</span>
                      <span className="text-xs text-textMuted font-mono bg-surfaceHover px-2 py-1 rounded border border-surfaceBorder">{v.entity_type} • {v.entity_id}</span>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-8 text-center text-textMuted border border-dashed border-surfaceBorder rounded-xl bg-surface/30">
                No compliance violations found in this test case.
              </div>
            )}
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-panel p-6 flex flex-col"
        >
          <h3 className="text-xl font-bold mb-6 font-display text-text flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-violet-400 shadow-glow-accent"></span>
            Violation Distribution by Severity
          </h3>
          <div className="space-y-6">
            {metrics.severity_data?.map((sev: any) => (
              <div key={sev.name} className="flex items-center gap-4">
                <div className="w-24 text-sm font-semibold text-text">{sev.name}</div>
                <div className="flex-1 h-3 bg-surfaceHover rounded-full overflow-hidden border border-surfaceBorder">
                  <div 
                    className={`h-full shadow-[0_0_10px_currentColor] ${sev.name === 'Critical' ? 'bg-rose-500 text-rose-500' : sev.name === 'High' ? 'bg-amber-500 text-amber-500' : 'bg-cyan-500 text-cyan-500'}`}
                    style={{ width: `${Math.max((sev.count / metrics.total_violations_found) * 100, 2)}%` }}
                  />
                </div>
                <div className="w-12 text-right text-sm font-bold text-textMuted">{sev.count}</div>
              </div>
            ))}
          </div>
          
          <div className="mt-auto p-6 bg-violet-500/10 border border-violet-500/20 rounded-xl relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-violet-500/20 rounded-full blur-3xl -mr-16 -mt-16"></div>
            <h4 className="font-bold text-violet-300 mb-2 flex items-center gap-2 relative z-10">
              <FileText className="w-5 h-5 drop-shadow-[0_0_8px_rgba(139,92,246,0.8)]" /> Next Step: Unstructured PDF Auditing
            </h4>
            <p className="text-sm text-violet-200/70 leading-relaxed mb-4 relative z-10">
              The deterministic engine has successfully analyzed the structured datasets. To cross-reference specific entities against unstructured evidence (e.g. Vendor Invoices), proceed to the AI Investigation tab.
            </p>
            <Link to="/investigation" className="btn-primary inline-flex relative z-10">Launch AI Auditor</Link>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
