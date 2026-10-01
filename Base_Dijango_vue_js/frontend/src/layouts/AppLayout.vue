<script setup lang="ts">
import { ref } from "vue";
import { useRoute } from "vue-router";

import BaseButton from "@/components/base/BaseButton.vue";
import AppLogo from "@/components/common/AppLogo.vue";
import ThemeToggle from "@/components/common/ThemeToggle.vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import AppPopup from "@/components/feedback/AppPopup.vue";
import AppLink from "@/components/navigation/AppLink.vue";
import { useAuth } from "@/modules/auth/composables/useAuth";

const route = useRoute();
const { user, logout, logoutLoading, logoutError } = useAuth();
const showLogoutConfirm = ref(false);

function triggerLogout() {
  showLogoutConfirm.value = true;
}

async function confirmLogout() {
  await logout();
  showLogoutConfirm.value = false;
}
</script>

<template>
  <div class="min-h-screen bg-[#090a0f] text-slate-100 relative selection:bg-emerald-500 selection:text-black">
    <!-- Ambient Studio Lighting -->
    <div
      aria-hidden="true"
      class="pointer-events-none fixed inset-0 overflow-hidden"
    >
      <div
        class="absolute -top-40 left-1/2 -translate-x-1/2 w-[750px] h-[500px] rounded-full bg-gradient-to-b from-emerald-500/10 via-emerald-600/5 to-transparent blur-3xl"
      />
      <div
        class="absolute top-1/3 -right-40 w-[450px] h-[450px] rounded-full bg-blue-600/5 blur-3xl"
      />
    </div>

    <a
      href="#account-content"
      class="sr-only z-50 rounded-xl bg-emerald-400 px-4 py-2 font-bold text-black focus:not-sr-only focus:fixed focus:top-4 focus:left-4 shadow-xl"
    >
      Chuyển đến nội dung chính
    </a>

    <!-- Top Athletic Header -->
    <header class="relative z-30 border-b border-white/10 bg-[#0c0e17]/85 backdrop-blur-xl">
      <div
        class="mx-auto flex min-h-18 max-w-6xl items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8"
      >
        <!-- Store Brand Logo -->
        <AppLink to="/" class="no-underline transition-transform hover:scale-[1.02]">
          <AppLogo theme="dark" />
        </AppLink>

        <!-- Navigation & User Profile -->
        <div class="flex items-center gap-2 sm:gap-3">
          <nav class="flex items-center gap-1 sm:gap-1.5" aria-label="Điều hướng chính">
            <AppLink
              to="/profile"
              :class="[
                'rounded-xl px-3 py-2 text-xs sm:text-sm font-bold uppercase tracking-wider no-underline transition-all',
                route.path === '/profile'
                  ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                  : 'text-slate-300 hover:bg-white/10 hover:text-white'
              ]"
            >
              Hồ sơ
            </AppLink>
            <AppLink
              to="/orders"
              :class="[
                'rounded-xl px-3 py-2 text-xs sm:text-sm font-bold uppercase tracking-wider no-underline transition-all',
                route.path.startsWith('/orders')
                  ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                  : 'text-slate-300 hover:bg-white/10 hover:text-white'
              ]"
            >
              Đơn hàng
            </AppLink>
            <AppLink
              v-if="user?.roles?.includes('ADMIN') || user?.roles?.includes('STAFF')"
              to="/admin"
              :class="[
                'rounded-xl px-3 py-2 text-xs sm:text-sm font-bold uppercase tracking-wider no-underline transition-all inline-flex items-center gap-1.5',
                route.path.startsWith('/admin')
                  ? 'bg-emerald-500/25 text-emerald-300 border border-emerald-500/50 shadow-[0_0_15px_rgba(16,185,129,0.3)]'
                  : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/20 hover:text-emerald-300'
              ]"
            >
              <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <span>Quản trị</span>
            </AppLink>
          </nav>

          <!-- Theme Toggle -->
          <ThemeToggle />

          <!-- User Chip & Logout -->
          <div class="ml-1 sm:ml-2 flex items-center gap-2 border-l border-white/15 pl-2 sm:pl-3">
            <div
              v-if="user"
              class="hidden sm:flex items-center gap-2 rounded-xl bg-white/5 border border-white/10 px-3 py-1.5"
            >
              <div
                class="flex h-6 w-6 items-center justify-center rounded-lg bg-emerald-500/20 text-emerald-400 text-xs font-black"
              >
                {{ (user.full_name || user.email || "U").charAt(0).toUpperCase() }}
              </div>
              <span class="max-w-[140px] truncate text-xs font-semibold text-slate-200">
                {{ user.full_name || user.email }}
              </span>
              <span
                v-if="user?.roles?.includes('ADMIN')"
                class="rounded bg-rose-500/20 px-1.5 py-0.5 text-[9px] font-black uppercase tracking-wider text-rose-300 border border-rose-500/30"
              >
                ADMIN
              </span>
              <span
                v-else-if="user?.roles?.includes('STAFF')"
                class="rounded bg-amber-500/20 px-1.5 py-0.5 text-[9px] font-black uppercase tracking-wider text-amber-300 border border-amber-500/30"
              >
                STAFF
              </span>
            </div>

            <BaseButton
              variant="ghost"
              size="sm"
              class="rounded-xl border border-white/15 text-slate-300 hover:border-rose-500/30 hover:bg-rose-500/10 hover:text-rose-400 text-xs font-bold uppercase tracking-wider"
              :loading="logoutLoading"
              @click="triggerLogout"
            >
              Đăng xuất
            </BaseButton>
          </div>
        </div>
      </div>
    </header>

    <!-- Logout Error Banner -->
    <div v-if="logoutError" class="relative z-20 mx-auto max-w-5xl px-4 pt-4 sm:px-6 lg:px-8">
      <AppAlert variant="error" title="Chưa thể thu hồi phiên trên máy chủ">
        {{ logoutError }} Bạn có thể thử đăng xuất lại khi có mạng.
      </AppAlert>
    </div>

    <!-- Main Content Slot -->
    <main id="account-content" class="relative z-10 mx-auto max-w-5xl px-4 py-8 sm:px-6 sm:py-12 lg:px-8">
      <slot :user="user" />
    </main>

    <!-- Logout Confirmation Modal -->
    <AppPopup
      v-model="showLogoutConfirm"
      mode="confirm"
      variant="warning"
      title="Xác nhận đăng xuất"
      message="Bạn có chắc chắn muốn đăng xuất khỏi tài khoản Hải Duy Shop không?"
      action-text="Đăng xuất"
      cancel-text="Ở lại"
      :loading="logoutLoading"
      @confirm="confirmLogout"
    />
  </div>
</template>
