<script setup lang="ts">
import { useAuth } from "@/modules/auth/composables/useAuth";

import BaseButton from "@/components/base/BaseButton.vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import AppLink from "@/components/navigation/AppLink.vue";

const { user, logout, logoutLoading, logoutError } = useAuth();
</script>

<template>
  <div class="min-h-screen">
    <header class="border-b border-[var(--color-border)] bg-white/95 backdrop-blur">
      <div
        class="mx-auto flex min-h-16 max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-2 sm:px-6 lg:px-8"
      >
        <AppLink to="/" class="text-lg no-underline">Django Base</AppLink>
        <nav class="flex items-center gap-2" aria-label="Điều hướng chính">
          <AppLink to="/">Trang chính</AppLink>
          <AppLink to="/profile">Hồ sơ</AppLink>
          <BaseButton variant="ghost" size="sm" :loading="logoutLoading" @click="logout">
            Đăng xuất
          </BaseButton>
        </nav>
      </div>
    </header>

    <div v-if="logoutError" class="mx-auto max-w-6xl px-4 pt-4 sm:px-6 lg:px-8">
      <AppAlert variant="error" title="Chưa thể thu hồi phiên trên máy chủ">
        {{ logoutError }} Bạn có thể thử đăng xuất lại khi có mạng.
      </AppAlert>
    </div>

    <main class="mx-auto max-w-6xl px-4 py-8 sm:px-6 sm:py-10 lg:px-8">
      <slot :user="user" />
    </main>
  </div>
</template>
