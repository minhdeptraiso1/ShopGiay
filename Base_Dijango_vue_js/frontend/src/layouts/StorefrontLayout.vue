<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";

import BaseButton from "@/components/base/BaseButton.vue";
import AppLogo from "@/components/common/AppLogo.vue";
import ThemeToggle from "@/components/common/ThemeToggle.vue";
import AppLink from "@/components/navigation/AppLink.vue";
import { useAuth } from "@/modules/auth/composables/useAuth";
import { useCartStore } from "@/modules/cart/stores/cart";
import { useWishlistStore } from "@/modules/engagement/stores/wishlist";

const router = useRouter();
const { user, isAuthenticated, logout, logoutLoading } = useAuth();
const cartStore = useCartStore();
const wishlist = useWishlistStore();

const searchQuery = ref("");
const isMobileMenuOpen = ref(false);

onMounted(() => {
  if (isAuthenticated.value) {
    void cartStore.loadCart();
    void wishlist.load();
  }
});

watch(isAuthenticated, (authenticated) => {
  if (authenticated) void wishlist.load();
  else wishlist.clear();
});

const navLinks = [
  { label: "Sản phẩm", cat: "" },
  { label: "Mới", cat: "new" },
  { label: "Nam", cat: "men" },
  { label: "Nữ", cat: "women" },
  { label: "Bóng rổ", cat: "basketball" },
  { label: "Chạy bộ", cat: "running" },
];

function navigateToCategory(cat: string) {
  isMobileMenuOpen.value = false;
  void router.push({ name: "products", query: cat ? { category: cat } : {} });
}

function handleSearch() {
  if (!searchQuery.value.trim()) return;
  isMobileMenuOpen.value = false;
  void router.push({ name: "products", query: { q: searchQuery.value.trim() } });
}
</script>

