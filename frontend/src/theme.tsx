import { createSystem, defaultConfig } from "@chakra-ui/react"
import { buttonRecipe } from "./theme/button.recipe"

export const system = createSystem(defaultConfig, {
  globalCss: {
    html: {
      fontSize: "16px",
    },
    body: {
      fontSize: "0.875rem",
      margin: 0,
      padding: 0,
      bg: "var(--chakra-colors-chakra-body-bg)",
      color: "var(--chakra-colors-chakra-text-color)",
    },
    ".main-link": {
      color: "ui.main",
      fontWeight: "bold",
    },
    "::-webkit-scrollbar": {
      height: "8px",
      width: "0px",
    },
    "::-webkit-scrollbar-track": {
      background: "var(--chakra-colors-gray-100)",
      borderRadius: "4px",
      _dark: {
        background: "var(--chakra-colors-gray-700)",
      },
    },
    "::-webkit-scrollbar-thumb": {
      background: "var(--chakra-colors-gray-300)",
      borderRadius: "4px",
      _hover: {
        background: "var(--chakra-colors-gray-400)",
      },
      _dark: {
        background: "var(--chakra-colors-gray-600)",
        _hover: {
          background: "var(--chakra-colors-gray-500)",
        },
      },
    },
  },
  theme: {
    tokens: {
      colors: {
        ui: {
          main: { value: "#009688" },
        },
        pastel: {
          blue: { value: "#B5D8F7" },
          green: { value: "#B5E6D8" },
          purple: { value: "#E6D8F7" },
          yellow: { value: "#F7E6B5" },
          red: { value: "#F7B5B5" },
          gray: { value: "#E6E6E6" },
        },
      },
    },
    recipes: {
      button: buttonRecipe,
    },
  },
})
