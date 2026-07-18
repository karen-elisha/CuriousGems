/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0F172A', // Slate 900
        surface: 'rgba(30, 41, 59, 0.7)', // Slate 800 with opacity for glassmorphism
        surfaceBorder: 'rgba(51, 65, 85, 0.5)',
        primary: '#3B82F6', // Blue 500
        accent: '#10B981', // Emerald 500
        danger: '#EF4444', // Red 500
        text: '#F8FAFC', // Slate 50
        textMuted: '#94A3B8', // Slate 400
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
