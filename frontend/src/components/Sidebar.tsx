import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Network, 
  GitBranch, 
  Search, 
  BrainCircuit,
  FileText,
  ListOrdered,
  ShieldCheck
} from 'lucide-react';
import { motion } from 'framer-motion';

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/explorer', icon: Network, label: 'Digital Twin Explorer' },
  { path: '/simulation', icon: GitBranch, label: 'Simulation Lab' },
  { path: '/evidence', icon: Search, label: 'Evidence Graph' },
  { path: '/investigation', icon: BrainCircuit, label: 'AI Investigation' },
  { path: '/reports', icon: FileText, label: 'Reports' },
  { path: '/transactions', icon: ListOrdered, label: 'Transactions' },
  { path: '/policies', icon: ShieldCheck, label: 'Policies' },
];

export function Sidebar() {
  return (
<<<<<<< HEAD
    <div className="w-64 h-screen bg-surface/80 backdrop-blur-2xl border-r border-surfaceBorder flex flex-col fixed left-0 top-0 z-50 shadow-[4px_0_24px_rgba(0,0,0,0.2)]">
      <div className="p-6 border-b border-surfaceBorder flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center shadow-glow-primary">
          <BrainCircuit className="text-white w-5 h-5" />
        </div>
        <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-blue-500 to-violet-500 font-display tracking-tight">
=======
    <div className="w-64 h-screen bg-[var(--bg-surface)] border-r border-[var(--border-surface)] flex flex-col fixed left-0 top-0 z-50">
      <div className="p-6 border-b border-[var(--border-surface)] flex items-center gap-3">
        <div className="w-8 h-8 rounded bg-[var(--color-primary)] flex items-center justify-center">
          <BrainCircuit className="text-white w-5 h-5" />
        </div>
        <h1 className="text-xl font-bold text-[var(--text-main)] tracking-tight">
>>>>>>> 632c496 (Update frontend)
          VeriGem
        </h1>
      </div>
      
<<<<<<< HEAD
      <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
        {navItems.map((item, index) => (
          <motion.div
            key={item.path}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.05 }}
          >
            <NavLink
              to={item.path}
              className={({ isActive }) =>
                `group relative flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 ${
                  isActive 
                    ? 'bg-primary/10 text-cyan-400 border border-primary/20 shadow-[inset_0_0_20px_rgba(6,182,212,0.1)]' 
                    : 'text-textMuted hover:bg-surfaceHover hover:text-text hover:-translate-y-0.5'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <item.icon className={`w-5 h-5 transition-transform duration-300 group-hover:scale-110 ${isActive ? 'text-cyan-400' : 'group-hover:text-cyan-300'}`} />
                  <span className="font-medium tracking-wide">{item.label}</span>
                  {isActive && (
                    <motion.div
                      layoutId="sidebar-active"
                      className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-cyan-400 rounded-r-full shadow-[0_0_10px_rgba(6,182,212,0.8)]"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ duration: 0.3 }}
                    />
                  )}
                </>
              )}
            </NavLink>
          </motion.div>
        ))}
      </nav>
      
      <div className="p-4 border-t border-surfaceBorder bg-background/30 backdrop-blur-md">
        <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-surfaceHover border border-surfaceBorder shadow-inner">
          <div className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500 shadow-[0_0_8px_rgba(6,182,212,0.8)]"></span>
          </div>
          <span className="text-sm text-text font-medium tracking-wide">Digital Twin: Active</span>
=======
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors text-sm ${
                isActive 
                  ? 'bg-gray-100 text-[var(--color-primary)] font-semibold' 
                  : 'text-[var(--text-muted)] hover:bg-gray-50 hover:text-[var(--text-main)]'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <item.icon className={`w-4 h-4 ${isActive ? 'text-[var(--color-primary)]' : ''}`} />
                <span>{item.label}</span>
                {isActive && (
                  <motion.div
                    layoutId="sidebar-active"
                    className="absolute left-0 w-1 h-6 bg-[var(--color-primary)] rounded-r"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.2 }}
                  />
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>
      
      <div className="p-4 border-t border-[var(--border-surface)]">
        <div className="flex items-center gap-3 px-3 py-2 rounded bg-gray-50 border border-[var(--border-surface)]">
          <div className="w-2 h-2 rounded-full bg-emerald-500" />
          <span className="text-xs text-[var(--text-main)] font-medium">Test Environment</span>
>>>>>>> 632c496 (Update frontend)
        </div>
      </div>
    </div>
  );
}
