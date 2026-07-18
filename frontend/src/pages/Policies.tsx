import { useEffect, useState } from 'react';
import { ShieldCheck, ShieldAlert } from 'lucide-react';
import { motion } from 'framer-motion';
import apiClient from '../api/client';

export function Policies() {
  const [policies, setPolicies] = useState<any[]>([]);

  useEffect(() => {
    apiClient.get('/policies/').then(res => setPolicies(res.data.data)).catch(() => {});
  }, []);

  const severityColor = (severity: string) => {
    switch (severity) {
      case 'Critical': return 'bg-rose-500/10 text-rose-400 border border-rose-500/20';
      case 'High': return 'bg-amber-500/10 text-amber-400 border border-amber-500/20';
      case 'Medium': return 'bg-blue-500/10 text-blue-400 border border-blue-500/20';
      default: return 'bg-surfaceHover text-textMuted border border-surfaceBorder';
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
          Compliance Policies
        </motion.h1>
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="text-textMuted text-lg mt-2"
        >
          Active business rules evaluated by the Rule Engine
        </motion.p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {policies.map((policy: any, i: number) => (
          <motion.div 
            key={policy.id} 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className={`glass-card p-6 flex items-start gap-4 group hover:shadow-lg ${policy.status === 'Active' ? 'hover:border-emerald-500/50 hover:shadow-[0_0_15px_rgba(16,185,129,0.15)]' : 'hover:border-amber-500/50 hover:shadow-[0_0_15px_rgba(245,158,11,0.15)]'}`}
          >
            <div className={`p-4 rounded-xl transition-transform duration-300 group-hover:scale-110 group-hover:-rotate-3 ${policy.status === 'Active' ? 'bg-emerald-500/10' : 'bg-amber-500/10'}`}>
              {policy.status === 'Active' ? (
                <ShieldCheck className="w-6 h-6 text-emerald-400 drop-shadow-[0_0_8px_rgba(16,185,129,0.8)]" />
              ) : (
                <ShieldAlert className="w-6 h-6 text-amber-400 drop-shadow-[0_0_8px_rgba(245,158,11,0.8)]" />
              )}
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between mb-1">
                <h3 className="font-bold text-xl font-display text-text group-hover:text-cyan-400 transition-colors">{policy.name}</h3>
                <span className={`px-2 py-1 text-xs font-bold uppercase tracking-wider rounded ${severityColor(policy.severity)}`}>
                  {policy.severity}
                </span>
              </div>
              <p className="text-sm text-textMuted mt-1">{policy.description}</p>
              <p className="text-xs text-textMuted mt-3 font-mono bg-surfaceHover inline-block px-2 py-1 rounded border border-surfaceBorder">{policy.id}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
