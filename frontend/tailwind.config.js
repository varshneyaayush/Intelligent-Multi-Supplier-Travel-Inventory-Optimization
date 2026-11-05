/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        sage: {
          50: '#F4F5F2',
          100: '#E6E7E2',
          200: '#D1D3C9',
          300: '#BDBFB2',
          400: '#A5A79B', // Primary brand background
          500: '#8E9084',
          600: '#75776C',
          700: '#5C5E55',
          800: '#43443E',
          900: '#2A2B27',
        },
        cream: {
          50: '#FDFCF9',
          100: '#F8F4ED',
          200: '#F1E8DC',
          300: '#E8D2B5', // Secondary brand surface
          400: '#DEC099',
          500: '#D2AD7D',
          600: '#B89260',
          700: '#947247',
          800: '#705331',
          900: '#4C351C',
        },
        burgundy: {
          50: '#FDF2F2',
          100: '#F9DDDC',
          200: '#F2B6B4',
          300: '#E3807D',
          400: '#CB4A47',
          500: '#A82522',
          600: '#841513',
          700: '#690C0A',
          800: '#590907', // Accent brand deep burgundy
          900: '#420605',
          950: '#2C0303',
        },
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(42, 43, 39, 0.12)',
        'glass-hover': '0 12px 40px 0 rgba(42, 43, 39, 0.20)',
        'glow-burgundy': '0 0 20px -3px rgba(89, 9, 7, 0.35)',
      },
      backdropBlur: {
        'xs': '2px',
      }
    },
  },
  plugins: [],
}

