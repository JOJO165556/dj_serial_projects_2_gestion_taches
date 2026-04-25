import { defineStore } from "pinia";
import { ref, watch } from "vue";

export const useThemeStore = defineStore("theme", () => {
  const savedTheme = localStorage.getItem("theme");
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  const isDark = ref(savedTheme ? savedTheme === "dark" : prefersDark);

  const apply = () => {
    if (isDark.value) {
      document.documentElement.classList.add("dark");
      document.documentElement.style.colorScheme = "dark";
    } else {
      document.documentElement.classList.remove("dark");
      document.documentElement.style.colorScheme = "light";
    }
    localStorage.setItem("theme", isDark.value ? "dark" : "light");
  };

  const toggle = () => {
    isDark.value = !isDark.value;
  };

  apply();
  watch(isDark, apply);

  return { isDark, toggle };
});
