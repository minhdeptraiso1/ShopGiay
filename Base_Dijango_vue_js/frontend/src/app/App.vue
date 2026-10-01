<script setup lang="ts">
import { onMounted } from "vue";
import AppToast from "@/components/feedback/AppToast.vue";
import { useThemeStore } from "@/app/stores/theme";

const themeStore = useThemeStore();

onMounted(() => {
  themeStore.initTheme();
});
</script>

<template>
  <RouterView />
  <AppToast />
</template>
