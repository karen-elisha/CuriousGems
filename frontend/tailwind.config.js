/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#070B14', // Very deep blue-black
        surface: 'rgba(15, 23, 42, 0.4)', // Ultra-transparent slate for glass
        surfaceHover: 'rgba(30, 41, 59, 0.6)',
        surfaceBorder: 'rgba(148, 163, 184, 0.1)',
        primary: '#06B6D4', // Cyan 500
        primaryGlow: 'rgba(6, 182, 212, 0.5)',
        accent: '#8B5CF6', // Violet 500
        danger: '#F43F5E', // Rose 500
        text: '#F8FAFC',
        textMuted: '#94A3B8',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Outfit', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'glow-primary': '0 0 20px rgba(6, 182, 212, 0.3)',
        'glow-accent': '0 0 20px rgba(139, 92, 246, 0.3)',
        'glow-danger': '0 0 20px rgba(244, 63, 94, 0.3)',
      }
    },
  },
  plugins: [],
}
