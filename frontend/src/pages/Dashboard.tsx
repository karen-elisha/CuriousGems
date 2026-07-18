import React, { useEffect, useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { motion } from 'framer-motion';
import { Activity, AlertTriangle, CheckCircle, ShieldAlert } from 'lucide-react';
import apiClient from '../api/client';

const data = [
  { name: 'Jan', spend: 4000 },
  { name: 'Feb', spend: 3000 },
  { name: 'Mar', spend: 2000 },
  { name: 'Apr', spend: 2780 },
  { name: 'May', spend: 1890 },
  { name: 'Jun', spend: 2390 },
  { name: 'Jul', spend: 3490 },
];

export function Dashboard() {
  return (
    <div className="space-y-6">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-text">Digital Twin Overview</h1>
        <p className="text-textMuted">Live pulse of your financial ecosystem</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { title: 'Total Active Nodes', value: '1,284', icon: Activity, color: 'text-blue-400', bg: 'bg-blue-400/10' },
          { title: 'Pending Rules', value: '12', icon: ShieldAlert, color: 'text-amber-400', bg: 'bg-amber-400/10' },
          { title: 'High Risk Entities', value: '3', icon: AlertTriangle, color: 'text-red-400', bg: 'bg-red-400/10' },
          { title: 'System Health', value: 'Optimal', icon: CheckCircle, color: 'text-emerald-400', bg: 'bg-emerald-400/10' },
        ].map((stat, i) => (
          <motion.div 
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="glass-card p-6"
          >
            <div className="flex items-center gap-4">
              <div className={`p-3 rounded-xl ${stat.bg}`}>
                <stat.icon className={`w-6 h-6 ${stat.color}`} />
              </div>
              <div>
                <p className="text-sm text-textMuted font-medium">{stat.title}</p>
                <h3 className="text-2xl font-bold text-text mt-1">{stat.value}</h3>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="lg:col-span-2 glass-panel p-6 h-[400px]"
        >
          <h3 className="text-lg font-bold mb-4">Spend Velocity</h3>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data}>
              <defs>
                <linearGradient id="colorSpend" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
              <XAxis dataKey="name" stroke="#94A3B8" />
              <YAxis stroke="#94A3B8" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1E293B', border: '1px solid #334155', borderRadius: '8px' }}
              />
              <Area type="monotone" dataKey="spend" stroke="#3B82F6" strokeWidth={3} fillOpacity={1} fill="url(#colorSpend)" />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="glass-panel p-6"
        >
          <h3 className="text-lg font-bold mb-4">Recent Events</h3>
          <div className="space-y-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="flex items-start gap-3 p-3 rounded-lg hover:bg-slate-800/50 transition-colors">
                <div className="w-2 h-2 rounded-full bg-emerald-500 mt-2" />
                <div>
                  <p className="text-sm font-medium">Transaction TXN-100{i} Approved</p>
                  <p className="text-xs text-textMuted mt-1">2 mins ago • Auto-Rule Engine</p>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
