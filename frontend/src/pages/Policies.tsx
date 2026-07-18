import React from 'react';
import { ShieldCheck, ShieldAlert } from 'lucide-react';

export function Policies() {
  return (
    <div className="space-y-6">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-text">Compliance Policies</h1>
        <p className="text-textMuted">Active business rules evaluated by the Rule Engine</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {[
          { name: 'Segregation of Duties', desc: 'Prevents PO raiser from approving invoice.', status: 'Active' },
          { name: 'Duplicate Invoice', desc: 'Flags matching amounts within 30 days.', status: 'Active' },
          { name: 'Invoice After Payment', desc: 'Flags inverted chronological events.', status: 'Active' },
          { name: 'High Value Threshold', desc: 'Requires VP approval over ₹1,000,000.', status: 'Warning' },
        ].map((policy, i) => (
          <div key={i} className="glass-card p-5 flex items-start gap-4">
            <div className={`p-3 rounded-lg ${policy.status === 'Active' ? 'bg-emerald-500/10' : 'bg-amber-500/10'}`}>
              {policy.status === 'Active' ? (
                <ShieldCheck className="w-6 h-6 text-emerald-400" />
              ) : (
                <ShieldAlert className="w-6 h-6 text-amber-400" />
              )}
            </div>
            <div>
              <h3 className="font-bold text-lg">{policy.name}</h3>
              <p className="text-sm text-textMuted mt-1">{policy.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
