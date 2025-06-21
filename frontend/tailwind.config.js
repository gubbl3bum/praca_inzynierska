/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      // Dodane: line-clamp utilities
      lineClamp: {
        1: '1',
        2: '2',
        3: '3',
      }
    },
  },
  plugins: [
    // Dodaj plugin dla line-clamp jeśli jest dostępny
    require('@tailwindcss/line-clamp'),
  ],
}
