/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gold: {
          50:  '#fdf9ee',
          100: '#f7edcc',
          200: '#eed897',
          300: '#e4be5c',
          400: '#d4a017',
          500: '#b8860b',
          600: '#9a6f0a',
          700: '#7a550b',
          800: '#63430e',
          900: '#523710',
        },
        ivory: '#f8f5f0',
      },
      fontFamily: {
        sans: [
          'Noto Sans JP',
          'Hiragino Kaku Gothic ProN',
          'Hiragino Sans',
          'Meiryo',
          'sans-serif',
        ],
      },
    },
  },
  plugins: [],
}

