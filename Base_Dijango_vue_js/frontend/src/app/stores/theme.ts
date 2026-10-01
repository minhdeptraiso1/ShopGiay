import { defineStore } from "pinia";
import { ref } from "vue";

export type ThemeMode = "dark" | "light";

const THEME_STORAGE_KEY = "hd_theme_mode";

export const useThemeStore = defineStore("theme", () => {
  const initialTheme = (typeof localStorage !== "undefined" &&
    localStorage.getItem(THEME_STORAGE_KEY) === "light")
    ? "light"
    : "dark";

  const currentTheme = ref<ThemeMode>(initialTheme);

  function applyTheme(theme: ThemeMode) {
    currentTheme.value = theme;
    if (typeof document !== "undefined") {
      const root = document.documentElement;
      root.classList.remove("dark", "light");
      root.classList.add(theme);
      root.setAttribute("data-theme", theme);
      localStorage.setItem(THEME_STORAGE_KEY, theme);
    }
  }

  function toggleTheme() {
    const next = currentTheme.value === "dark" ? "light" : "dark";
    applyTheme(next);
  }

  function initTheme() {
    applyTheme(currentTheme.value);
  }

  return { currentTheme, toggleTheme, applyTheme, initTheme };
});
