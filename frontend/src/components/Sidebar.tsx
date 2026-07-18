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
    <div className="w-64 h-screen glass-panel flex flex-col fixed left-0 top-0 z-50">
      <div className="p-6 border-b border-surfaceBorder flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
          <BrainCircuit className="text-white w-5 h-5" />
        </div>
        <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400">
          VeriGem
        </h1>
      </div>
      
      <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 ${
                isActive 
                  ? 'bg-primary/20 text-blue-400 border border-primary/30 shadow-lg shadow-primary/10' 
                  : 'text-textMuted hover:bg-surfaceBorder/50 hover:text-text'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <item.icon className={`w-5 h-5 ${isActive ? 'text-blue-400' : ''}`} />
                <span className="font-medium">{item.label}</span>
                {isActive && (
                  <motion.div
                    layoutId="sidebar-active"
                    className="absolute left-0 w-1 h-8 bg-blue-500 rounded-r-full"
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
      
      <div className="p-4 border-t border-surfaceBorder">
        <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-slate-800/50">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-sm text-textMuted font-medium">Digital Twin: Active</span>
        </div>
      </div>
    </div>
  );
}
