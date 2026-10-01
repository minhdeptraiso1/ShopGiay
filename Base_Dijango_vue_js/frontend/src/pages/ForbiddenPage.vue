<script setup lang="ts">
import AppLink from "@/components/navigation/AppLink.vue";
import StorefrontLayout from "@/layouts/StorefrontLayout.vue";
</script>

<template>
  <StorefrontLayout>
    <section class="mx-auto max-w-xl px-4 py-20 text-center sm:px-6">
      <p class="text-sm font-bold tracking-widest text-[var(--color-error)]">403</p>
      <h1 class="mt-3 text-3xl font-bold">Bạn không có quyền truy cập</h1>
      <p class="mt-3 text-[var(--color-text-muted)]">
        Tài khoản hiện tại không được cấp quyền cho khu vực này.
      </p>
      <p class="mt-6"><AppLink to="/">Quay lại cửa hàng</AppLink></p>
    </section>
  </StorefrontLayout>
</template>
