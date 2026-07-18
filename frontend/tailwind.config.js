/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#F8FAFC', // Slate 50
        surface: 'rgba(255, 255, 255, 0.7)', // Translucent white for glass
        surfaceHover: 'rgba(241, 245, 249, 0.8)', // Slate 100
        surfaceBorder: 'rgba(203, 213, 225, 0.4)', // Slate 300
        primary: '#3B82F6', // Blue 500
        primaryGlow: 'rgba(59, 130, 246, 0.4)',
        accent: '#8B5CF6', // Violet 500
        danger: '#EF4444', // Red 500
        text: '#0F172A', // Slate 900
        textMuted: '#64748B', // Slate 500
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
