<<<<<<< HEAD
import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { motion } from 'framer-motion';
import { Activity, AlertTriangle, CheckCircle, ShieldAlert } from 'lucide-react';
=======
import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Database, AlertTriangle, CheckCircle, ShieldAlert, FileText, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import apiClient from '../api/client';
>>>>>>> 632c496 (Update frontend)

export function Dashboard() {
  const [metrics, setMetrics] = useState<any>(null);

  useEffect(() => {
    apiClient.get('/dashboard/metrics').then(res => setMetrics(res.data.data)).catch(() => {});
  }, []);

  if (!metrics) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-[var(--text-muted)] font-medium">Loading test results...</p>
      </div>
    );
  }

  const stats = [
    { title: 'Total Nodes Analyzed', value: metrics.total_nodes_analyzed?.toLocaleString() || 0, icon: Database, color: 'text-indigo-600', bg: 'bg-indigo-50 border-indigo-100' },
    { title: 'Violations Found', value: metrics.total_violations_found || 0, icon: ShieldAlert, color: 'text-red-600', bg: 'bg-red-50 border-red-100' },
    { title: 'High Risk Vendors', value: metrics.high_risk_vendors || 0, icon: AlertTriangle, color: 'text-amber-600', bg: 'bg-amber-50 border-amber-100' },
    { title: 'Test Status', value: metrics.test_status || 'Complete', icon: CheckCircle, color: 'text-emerald-600', bg: 'bg-emerald-50 border-emerald-100' },
  ];

  return (
    <div className="space-y-6">
<<<<<<< HEAD
      <header className="mb-8">
        <motion.h1 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-4xl font-bold text-text font-display tracking-tight"
        >
          Digital Twin Overview
        </motion.h1>
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="text-textMuted text-lg mt-2"
        >
          Live pulse of your financial ecosystem
        </motion.p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { title: 'Total Active Nodes', value: '1,284', icon: Activity, color: 'text-cyan-400', bg: 'bg-cyan-400/10', glow: 'shadow-glow-primary' },
          { title: 'Pending Rules', value: '12', icon: ShieldAlert, color: 'text-amber-400', bg: 'bg-amber-400/10', glow: 'shadow-[0_0_20px_rgba(251,191,36,0.3)]' },
          { title: 'High Risk Entities', value: '3', icon: AlertTriangle, color: 'text-rose-400', bg: 'bg-rose-400/10', glow: 'shadow-glow-danger' },
          { title: 'System Health', value: 'Optimal', icon: CheckCircle, color: 'text-emerald-400', bg: 'bg-emerald-400/10', glow: 'shadow-[0_0_20px_rgba(52,211,153,0.3)]' },
        ].map((stat, i) => (
          <motion.div 
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className={`glass-card p-6 group hover:${stat.glow}`}
          >
            <div className="flex items-center gap-4">
              <div className={`p-3 rounded-xl ${stat.bg} transition-transform duration-300 group-hover:scale-110 group-hover:rotate-3`}>
                <stat.icon className={`w-7 h-7 ${stat.color}`} />
              </div>
              <div>
                <p className="text-sm text-textMuted font-medium uppercase tracking-wider">{stat.title}</p>
                <h3 className="text-3xl font-bold text-text mt-1 font-display">{stat.value}</h3>
              </div>
            </div>
          </motion.div>
        ))}
=======
      <header className="mb-8 border-b border-[var(--border-surface)] pb-6">
        <h1 className="text-3xl font-bold text-[var(--text-main)] tracking-tight">Test Execution Results</h1>
        <p className="text-[var(--text-muted)] mt-1">Summary of compliance violations caught in the uploaded test case dataset.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat, i) => {
          return (
            <motion.div 
              key={stat.title}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="glass-card p-6 border-l-4"
              style={{ borderLeftColor: 'var(--color-primary)' }}
            >
              <div className="flex items-center gap-4">
                <div className={`p-3 rounded-lg border ${stat.bg}`}>
                  <stat.icon className={`w-6 h-6 ${stat.color}`} />
                </div>
                <div>
                  <p className="text-sm text-[var(--text-muted)] font-medium">{stat.title}</p>
                  <h3 className="text-2xl font-bold text-[var(--text-main)] mt-1">{stat.value}</h3>
                </div>
              </div>
            </motion.div>
          );
        })}
