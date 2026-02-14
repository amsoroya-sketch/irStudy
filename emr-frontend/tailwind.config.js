/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Cerner theme colors
        'cerner-primary': '#3498db',
        'cerner-bg-dark': '#2c3e50',
        'cerner-bg-darker': '#1a252f',
        'cerner-success': '#27ae60',
        'cerner-error': '#e74c3c',

        // Epic theme colors
        'epic-primary': '#8b5cf6',
        'epic-primary-dark': '#7c3aed',
        'epic-bg-white': '#ffffff',
        'epic-bg-light': '#f9fafb',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['SF Mono', 'Monaco', 'Consolas', 'monospace'],
      },
    },
  },
  plugins: [],
}
