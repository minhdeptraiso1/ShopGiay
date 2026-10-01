<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";

import AppLink from "@/components/navigation/AppLink.vue";
import { fetchBanners } from "../api";
import type { Banner } from "../types";

const props = defineProps<{ position: Banner["position"] }>();
const banners = ref<Banner[]>([]);
const activeIndex = ref(0);
let timer: ReturnType<typeof globalThis.setInterval> | undefined;
const activeBanner = computed(() => banners.value[activeIndex.value] ?? null);

function goTo(index: number): void {
  activeIndex.value = index;
}

function startRotation(): void {
  if (banners.value.length < 2 || globalThis.matchMedia("(prefers-reduced-motion: reduce)").matches)
    return;
  timer = globalThis.setInterval(() => {
    activeIndex.value = (activeIndex.value + 1) % banners.value.length;
  }, 7000);
}

onMounted(async () => {
  try {
    banners.value = await fetchBanners(props.position);
    startRotation();
  } catch {
    banners.value = [];
  }
});

onBeforeUnmount(() => {
  if (timer) globalThis.clearInterval(timer);
});
</script>

<template>
  <section v-if="banners.length" class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
    <div v-if="activeBanner" class="relative">
      <Transition name="banner-fade" mode="out-in">
        <AppLink
          :key="activeBanner.id"
          :to="activeBanner.target_url || '/products'"
          class="group relative block min-h-40 overflow-hidden rounded-3xl border border-white/10 bg-[#12151e] no-underline"
        >
          <img
            :src="activeBanner.image_url"
            :alt="activeBanner.title"
            class="absolute inset-0 h-full w-full object-cover opacity-55 transition duration-700 group-hover:scale-[1.02] group-hover:opacity-65"
          />
          <span
            class="absolute inset-0 bg-gradient-to-r from-black/90 via-black/50 to-transparent"
          />
          <span class="relative z-10 flex min-h-40 max-w-xl flex-col justify-center p-6 sm:p-8">
            <span class="text-xl font-black text-white sm:text-2xl">{{ activeBanner.title }}</span>
            <span
              v-if="activeBanner.subtitle"
              class="mt-2 text-sm leading-relaxed text-slate-200"
              >{{ activeBanner.subtitle }}</span
            >
          </span>
        </AppLink>
      </Transition>
      <div
        v-if="banners.length > 1"
        class="mt-3 flex justify-center gap-2"
        aria-label="Chọn banner"
      >
        <button
          v-for="(banner, index) in banners"
          :key="banner.id"
          type="button"
          class="h-2 rounded-full transition-all"
          :class="
            index === activeIndex ? 'w-8 bg-emerald-400' : 'w-2 bg-slate-600 hover:bg-slate-400'
          "
          :aria-label="`Hiển thị banner ${String(index + 1)}`"
          :aria-current="index === activeIndex ? 'true' : undefined"
          @click="goTo(index)"
        />
      </div>
    </div>
  </section>
</template>

<style scoped>
.banner-fade-enter-active,
.banner-fade-leave-active {
  transition: opacity 0.7s ease;
}
.banner-fade-enter-from,
.banner-fade-leave-to {
  opacity: 0;
}
</style>
