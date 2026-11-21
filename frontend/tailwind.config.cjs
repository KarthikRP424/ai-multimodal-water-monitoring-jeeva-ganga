// tailwind.config.cjs
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#001F3F", // deep midnight navy
        secondary: "#0A2F5B", // dark blue
        accentCyan: "#00FFFF", // electric cyan
        accentAqua: "#7FFFD4", // aqua blue
        accentEmerald: "#50C878", // emerald green
        warning: "#FFBF00", // amber
        critical: "#FF4136", // red
      },
    },
  },
  plugins: [],
};
