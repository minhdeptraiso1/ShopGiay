<script setup lang="ts">
import { computed } from "vue";
import { useThemeStore } from "@/app/stores/theme";

let themeStore: ReturnType<typeof useThemeStore> | null = null;
try {
  themeStore = useThemeStore();
} catch {
  // Fallback when rendered without Pinia in unit tests
}

const isDark = computed(() => (themeStore ? themeStore.currentTheme === "dark" : true));

function handleToggle() {
  themeStore?.toggleTheme();
}
</script>

<template>
  <button
    type="button"
    class="relative flex h-9 w-9 items-center justify-center rounded-full border border-white/10 dark:border-white/10 bg-white/5 dark:bg-white/5 text-slate-300 dark:text-slate-300 hover:bg-white/10 dark:hover:bg-white/10 hover:text-white dark:hover:text-white transition-all cursor-pointer"
    :title="isDark ? 'Chuyển sang giao diện Sáng' : 'Chuyển sang giao diện Tối'"
    :aria-label="isDark ? 'Chuyển sang giao diện Sáng' : 'Chuyển sang giao diện Tối'"
    @click="handleToggle"
  >
    <!-- Sun Icon (Shown in Dark mode to switch to Light) -->
    <svg
      v-if="isDark"
      class="h-4.5 w-4.5 text-amber-400 transition-transform duration-200 hover:rotate-45"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      stroke-width="2"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
      />
    </svg>

    <!-- Moon Icon (Shown in Light mode to switch to Dark) -->
    <svg
      v-else
      class="h-4.5 w-4.5 text-indigo-600 transition-transform duration-200 hover:-rotate-12"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      stroke-width="2"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
      />
    </svg>
  </button>
</template>
