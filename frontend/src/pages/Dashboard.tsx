import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { motion } from 'framer-motion';
import { Activity, AlertTriangle, CheckCircle, ShieldAlert } from 'lucide-react';

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
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
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
          </div>
        </motion.div>

        <motion.div 
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
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
