<script setup lang="ts">
import AppLink from "@/components/navigation/AppLink.vue";
</script>

<template>
  <main class="grid min-h-screen place-items-center px-4 text-center">
    <section>
      <p class="text-sm font-semibold text-[var(--color-primary)]">Lỗi 404</p>
      <h1 class="mt-2 text-4xl font-bold tracking-tight">Không tìm thấy trang</h1>
      <p class="mt-3 text-[var(--color-text-muted)]">Địa chỉ bạn truy cập không tồn tại.</p>
      <AppLink to="/" class="mt-6 inline-block">Về trang chính</AppLink>
    </section>
  </main>
</template>
