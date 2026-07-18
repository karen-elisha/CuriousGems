<<<<<<< HEAD
import React from 'react';
import { motion } from 'framer-motion';
=======
import React, { useEffect, useState } from 'react';
import apiClient from '../api/client';
>>>>>>> 632c496 (Update frontend)

export function Transactions() {
  const [transactions, setTransactions] = useState<any[]>([]);

  useEffect(() => {
    apiClient.get('/transactions/').then(res => setTransactions(res.data.data)).catch(() => {});
  }, []);

  const statusColor = (status: string) => {
    switch (status) {
      case 'Completed': return 'bg-emerald-500/10 text-emerald-400';
      case 'Pending': return 'bg-amber-500/10 text-amber-400';
      case 'Flagged': return 'bg-red-500/10 text-red-400';
      default: return 'bg-slate-500/10 text-slate-400';
    }
  };

  return (
    <div className="space-y-6">
      <header className="mb-8">
<<<<<<< HEAD
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
=======
        <h1 className="text-3xl font-bold text-text">Transactions Ledger</h1>
        <p className="text-textMuted">Raw immutable transaction entries from the Digital Twin</p>
>>>>>>> 632c496 (Update frontend)
      </header>

      <motion.div 
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2 }}
        className="glass-panel overflow-hidden"
      >
        <table className="w-full text-left border-collapse">
          <thead>
<<<<<<< HEAD
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
=======
            <tr className="bg-slate-800/50 border-b border-surfaceBorder">
              <th className="p-4 text-sm font-medium text-textMuted">TXN ID</th>
              <th className="p-4 text-sm font-medium text-textMuted">Date</th>
              <th className="p-4 text-sm font-medium text-textMuted">Vendor</th>
              <th className="p-4 text-sm font-medium text-textMuted">Approver</th>
              <th className="p-4 text-sm font-medium text-textMuted">Amount</th>
              <th className="p-4 text-sm font-medium text-textMuted">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-surfaceBorder">
            {transactions.map((txn: any) => (
              <tr key={txn.id} className="hover:bg-slate-800/30 transition-colors">
                <td className="p-4 text-sm font-medium">{txn.id}</td>
                <td className="p-4 text-sm text-textMuted">{txn.date}</td>
                <td className="p-4 text-sm">{txn.vendor}</td>
                <td className="p-4 text-sm text-textMuted">{txn.approver}</td>
                <td className="p-4 text-sm font-mono">₹{txn.amount?.toLocaleString('en-IN')}</td>
                <td className="p-4">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusColor(txn.status)}`}>
                    {txn.status}
>>>>>>> 632c496 (Update frontend)
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
