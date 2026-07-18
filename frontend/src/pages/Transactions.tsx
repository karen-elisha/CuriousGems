import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import apiClient from '../api/client';

export function Transactions() {
  const [transactions, setTransactions] = useState<any[]>([]);

  useEffect(() => {
    apiClient.get('/transactions/').then(res => setTransactions(res.data.data)).catch(() => {});
  }, []);

  const statusColor = (status: string) => {
    switch (status) {
      case 'Completed': return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20 group-hover:shadow-[0_0_10px_rgba(16,185,129,0.2)]';
      case 'Pending': return 'bg-amber-500/10 text-amber-400 border-amber-500/20 group-hover:shadow-[0_0_10px_rgba(245,158,11,0.2)]';
      case 'Flagged': return 'bg-rose-500/10 text-rose-400 border-rose-500/20 group-hover:shadow-[0_0_10px_rgba(244,63,94,0.2)]';
      default: return 'bg-surfaceHover text-textMuted border-surfaceBorder';
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
          Transactions Ledger
        </motion.h1>
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="text-textMuted text-lg mt-2"
        >
          Raw immutable transaction entries from the Digital Twin
        </motion.p>
      </header>

      <motion.div 
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2 }}
        className="glass-panel overflow-hidden"
      >
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse min-w-[800px]">
            <thead>
              <tr className="bg-surface/60 border-b border-surfaceBorder backdrop-blur-md">
                <th className="p-5 text-sm font-semibold text-textMuted uppercase tracking-wider">TXN ID</th>
                <th className="p-5 text-sm font-semibold text-textMuted uppercase tracking-wider">Date</th>
                <th className="p-5 text-sm font-semibold text-textMuted uppercase tracking-wider">Vendor</th>
                <th className="p-5 text-sm font-semibold text-textMuted uppercase tracking-wider">Approver</th>
                <th className="p-5 text-sm font-semibold text-textMuted uppercase tracking-wider text-right">Amount</th>
                <th className="p-5 text-sm font-semibold text-textMuted uppercase tracking-wider text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surfaceBorder">
              {transactions.map((txn: any) => (
                <tr key={txn.id} className="hover:bg-surfaceHover/80 transition-colors group cursor-pointer">
                  <td className="p-5 text-sm font-bold text-text group-hover:text-cyan-400 transition-colors">{txn.id}</td>
                  <td className="p-5 text-sm text-textMuted">{txn.date}</td>
                  <td className="p-5 text-sm text-text">{txn.vendor}</td>
                  <td className="p-5 text-sm text-textMuted">{txn.approver}</td>
                  <td className="p-5 text-sm font-mono text-text text-right">₹{txn.amount?.toLocaleString('en-IN')}</td>
                  <td className="p-5 text-center">
                    <span className={`px-3 py-1.5 text-xs font-bold uppercase tracking-wider rounded-full border transition-shadow ${statusColor(txn.status)}`}>
                      {txn.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  );
}