<template>
  <div
    class="flex min-h-screen flex-col bg-[#090a0f] font-sans text-slate-100 antialiased selection:bg-emerald-500 selection:text-black"
  >
    <!-- Skip to main content accessibility -->
    <a
      href="#main-content"
      class="sr-only z-50 rounded-md bg-emerald-500 px-4 py-2 font-bold text-black focus:not-sr-only focus:fixed focus:top-3 focus:left-3"
    >
      Chuyển đến nội dung chính
    </a>

    <!-- Main Navigation Header (Clean, 3-column unified layout) -->
    <header class="sticky top-0 z-40 border-b border-white/10 bg-[#090a0f]/95 backdrop-blur-md">
      <div
        class="mx-auto flex h-16 max-w-7xl items-center justify-between gap-4 px-4 sm:px-6 lg:px-8"
      >
        <!-- 1. Left: Brand Logo (No shrink, single line) -->
        <AppLink
          to="/"
          class="flex shrink-0 items-center no-underline transition-opacity hover:opacity-90"
        >
          <AppLogo size="md" theme="dark" />
        </AppLink>

        <!-- 2. Center: Desktop Category Navigation (Short names, active on xl screens) -->
        <nav class="hidden items-center gap-1 xl:flex" aria-label="Điều hướng chính">
          <button
            v-for="link in navLinks"
            :key="link.cat"
            type="button"
            :class="[
              'cursor-pointer px-3 py-1.5 text-sm font-semibold tracking-tight transition-colors duration-150',
              'text-slate-300 hover:text-white',
            ]"
            @click="navigateToCategory(link.cat)"
          >
            {{ link.label }}
          </button>
        </nav>

        <!-- 3. Right: Search & Actions (Compact, single-row layout) -->
        <div class="flex shrink-0 items-center gap-2.5 sm:gap-3">
          <!-- Compact Search Bar -->
          <form class="relative hidden sm:block" @submit.prevent="handleSearch">
            <span
              class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400"
            >
              <svg
                class="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="1.75"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </span>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Tìm kiếm..."
              class="h-9 w-36 rounded-full border border-white/10 bg-white/5 pr-3 pl-9 text-xs text-white placeholder-slate-400 transition-all duration-200 focus:w-52 focus:border-emerald-500 focus:bg-white/10 focus:outline-none"
            />
          </form>

          <!-- Wishlist Action (Badge only if count > 0) -->
          <AppLink
            to="/wishlist"
            class="relative flex h-9 w-9 items-center justify-center rounded-full text-slate-300 transition-colors hover:bg-white/10 hover:text-white"
            title="Yêu thích"
          >
            <svg
              class="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="1.75"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
              />
            </svg>
            <span
              v-if="wishlist.count > 0"
              class="absolute -top-0.5 -right-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-emerald-500 text-[10px] font-bold text-black"
            >
              {{ wishlist.count }}
            </span>
          </AppLink>

          <!-- Shopping Bag Action (Badge only if count > 0) -->
          <AppLink
            to="/cart"
            class="relative flex h-9 w-9 items-center justify-center rounded-full text-slate-300 no-underline transition-colors hover:bg-white/10 hover:text-white"
            title="Giỏ hàng"
          >
            <svg
              class="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="1.75"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
              />
            </svg>
            <span
              v-if="cartStore.itemCount > 0"
              class="absolute -top-0.5 -right-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-emerald-500 text-[10px] font-bold text-black"
            >
              {{ cartStore.itemCount }}
            </span>
          </AppLink>

          <!-- Theme Toggle Switch -->
          <ThemeToggle />

          <!-- Auth Status Actions (Single line, no wrap) -->
          <div class="hidden items-center gap-2 md:flex">
            <template v-if="isAuthenticated">
              <AppLink
                v-if="user?.roles.includes('ADMIN') || user?.roles.includes('STAFF')"
                to="/admin"
                class="flex items-center gap-1.5 rounded-full border border-emerald-500/40 bg-emerald-500/15 px-3 py-1 text-xs font-bold text-emerald-400 no-underline transition hover:bg-emerald-500/25 hover:text-white shadow-sm"
              >
                <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                  />
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
                Quản trị
              </AppLink>
              <AppLink
                to="/profile"
                class="flex items-center gap-1.5 rounded-full border border-white/10 bg-white/5 px-2.5 py-1 text-xs font-semibold text-slate-200 no-underline transition hover:border-emerald-500/50 hover:text-white"
              >
                <div
                  class="grid h-5 w-5 place-items-center rounded-full bg-emerald-500 text-[10px] font-black text-black"
                >
                  {{ (user?.full_name || user?.email || "U")[0]?.toUpperCase() || "U" }}
                </div>
                <span class="max-w-[100px] truncate text-xs">{{
                  user?.full_name || user?.email
                }}</span>
              </AppLink>
              <BaseButton
                size="sm"
                variant="ghost"
                :loading="logoutLoading"
                class="px-2 text-xs font-medium text-slate-400 hover:text-rose-400"
                @click="logout"
              >
                Đăng xuất
              </BaseButton>
            </template>
            <template v-else>
              <AppLink
                to="/login"
                class="px-2.5 py-1.5 text-xs font-semibold text-slate-300 no-underline transition hover:text-white"
              >
                Đăng nhập
              </AppLink>
              <AppLink
                to="/register"
                class="rounded-full bg-emerald-500 px-3.5 py-1.5 text-xs font-bold text-black no-underline transition hover:bg-emerald-400"
              >
                Đăng ký
              </AppLink>
            </template>
          </div>

          <!-- Mobile Hamburger Toggle (Visible under xl breakpoint) -->
          <button
            type="button"
            class="flex h-9 w-9 items-center justify-center rounded-lg text-slate-300 xl:hidden hover:bg-white/10 hover:text-white"
            @click="isMobileMenuOpen = !isMobileMenuOpen"
            aria-label="Mở menu"
          >
            <svg
              v-if="!isMobileMenuOpen"
              class="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
            >
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
            <svg
              v-else
              class="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
            >
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Mobile Dropdown Navigation Drawer -->
      <div
        v-if="isMobileMenuOpen"
        class="border-b border-white/10 bg-[#090a0f]/98 px-4 py-4 backdrop-blur-xl xl:hidden"
      >
        <!-- Mobile Search -->
        <form class="mb-3 sm:hidden" @submit.prevent="handleSearch">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Tìm kiếm giày..."
            class="h-9 w-full rounded-full border border-white/10 bg-white/5 px-4 text-xs text-white placeholder-slate-400 focus:border-emerald-500 focus:outline-none"
          />
        </form>

        <!-- Category Links -->
        <div class="grid grid-cols-2 gap-1 sm:grid-cols-3">
          <button
            v-for="link in navLinks"
            :key="link.cat"
            type="button"
            :class="[
              'rounded-lg px-3 py-2 text-left text-sm font-semibold transition-colors',
              'text-slate-200 hover:bg-white/5',
            ]"
            @click="navigateToCategory(link.cat)"
          >
            {{ link.label }}
          </button>
        </div>

        <!-- Mobile Auth Actions -->
        <div class="mt-4 border-t border-white/10 pt-3">
          <template v-if="isAuthenticated">
            <div class="mb-2 flex items-center justify-between">
              <AppLink
                to="/profile"
                class="text-xs font-semibold text-emerald-400 no-underline"
                @click="isMobileMenuOpen = false"
              >
                Hồ sơ: {{ user?.full_name || user?.email }}
              </AppLink>
              <button type="button" class="text-xs font-semibold text-rose-400" @click="logout">
                Đăng xuất
              </button>
            </div>
            <div class="flex gap-2 text-xs">
              <AppLink
                to="/cart"
                class="flex-1 rounded-lg border border-white/10 bg-white/5 py-2 text-center font-semibold text-slate-200 no-underline"
                @click="isMobileMenuOpen = false"
              >
                🛒 Giỏ hàng ({{ cartStore.itemCount }})
              </AppLink>
              <AppLink
                to="/orders"
                class="flex-1 rounded-lg border border-white/10 bg-white/5 py-2 text-center font-semibold text-slate-200 no-underline"
                @click="isMobileMenuOpen = false"
              >
                📦 Đơn hàng
              </AppLink>
              <AppLink
                to="/wishlist"
                class="flex-1 rounded-lg border border-white/10 bg-white/5 py-2 text-center font-semibold text-slate-200 no-underline"
                @click="isMobileMenuOpen = false"
              >
                ♥ Yêu thích ({{ wishlist.count }})
              </AppLink>
              <AppLink
                v-if="user?.roles?.includes('ADMIN') || user?.roles?.includes('STAFF')"
                to="/admin"
                class="flex-1 rounded-lg border border-emerald-500/40 bg-emerald-500/15 py-2 text-center font-bold text-emerald-400 no-underline shadow-[0_0_12px_rgba(16,185,129,0.2)]"
                @click="isMobileMenuOpen = false"
              >
                🛡️ Quản trị
              </AppLink>
            </div>
          </template>
          <template v-else>
            <div class="flex gap-2">
              <AppLink
                to="/login"
                class="flex-1 rounded-full border border-white/20 py-2 text-center text-xs font-semibold text-white no-underline"
                @click="isMobileMenuOpen = false"
              >
                Đăng nhập
              </AppLink>
              <AppLink
                to="/register"
                class="flex-1 rounded-full bg-emerald-500 py-2 text-center text-xs font-bold text-black no-underline"
                @click="isMobileMenuOpen = false"
              >
                Đăng ký
              </AppLink>
            </div>
          </template>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main id="main-content" class="flex-1">
      <slot />
    </main>

    <!-- Clean, Unified Footer -->
    <footer class="border-t border-white/10 bg-[#07080c] text-slate-400">
      <div class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 gap-8 md:grid-cols-12">
          <!-- Store Info -->
          <div class="md:col-span-5 space-y-3">
            <AppLogo size="md" theme="dark" />
            <p class="max-w-sm text-xs leading-relaxed text-slate-400">
              Cửa hàng giày thể thao & sneakers chính hãng. Trải nghiệm bước chạy tự tin cùng phong
              cách đường phố hiện đại.
            </p>
            <p class="text-xs text-slate-500">
              Showroom: 123 Phố Thể Thao, Hà Nội • Hotline: 0988.888.xxx
            </p>
          </div>

          <!-- Links Column 1 -->
          <div class="md:col-span-3">
            <h3 class="text-xs font-bold tracking-wider text-white uppercase">Danh Mục</h3>
            <ul class="mt-3 space-y-2 text-xs">
              <li>
                <AppLink
                  :to="{ name: 'products', query: { category: 'running' } }"
                  class="text-slate-400 no-underline hover:text-white"
                >
                  Giày Chạy Bộ
                </AppLink>
              </li>
              <li>
                <AppLink
                  :to="{ name: 'products', query: { category: 'basketball' } }"
                  class="text-slate-400 no-underline hover:text-white"
                >
                  Giày Bóng Rổ
                </AppLink>
              </li>
              <li>
                <AppLink
                  :to="{ name: 'products', query: { category: 'men' } }"
                  class="text-slate-400 no-underline hover:text-white"
                >
                  Sneakers Nam
                </AppLink>
              </li>
              <li>
                <AppLink
                  :to="{ name: 'products', query: { category: 'women' } }"
                  class="text-slate-400 no-underline hover:text-white"
                >
                  Sneakers Nữ
                </AppLink>
              </li>
            </ul>
          </div>

          <!-- Links Column 2 -->
          <div class="md:col-span-4">
            <h3 class="text-xs font-bold tracking-wider text-white uppercase">
              Chính Sách & Cam Kết
            </h3>
            <ul class="mt-3 space-y-2 text-xs">
              <li><span class="text-slate-400">✓ 100% Sản phẩm chính hãng</span></li>
              <li><span class="text-slate-400">✓ Hỗ trợ đổi size trong 30 ngày</span></li>
              <li><span class="text-slate-400">✓ Giao hàng hỏa tốc toàn quốc</span></li>
              <li><span class="text-slate-400">✓ Bảo hành keo dán trọn đời</span></li>
            </ul>
          </div>
        </div>

        <!-- Bottom Copyright -->
        <div
          class="mt-10 flex flex-wrap items-center justify-between gap-4 border-t border-white/5 pt-6 text-xs text-slate-500"
        >
          <p>© 2026 Hải Duy Shop. Tất cả các quyền được bảo lưu.</p>
          <p>Thiết kế cho trải nghiệm mua sắm sneaker hiện đại.</p>
        </div>
      </div>
    </footer>
  </div>
</template>
