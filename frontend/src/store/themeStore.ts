import { defineStore } from "pinia";
import { ref, watch } from "vue";

export const useThemeStore = defineStore("theme", () => {
  // Blanc par defaut si aucune preference sauvegardee
  const isDark = ref(localStorage.getItem("theme") === "dark");

  const apply = () => {
    if (isDark.value) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
    localStorage.setItem("theme", isDark.value ? "dark" : "light");
  };

  const toggle = () => {
    isDark.value = !isDark.value;
  };

  // Appliquer au chargement
  apply();

  // Appliquer a chaque changement
  watch(isDark, apply);

  return { isDark, toggle };
});
