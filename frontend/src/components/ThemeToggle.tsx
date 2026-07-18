import { Sun, Moon } from 'lucide-react';
import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

export function ThemeToggle() {
  const [dark, setDark] = useState(() => {
    const stored = localStorage.getItem('verigem-theme');
    if (stored) return stored === 'dark';
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    const root = document.documentElement;
    if (dark) {
      root.classList.add('dark');
      localStorage.setItem('verigem-theme', 'dark');
    } else {
      root.classList.remove('dark');
      localStorage.setItem('verigem-theme', 'light');
    }
  }, [dark]);

  return (
    <motion.button
      whileTap={{ scale: 0.9 }}
      onClick={() => setDark(!dark)}
      className="relative p-2.5 rounded-xl bg-surfaceHover border border-surfaceBorder hover:border-primary/40 transition-all duration-300 group"
      aria-label={dark ? 'Switch to light mode' : 'Switch to dark mode'}
      id="theme-toggle-btn"
    >
      <motion.div
        key={dark ? 'moon' : 'sun'}
        initial={{ rotate: -90, opacity: 0, scale: 0.5 }}
        animate={{ rotate: 0, opacity: 1, scale: 1 }}
        exit={{ rotate: 90, opacity: 0, scale: 0.5 }}
        transition={{ duration: 0.3 }}
      >
        {dark ? (
          <Moon className="w-5 h-5 text-violet-400 drop-shadow-[0_0_8px_rgba(139,92,246,0.8)] group-hover:scale-110 transition-transform" />
        ) : (
          <Sun className="w-5 h-5 text-amber-400 drop-shadow-[0_0_8px_rgba(251,191,36,0.8)] group-hover:scale-110 transition-transform" />
        )}
      </motion.div>
    </motion.button>
  );
}
