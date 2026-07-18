import React from 'react';

export function Transactions() {
  return (
    <div className="space-y-6">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-text">Transactions Ledger</h1>
        <p className="text-textMuted">Raw immutable transaction entries</p>
      </header>

      <div className="glass-panel overflow-hidden">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-800/50 border-b border-surfaceBorder">
              <th className="p-4 text-sm font-medium text-textMuted">TXN ID</th>
              <th className="p-4 text-sm font-medium text-textMuted">Date</th>
              <th className="p-4 text-sm font-medium text-textMuted">Amount</th>
              <th className="p-4 text-sm font-medium text-textMuted">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-surfaceBorder">
            {[1, 2, 3, 4, 5].map((i) => (
              <tr key={i} className="hover:bg-slate-800/30 transition-colors">
                <td className="p-4 text-sm font-medium">TXN-00{i}</td>
                <td className="p-4 text-sm text-textMuted">2026-11-0{i}</td>
                <td className="p-4 text-sm font-mono">₹45,000.00</td>
                <td className="p-4">
                  <span className="px-2 py-1 text-xs font-medium bg-emerald-500/10 text-emerald-400 rounded-full">
                    Completed
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
