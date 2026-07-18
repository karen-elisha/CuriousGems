import { useEffect, useState } from 'react';
import { ShieldCheck, ShieldAlert, Loader2, ShieldOff } from 'lucide-react';
import { motion } from 'framer-motion';
import apiClient from '../api/client';

export function Policies() {
  const [policies, setPolicies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    apiClient.get('/policies/')
      .then(res => {
        setPolicies(res.data.data || []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.response?.data?.detail || 'Failed to load policies.');
        setLoading(false);
      });
  }, []);

  const severityColor = (severity: string) => {
    switch (severity) {
      case 'Critical': return 'bg-rose-500/10 text-rose-500 border border-rose-500/20';
      case 'High': return 'bg-amber-500/10 text-amber-500 border border-amber-500/20';
      case 'Medium': return 'bg-blue-500/10 text-blue-500 border border-blue-500/20';
      case 'Low': return 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20';
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

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
        </div>
      ) : error ? (
        <div className="p-8 text-center text-rose-400 border border-rose-500/20 bg-rose-500/10 rounded-xl">
          {error}
        </div>
      ) : policies.length === 0 ? (
        <div className="p-12 text-center border border-dashed border-surfaceBorder rounded-xl">
          <ShieldOff className="w-12 h-12 text-textMuted mx-auto mb-4 opacity-50" />
          <p className="text-textMuted text-lg">No policies found in the Digital Twin.</p>
        </div>
      ) : (
        <>
          <div className="flex items-center gap-4 mb-2">
            <span className="text-sm text-textMuted font-medium">
              {policies.filter(p => p.status === 'Active').length} active / {policies.length} total policies
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {policies.map((policy: any, i: number) => (
              <motion.div 
                key={policy.id} 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                className="glass-card p-6 flex items-start gap-4 group"
              >
                <div className={`p-4 rounded-xl transition-transform duration-300 group-hover:scale-110 group-hover:-rotate-3 ${policy.status === 'Active' ? 'bg-emerald-500/10' : 'bg-amber-500/10'}`}>
                  {policy.status === 'Active' ? (
                    <ShieldCheck className="w-6 h-6 text-emerald-500" />
                  ) : (
                    <ShieldAlert className="w-6 h-6 text-amber-500" />
                  )}
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <h3 className="font-bold text-xl font-display text-text group-hover:text-primary transition-colors">{policy.name}</h3>
                    <span className={`px-2 py-1 text-xs font-bold uppercase tracking-wider rounded ${severityColor(policy.severity)}`}>
                      {policy.severity}
                    </span>
                  </div>
                  <p className="text-sm text-textMuted mt-1">{policy.description}</p>
                  <div className="flex items-center gap-2 mt-3">
                    <p className="text-xs text-textMuted font-mono bg-surfaceHover inline-block px-2 py-1 rounded border border-surfaceBorder">{policy.id}</p>
                    <span className={`text-xs font-bold px-2 py-1 rounded ${policy.status === 'Active' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-amber-500/10 text-amber-500'}`}>
                      {policy.status}
                    </span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
