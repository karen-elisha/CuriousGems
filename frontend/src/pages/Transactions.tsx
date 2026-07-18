import React from 'react';
import { motion } from 'framer-motion';

export function Transactions() {
  return (
    <div className="space-y-6">
      <header className="mb-8">
        <motion.h1 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-4xl font-bold text-text font-display tracking-tight"
        >
          Transactions Ledger
        </motion.h1>
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="text-textMuted text-lg mt-2"
        >
          Raw immutable transaction entries
        </motion.p>
      </header>

      <motion.div 
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2 }}
        className="glass-panel overflow-hidden"
      >
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-surface/60 border-b border-surfaceBorder backdrop-blur-md">
              <th className="p-5 text-sm font-semibold text-textMuted uppercase tracking-wider">TXN ID</th>
              <th className="p-5 text-sm font-semibold text-textMuted uppercase tracking-wider">Date</th>
              <th className="p-5 text-sm font-semibold text-textMuted uppercase tracking-wider">Amount</th>
              <th className="p-5 text-sm font-semibold text-textMuted uppercase tracking-wider">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-surfaceBorder">
            {[1, 2, 3, 4, 5].map((i) => (
              <tr key={i} className="hover:bg-surfaceHover/80 transition-colors group cursor-pointer">
                <td className="p-5 text-sm font-bold text-text group-hover:text-cyan-400 transition-colors">TXN-00{i}</td>
                <td className="p-5 text-sm text-textMuted">2026-11-0{i}</td>
                <td className="p-5 text-sm font-mono text-text">₹45,000.00</td>
                <td className="p-5">
                  <span className="px-3 py-1.5 text-xs font-bold uppercase tracking-wider bg-emerald-500/10 text-emerald-400 rounded-full border border-emerald-500/20 group-hover:shadow-[0_0_10px_rgba(16,185,129,0.2)] transition-shadow">
                    Completed
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </motion.div>
    </div>
  );
}
