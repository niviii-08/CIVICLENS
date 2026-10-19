/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        civic: {
          950: '#06070a',
          900: '#0c1017',
          850: '#111723',
          800: '#182032',
          700: '#23304a',
          600: '#334366',
          blue: '#3b82f6',
          dmk: '#ef4444',
          aiadmk: '#22c55e',
          bjp: '#f97316',
          gold: '#eab308'
        }
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      }
    },
  },
  plugins: [],
};
