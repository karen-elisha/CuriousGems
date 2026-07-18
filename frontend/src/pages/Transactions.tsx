import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Loader2, ListOrdered } from 'lucide-react';
import apiClient from '../api/client';

export function Transactions() {
  const [transactions, setTransactions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    apiClient.get('/transactions/')
      .then(res => {
        setTransactions(res.data.data || []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.response?.data?.detail || 'Failed to load transactions.');
        setLoading(false);
      });
  }, []);

  const statusColor = (status: string) => {
    switch (status) {
      case 'Completed': return 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20';
      case 'Pending': return 'bg-amber-500/10 text-amber-500 border-amber-500/20';
      case 'Flagged': return 'bg-rose-500/10 text-rose-500 border-rose-500/20';
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

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
        </div>
      ) : error ? (
        <div className="p-8 text-center text-rose-400 border border-rose-500/20 bg-rose-500/10 rounded-xl">
          {error}
        </div>
      ) : transactions.length === 0 ? (
        <div className="p-12 text-center border border-dashed border-surfaceBorder rounded-xl">
          <ListOrdered className="w-12 h-12 text-textMuted mx-auto mb-4 opacity-50" />
          <p className="text-textMuted text-lg">No transactions found in the Digital Twin.</p>
        </div>
      ) : (
        <motion.div 
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="glass-panel overflow-hidden"
        >
          <div className="px-6 py-4 border-b border-surfaceBorder flex items-center justify-between">
            <span className="text-sm text-textMuted font-medium">Showing {transactions.length} transactions</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse min-w-[800px]">
              <thead>
                <tr className="border-b border-surfaceBorder">
                  <th className="p-5 text-sm font-semibold text-textMuted uppercase tracking-wider">TXN ID</th>
                  <th className="p-5 text-sm font-semibold text-textMuted uppercase tracking-wider">Date</th>
                  <th className="p-5 text-sm font-semibold text-textMuted uppercase tracking-wider">Vendor</th>
                  <th className="p-5 text-sm font-semibold text-textMuted uppercase tracking-wider">Approver</th>
                  <th className="p-5 text-sm font-semibold text-textMuted uppercase tracking-wider text-right">Amount</th>
                  <th className="p-5 text-sm font-semibold text-textMuted uppercase tracking-wider text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surfaceBorder">
                {transactions.map((txn: any, i: number) => (
                  <motion.tr 
                    key={txn.id} 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: i * 0.02 }}
                    className="hover:bg-surfaceHover transition-colors group cursor-pointer"
                  >
                    <td className="p-5 text-sm font-bold text-text group-hover:text-primary transition-colors">{txn.id}</td>
                    <td className="p-5 text-sm text-textMuted">{txn.date}</td>
                    <td className="p-5 text-sm text-text">{txn.vendor}</td>
                    <td className="p-5 text-sm text-textMuted">{txn.approver}</td>
                    <td className="p-5 text-sm font-mono text-text text-right">₹{txn.amount?.toLocaleString('en-IN')}</td>
                    <td className="p-5 text-center">
                      <span className={`px-3 py-1.5 text-xs font-bold uppercase tracking-wider rounded-full border transition-shadow ${statusColor(txn.status)}`}>
                        {txn.status}
                      </span>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      )}
    </div>
  );
}
