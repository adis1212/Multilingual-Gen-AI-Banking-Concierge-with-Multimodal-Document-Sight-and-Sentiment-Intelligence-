/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg:       "#07090f",
        surface:  "#0e1118",
        surface2: "#141720",
        border:   "#1e2333",
        accent:   "#3b7fff",
        accent2:  "#00d4aa",
        warn:     "#ff6b35",
        critical: "#ff3355",
        gold:     "#f5c842",
        muted:    "#6b7299",
      },
      fontFamily: {
        syne: ["Syne", "sans-serif"],
        dm:   ["DM Sans", "sans-serif"],
        mono: ["DM Mono", "monospace"],
      },
    },
  },
  plugins: [],
}