<script setup lang="ts">
import AppLogo from "@/components/common/AppLogo.vue";
import ThemeToggle from "@/components/common/ThemeToggle.vue";
import AppLink from "@/components/navigation/AppLink.vue";
</script>

<template>
  <main class="relative isolate flex min-h-screen flex-col items-center justify-center overflow-hidden bg-[#090a0f] px-4 py-12 text-white sm:px-6">
    <!-- Floating Theme Toggle & Home Action -->
    <div class="absolute top-4 right-4 z-30 flex items-center gap-2 sm:gap-3">
      <ThemeToggle />
    </div>

    <!-- Studio Ambient Radial Glow -->
    <div
      class="pointer-events-none absolute inset-0 opacity-40"
      style="background: radial-gradient(circle at 50% 25%, rgba(16, 185, 129, 0.16), transparent 60%), radial-gradient(circle at 80% 80%, rgba(56, 189, 248, 0.06), transparent 50%);"
      aria-hidden="true"
    />

    <!-- Brand Header with Monogram Logo -->
    <header class="relative z-10 mb-8 flex flex-col items-center text-center">
      <AppLink to="/" class="transition-transform duration-200 hover:scale-105 no-underline" aria-label="Trang chủ Hải Duy Shop">
        <AppLogo />
      </AppLink>
    </header>

    <!-- Auth Card -->
    <section
      class="auth-card auth-theme relative z-10 w-full max-w-md rounded-3xl border border-white/10 bg-[#12151e]/90 p-6 shadow-[0_25px_60px_-15px_rgba(0,0,0,0.9)] backdrop-blur-xl sm:p-8"
    >
      <header class="mb-6">
        <h1 class="text-2xl font-black tracking-tight text-white uppercase sm:text-3xl">
          <slot name="title" />
        </h1>
        <p class="mt-2 text-sm text-slate-400">
          <slot name="subtitle" />
        </p>
      </header>
      <slot />
    </section>

    <!-- Footer Copyright -->
    <footer class="relative z-10 mt-8 text-center text-xs text-slate-500">
      <p>© 2026 HẢI DUY SHOP • Thương hiệu sneaker & streetwear chính hãng</p>
    </footer>
  </main>
</template>
