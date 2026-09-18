/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: "#1B2430",
          light: "#2E3B4E",
          soft: "#485469",
        },
        sage: {
          DEFAULT: "#EDEFE5",
          dark: "#DCE1CF",
          deep: "#8FA084",
        },
        amber: {
          DEFAULT: "#C97A3D",
          light: "#E3A567",
          soft: "#F3DEC3",
        },
        paper: "#FAF9F5",
      },
      fontFamily: {
        display: ["Spectral", "serif"],
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["IBM Plex Mono", "monospace"],
      },
    },
  },
  plugins: [],
}
