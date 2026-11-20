/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          "Inter",
          "system-ui",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Roboto",
          "sans-serif",
        ],
        mono: [
          '"JetBrains Mono"',
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "Monaco",
          "Consolas",
          "monospace",
        ],
      },
      colors: {
        surface: {
          DEFAULT: "#FFFFFF",
          secondary: "#FAFAFA",
        },
        border: {
          light: "#E5E7EB",
          dark: "#000000",
        },
        content: {
          primary: "#0A0A0A",
          secondary: "#52525B",
        },
      },
    },
  },
  plugins: [],
};
