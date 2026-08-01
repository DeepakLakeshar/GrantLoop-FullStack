/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Primary (navy) — main brand/action color
        "primary": "#002045",
        "on-primary": "#ffffff",
        "primary-container": "#1a365d",
        "on-primary-container": "#86a0cd",
        "primary-fixed": "#d6e3ff",
        "primary-fixed-dim": "#adc7f7",
        "on-primary-fixed": "#001b3c",
        "on-primary-fixed-variant": "#2d476f",

        // Secondary (green) — verification/success/accountability
        "secondary": "#2c694e",
        "on-secondary": "#ffffff",
        "secondary-container": "#aeeecb",
        "on-secondary-container": "#316e52",
        "secondary-fixed": "#b1f0ce",
        "secondary-fixed-dim": "#95d4b3",
        "on-secondary-fixed": "#002114",
        "on-secondary-fixed-variant": "#0e5138",

        // Tertiary — rarely used, neutral dark accent
        "tertiary": "#1d2123",
        "on-tertiary": "#ffffff",
        "tertiary-container": "#333638",
        "on-tertiary-container": "#9c9fa1",
        "tertiary-fixed": "#e0e3e5",
        "tertiary-fixed-dim": "#c4c7c9",
        "on-tertiary-fixed": "#191c1e",
        "on-tertiary-fixed-variant": "#444749",

        // Error
        "error": "#ba1a1a",
        "on-error": "#ffffff",
        "error-container": "#ffdad6",
        "on-error-container": "#93000a",

        // Surfaces (backgrounds, cards, elevation levels)
        "background": "#f9f9ff",
        "on-background": "#111c2c",
        "surface": "#f9f9ff",
        "surface-dim": "#cfdaf1",
        "surface-bright": "#f9f9ff",
        "surface-container-lowest": "#ffffff",
        "surface-container-low": "#f0f3ff",
        "surface-container": "#e7eeff",
        "surface-container-high": "#dee8ff",
        "surface-container-highest": "#d8e3fa",
        "surface-variant": "#d8e3fa",
        "surface-tint": "#455f88",
        "on-surface": "#111c2c",
        "on-surface-variant": "#43474e",

        // Outlines
        "outline": "#74777f",
        "outline-variant": "#c4c6cf",

        // Inverse (for dark-on-light callout cards)
        "inverse-surface": "#263142",
        "inverse-on-surface": "#ebf1ff",
        "inverse-primary": "#adc7f7",
      },
      borderRadius: {
        DEFAULT: "0.125rem", // 2px — inputs, table cells
        lg: "0.25rem",       // 4px — buttons, small cards
        xl: "0.5rem",        // 8px — cards, panels
        full: "0.75rem",     // 12px — NOTE: not a true pill despite the name;
                             // this codebase uses it for "large rounded" cards
      },
      spacing: {
        baseline: "4px",
        "margin-mobile": "16px",
        "container-max": "1280px",
        "margin-desktop": "48px",
        gutter: "24px",
      },
      fontFamily: {
        "headline-sm": ["Manrope"],
        "headline-md": ["Manrope"],
        "headline-lg": ["Manrope"],
        "body-md": ["Inter"],
        "body-lg": ["Inter"],
        "data-table": ["Inter"],
        "label-caps": ["JetBrains Mono"],
      },
      fontSize: {
        "headline-sm": ["20px", { lineHeight: "28px", fontWeight: "600" }],
        "headline-md": ["28px", { lineHeight: "36px", letterSpacing: "-0.01em", fontWeight: "600" }],
        "headline-lg": ["40px", { lineHeight: "48px", letterSpacing: "-0.02em", fontWeight: "700" }],
        "body-md": ["16px", { lineHeight: "24px", fontWeight: "400" }],
        "body-lg": ["18px", { lineHeight: "28px", fontWeight: "400" }],
        "data-table": ["14px", { lineHeight: "20px", fontWeight: "500" }],
        "label-caps": ["12px", { lineHeight: "16px", letterSpacing: "0.05em", fontWeight: "500" }],
      },
    },
  },
  plugins: [
    require("@tailwindcss/forms"),
    require("@tailwindcss/container-queries"),
  ],
};
