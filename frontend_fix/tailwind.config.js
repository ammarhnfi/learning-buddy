/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class', // Ini penting untuk theme toggle kita
  theme: {
    extend: {},
  },
  plugins: [],
}