<<<<<<< HEAD
import React from 'react';
import { ShieldCheck, ShieldAlert } from 'lucide-react';
import { motion } from 'framer-motion';
=======
import React, { useEffect, useState } from 'react';
import { ShieldCheck, ShieldAlert, ShieldX } from 'lucide-react';
import apiClient from '../api/client';
>>>>>>> 632c496 (Update frontend)

export function Policies() {
  const [policies, setPolicies] = useState<any[]>([]);

  useEffect(() => {
    apiClient.get('/policies/').then(res => setPolicies(res.data.data)).catch(() => {});
  }, []);

  const severityColor = (severity: string) => {
    switch (severity) {
      case 'Critical': return 'bg-red-500/10 text-red-400';
      case 'High': return 'bg-amber-500/10 text-amber-400';
      case 'Medium': return 'bg-blue-500/10 text-blue-400';
      default: return 'bg-slate-500/10 text-slate-400';
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
<<<<<<< HEAD
        {[
          { name: 'Segregation of Duties', desc: 'Prevents PO raiser from approving invoice.', status: 'Active' },
          { name: 'Duplicate Invoice', desc: 'Flags matching amounts within 30 days.', status: 'Active' },
          { name: 'Invoice After Payment', desc: 'Flags inverted chronological events.', status: 'Active' },
          { name: 'High Value Threshold', desc: 'Requires VP approval over ₹1,000,000.', status: 'Warning' },
        ].map((policy, i) => (
          <motion.div 
            key={i} 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className={`glass-card p-6 flex items-start gap-4 group hover:shadow-lg ${policy.status === 'Active' ? 'hover:border-emerald-500/50 hover:shadow-[0_0_15px_rgba(16,185,129,0.15)]' : 'hover:border-amber-500/50 hover:shadow-[0_0_15px_rgba(245,158,11,0.15)]'}`}
          >
            <div className={`p-4 rounded-xl transition-transform duration-300 group-hover:scale-110 group-hover:-rotate-3 ${policy.status === 'Active' ? 'bg-emerald-500/10' : 'bg-amber-500/10'}`}>
=======
        {policies.map((policy: any) => (
          <div key={policy.id} className="glass-card p-5 flex items-start gap-4">
            <div className={`p-3 rounded-lg ${policy.status === 'Active' ? 'bg-emerald-500/10' : 'bg-amber-500/10'}`}>
>>>>>>> 632c496 (Update frontend)
              {policy.status === 'Active' ? (
                <ShieldCheck className="w-6 h-6 text-emerald-400 drop-shadow-[0_0_8px_rgba(16,185,129,0.8)]" />
              ) : (
                <ShieldAlert className="w-6 h-6 text-amber-400 drop-shadow-[0_0_8px_rgba(245,158,11,0.8)]" />
              )}
            </div>
<<<<<<< HEAD
            <div>
              <h3 className="font-bold text-xl font-display text-text">{policy.name}</h3>
              <p className="text-sm text-textMuted mt-1">{policy.desc}</p>
=======
            <div className="flex-1">
              <div className="flex items-center justify-between mb-1">
                <h3 className="font-bold text-lg">{policy.name}</h3>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${severityColor(policy.severity)}`}>
                  {policy.severity}
                </span>
              </div>
              <p className="text-sm text-textMuted">{policy.description}</p>
              <p className="text-xs text-textMuted mt-2 font-mono">{policy.id}</p>
>>>>>>> 632c496 (Update frontend)
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
