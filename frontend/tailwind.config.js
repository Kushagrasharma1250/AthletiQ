/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        industrial: {
          900: '#0b0f19',
          800: '#111827',
          700: '#1f2937',
          600: '#374151',
          border: '#1f293d',
        },
        fire: {
          red: '#ef4444',
          orange: '#f97316',
          amber: '#f59e0b',
          purple: '#a855f7',
        }
      }
    },
  },
  plugins: [],
}
