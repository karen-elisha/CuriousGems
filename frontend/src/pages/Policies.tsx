import React from 'react';
import { ShieldCheck, ShieldAlert } from 'lucide-react';
import { motion } from 'framer-motion';

export function Policies() {
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
              {policy.status === 'Active' ? (
                <ShieldCheck className="w-6 h-6 text-emerald-400 drop-shadow-[0_0_8px_rgba(16,185,129,0.8)]" />
              ) : (
                <ShieldAlert className="w-6 h-6 text-amber-400 drop-shadow-[0_0_8px_rgba(245,158,11,0.8)]" />
              )}
            </div>
            <div>
              <h3 className="font-bold text-xl font-display text-text">{policy.name}</h3>
              <p className="text-sm text-textMuted mt-1">{policy.desc}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
