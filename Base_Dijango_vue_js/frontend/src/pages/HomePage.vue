<script setup lang="ts">
import { storeToRefs } from "pinia";

import AppLink from "@/components/navigation/AppLink.vue";
import AppLayout from "@/layouts/AppLayout.vue";
import { useAuthStore } from "@/modules/auth/stores/auth";

const auth = useAuthStore();
const { user } = storeToRefs(auth);
</script>

<template>
  <AppLayout>
    <section class="space-y-6">
      <div>
        <p class="text-sm font-semibold text-[var(--color-primary)]">Tổng quan tài khoản</p>
        <h1 class="mt-1 text-3xl font-bold tracking-tight sm:text-4xl">
          Xin chào, {{ user?.full_name || user?.email }}
        </h1>
        <p class="mt-3 max-w-2xl text-[var(--color-text-muted)]">
          Phiên hiện tại đang dùng access token trong bộ nhớ và refresh token HttpOnly do máy chủ
          quản lý.
        </p>
      </div>

      <dl
        class="grid gap-4 rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-white p-5 shadow-[var(--shadow-surface)] sm:grid-cols-2 sm:p-6"
      >
        <div>
          <dt class="text-sm font-medium text-[var(--color-text-muted)]">Email</dt>
          <dd class="mt-1 break-all font-semibold">{{ user?.email }}</dd>
        </div>
        <div>
          <dt class="text-sm font-medium text-[var(--color-text-muted)]">Họ và tên</dt>
          <dd class="mt-1 font-semibold">{{ user?.full_name || "Chưa cập nhật" }}</dd>
        </div>
      </dl>

      <AppLink to="/profile">Cập nhật hồ sơ</AppLink>
    </section>
  </AppLayout>
</template>
