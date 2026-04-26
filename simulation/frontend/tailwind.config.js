/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        'esi-green': { light: '#eaf3de', mid: '#97c459', dark: '#3b6d11' },
        'esi-amber': { light: '#faeeda', mid: '#ef9f27', dark: '#854f0b' },
        'esi-red':   { light: '#fcebeb', mid: '#e24b4a', dark: '#a32d2d' },
        'brand':     { light: '#e1f5ee', mid: '#1d9e75', dark: '#085041' },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
