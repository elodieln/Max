/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'max-primary': '#007179',
        'max-secondary': '#F9BC97',
        'max-accent': '#FF914D'
      }
    },
  },
  plugins: [],
}