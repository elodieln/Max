/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
      "./index.html",
      "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
      extend: {
        colors: {
          'max-primary': 'rgb(0, 113, 121)',
          'max-background': 'rgb(65, 113, 121)',
        },
      },
    },
    plugins: [],
  }