/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./App.{js,ts,tsx}', './components/**/*.{js,ts,tsx}'],

  presets: [require('nativewind/preset')],
  theme: {
    extend: {
      colors: {
        whiteVar: "fff",
        avocado: "#64a12d",
        avocadoText: "#899B21",
        lightgreenbg: "#E9F0E2",
        darkgreentext: "#384728",
        yellowish: "#D1CF69",
        newBackground: "#6FCF97",
        newDarkText: "#0B9A47"
      },
      fontFamily: {
        'roboto': ['Roboto', 'sans-serif']
      }
    },
  },
  plugins: [],
};