>>>>>>> 632c496 (Update frontend)
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div 
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
<<<<<<< HEAD
          transition={{ delay: 0.2 }}
          className="lg:col-span-2 glass-panel p-6 h-[420px] flex flex-col"
        >
          <h3 className="text-xl font-bold mb-6 font-display text-text flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-cyan-400 shadow-glow-primary"></span>
            Spend Velocity
          </h3>
          <div className="flex-1 min-h-0">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorSpend" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06B6D4" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#06B6D4" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.1)" vertical={false} />
                <XAxis dataKey="name" stroke="#94A3B8" tickLine={false} axisLine={false} dy={10} />
                <YAxis stroke="#94A3B8" tickLine={false} axisLine={false} dx={-10} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', border: '1px solid rgba(148, 163, 184, 0.2)', borderRadius: '12px', backdropFilter: 'blur(8px)' }}
                  itemStyle={{ color: '#06B6D4', fontWeight: 'bold' }}
                />
                <Area type="monotone" dataKey="spend" stroke="#06B6D4" strokeWidth={3} fillOpacity={1} fill="url(#colorSpend)" activeDot={{ r: 6, fill: '#06B6D4', stroke: '#fff', strokeWidth: 2, className: 'drop-shadow-[0_0_8px_rgba(6,182,212,0.8)]' }} />
              </AreaChart>
            </ResponsiveContainer>
=======
          className="glass-panel p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-bold text-[var(--text-main)]">Caught Violations</h3>
            <Link to="/evidence" className="text-sm font-medium text-[var(--color-primary)] hover:underline flex items-center gap-1">
              View Evidence Graphs <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
          
          <div className="space-y-4">
            {metrics.recent_violations?.length > 0 ? (
              metrics.recent_violations.map((v: any, idx: number) => (
                <div key={idx} className="p-4 border border-[var(--border-surface)] rounded-lg bg-gray-50 flex items-start gap-4">
                  <div className="p-2 bg-red-100 text-red-700 rounded border border-red-200">
                    <ShieldAlert className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="font-bold text-[var(--text-main)] text-sm">{v.policy_id}: {v.policy_name}</h4>
                    <p className="text-sm text-[var(--text-muted)] mt-1">{v.detail}</p>
                    <div className="mt-3 flex items-center gap-2">
                      <span className="px-2 py-1 bg-red-100 text-red-800 text-xs font-semibold rounded">{v.severity}</span>
                      <span className="text-xs text-[var(--text-muted)] font-mono">{v.entity_type} • {v.entity_id}</span>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-8 text-center text-[var(--text-muted)] border border-dashed border-[var(--border-surface)] rounded-lg bg-gray-50">
                No compliance violations found in this test case.
              </div>
            )}
>>>>>>> 632c496 (Update frontend)
          </div>
        </motion.div>

        <motion.div 
<<<<<<< HEAD
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-panel p-6 flex flex-col"
        >
          <h3 className="text-xl font-bold mb-6 font-display text-text flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-violet-400 shadow-glow-accent"></span>
            Recent Events
          </h3>
          <div className="space-y-4 flex-1 overflow-y-auto pr-2 custom-scrollbar">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="group flex items-start gap-3 p-3 rounded-xl hover:bg-surfaceHover border border-transparent hover:border-surfaceBorder transition-all duration-300 hover:shadow-lg hover:-translate-y-0.5 cursor-pointer">
                <div className="relative mt-1">
                  <div className={`w-2.5 h-2.5 rounded-full ${i % 2 === 0 ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]' : 'bg-cyan-400 shadow-[0_0_8px_rgba(6,182,212,0.8)]'} group-hover:scale-125 transition-transform`} />
                </div>
                <div>
                  <p className="text-sm font-medium text-text group-hover:text-cyan-300 transition-colors">Transaction TXN-100{i} Approved</p>
                  <p className="text-xs text-textMuted mt-1">{i * 2} mins ago • Auto-Rule Engine</p>
=======
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass-panel p-6"
        >
          <h3 className="text-lg font-bold text-[var(--text-main)] mb-6">Violation Distribution by Severity</h3>
          <div className="space-y-6">
            {metrics.severity_data?.map((sev: any) => (
              <div key={sev.name} className="flex items-center gap-4">
                <div className="w-24 text-sm font-semibold text-[var(--text-main)]">{sev.name}</div>
                <div className="flex-1 h-3 bg-gray-100 rounded-full overflow-hidden border border-gray-200">
                  <div 
                    className={`h-full ${sev.name === 'Critical' ? 'bg-red-600' : sev.name === 'High' ? 'bg-amber-500' : 'bg-blue-500'}`}
                    style={{ width: `${Math.max((sev.count / metrics.total_violations_found) * 100, 2)}%` }}
                  />
>>>>>>> 632c496 (Update frontend)
                </div>
                <div className="w-12 text-right text-sm font-bold text-[var(--text-muted)]">{sev.count}</div>
              </div>
            ))}
          </div>
          
          <div className="mt-8 p-6 bg-indigo-50 border border-indigo-100 rounded-xl">
            <h4 className="font-bold text-indigo-900 mb-2 flex items-center gap-2">
              <FileText className="w-5 h-5" /> Next Step: Unstructured PDF Auditing
            </h4>
            <p className="text-sm text-indigo-800 leading-relaxed mb-4">
              The deterministic engine has successfully analyzed the structured datasets. To cross-reference specific entities against unstructured evidence (e.g. Vendor Invoices), proceed to the AI Investigation tab.
            </p>
            <Link to="/investigation" className="btn-primary inline-flex">Launch AI Auditor</Link>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
