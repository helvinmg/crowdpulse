/** @type {import('tailwindcss').Config} */
const config = {
  content: [
    "./src/app/**/*.{js,jsx,mdx}",
    "./src/components/**/*.{js,jsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f0fdf4",
          100: "#dcfce7",
          200: "#bbf7d0",
          500: "#22c55e",
          600: "#16a34a",
          700: "#15803d",
          900: "#14532d",
        },
        hype: "#ef4444",
        panic: "#3b82f6",
        neutral: "#a3a3a3",
      },
    },
  },
  plugins: [],
};

module.exports = config;
