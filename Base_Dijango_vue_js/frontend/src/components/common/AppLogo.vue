<script setup lang="ts">
import { computed } from "vue";
import { useThemeStore } from "@/app/stores/theme";

interface Props {
  size?: "sm" | "md" | "lg";
  theme?: "light" | "dark" | "auto";
}

const props = withDefaults(defineProps<Props>(), {
  size: "md",
  theme: "auto",
});

let themeStore: ReturnType<typeof useThemeStore> | null = null;
try {
  themeStore = useThemeStore();
} catch {
  // Fallback when rendered without Pinia in unit tests
}

const effectiveTheme = computed(() => {
  if (props.theme === "auto") {
    return themeStore?.currentTheme || "dark";
  }
  return props.theme;
});
</script>

<template>
  <div class="inline-flex shrink-0 items-center gap-2.5 font-sans select-none tracking-tight min-w-max">
    <!-- Clean, Sharp Geometric "HD" Athletic Monogram SVG -->
    <svg
      :class="[
        'shrink-0 transition-transform duration-200 hover:scale-105',
        size === 'sm' ? 'h-7 w-7' : size === 'lg' ? 'h-10 w-10' : 'h-8 w-8',
        effectiveTheme === 'light' ? 'text-slate-900' : 'text-white',
      ]"
      viewBox="0 0 40 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <!-- "H" Left Leg and Crossbar with Dynamic Cut -->
      <path
        d="M6 8H11V18H20V8H25V32H20V23H11V32H6V8Z"
        fill="currentColor"
      />
      <!-- "D" Right Curve with Sleek Geometric Chamfer and Emerald Speed Accent -->
      <path
        d="M26 8H31C35.4183 8 38.5 11.5817 38.5 16V24C38.5 28.4183 35.4183 32 31 32H26V8ZM31 27C33.2091 27 34 25.2091 34 23V17C34 14.7909 33.2091 13 31 13H30V27H31Z"
        fill="#10B981"
      />
    </svg>

    <!-- Brand Typography (Single horizontal line, never broken) -->
    <div class="flex items-center gap-1.5 whitespace-nowrap">
      <span
        :class="[
          'font-black tracking-tight uppercase transition-colors',
          size === 'sm' ? 'text-base' : size === 'lg' ? 'text-2xl' : 'text-lg',
          effectiveTheme === 'light' ? 'text-slate-900' : 'text-white',
        ]"
      >
        HẢI DUY
      </span>
      <span
        class="text-[11px] font-extrabold tracking-widest text-emerald-400 uppercase"
      >
        SHOP
      </span>
    </div>
  </div>
</template>
