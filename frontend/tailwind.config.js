/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: 'var(--bg-background)',
        surface: 'var(--bg-surface)',
        surfaceHover: 'var(--bg-surface-hover)',
        surfaceBorder: 'var(--border-surface)',
        primary: 'var(--color-primary)',
        primaryGlow: 'rgba(59, 130, 246, 0.4)',
        accent: '#8B5CF6',
        danger: 'var(--color-danger)',
        text: 'var(--text-main)',
        textMuted: 'var(--text-muted)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Outfit', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'glow-primary': '0 0 20px rgba(59, 130, 246, 0.3)',
        'glow-accent': '0 0 20px rgba(139, 92, 246, 0.3)',
        'glow-danger': '0 0 20px rgba(239, 68, 68, 0.3)',
      }
    },
  },
  plugins: [],
}
