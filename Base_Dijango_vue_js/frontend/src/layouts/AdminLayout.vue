<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";

import BaseButton from "@/components/base/BaseButton.vue";
import AppLogo from "@/components/common/AppLogo.vue";
import ThemeToggle from "@/components/common/ThemeToggle.vue";
import AppLink from "@/components/navigation/AppLink.vue";
import { useAuth } from "@/modules/auth/composables/useAuth";

interface NavigationItem {
  label: string;
  description: string;
  to: string;
  icon: "dashboard" | "orders" | "inventory" | "products" | "variants" | "settings" | "engagement";
}

interface NavigationSection {
  label: string;
  items: NavigationItem[];
}

const route = useRoute();
const { user, logout, logoutLoading } = useAuth();
const mobileMenuOpen = ref(false);

const isAdmin = computed(() => user.value?.roles.includes("ADMIN") ?? false);
const workspaceLabel = computed(() =>
  isAdmin.value ? "Quản trị cửa hàng" : "Không gian nhân viên",
);

const navigationSections = computed<NavigationSection[]>(() => {
  const sections: NavigationSection[] = [
    {
      label: "Vận hành",
      items: [
        { label: "Tổng quan", description: "Công việc hôm nay", to: "/admin", icon: "dashboard" },
        {
          label: "Đơn hàng",
          description: "Xác nhận và giao hàng",
          to: "/admin/orders",
          icon: "orders",
        },
        {
          label: "Kho hàng",
          description: "Tồn kho và điều chỉnh",
          to: "/admin/inventory",
          icon: "inventory",
        },
        {
          label: "Tương tác",
          description: "Đánh giá, ưu đãi, banner",
          to: "/admin/engagement",
          icon: "engagement",
        },
        {
          label: "Gợi ý sản phẩm",
          description: "CTR và chuyển đổi",
          to: "/admin/recommendations",
          icon: "engagement",
        },
        {
          label: "Đổi hàng",
          description: "Duyệt và kiểm hàng đổi",
          to: "/admin/exchanges",
          icon: "orders",
        },
      ],
    },
  ];
  if (isAdmin.value) {
    sections.push({
      label: "Catalog",
      items: [
        {
          label: "Sản phẩm",
          description: "Thông tin và hình ảnh",
          to: "/admin/products",
          icon: "products",
        },
        {
          label: "Biến thể SKU",
          description: "Giá, size và màu",
          to: "/admin/variants",
          icon: "variants",
        },
        {
          label: "Thiết lập catalog",
          description: "Danh mục, hãng, size, màu",
          to: "/admin/catalog-settings",
          icon: "settings",
        },
      ],
    });
  }
  return sections;
});

const pageTitle = computed(() => {
  const item = navigationSections.value
    .flatMap((section) => section.items)
    .find((entry) => entry.to === route.path);
  if (
    ["/admin/categories", "/admin/brands", "/admin/sizes", "/admin/colors"].includes(route.path)
  ) {
    return "Thiết lập catalog";
  }
  return item?.label ?? "Quản trị";
});

function isActive(path: string) {
  if (path === "/admin/catalog-settings") {
    return [path, "/admin/categories", "/admin/brands", "/admin/sizes", "/admin/colors"].includes(
      route.path,
    );
  }
  return path === "/admin" ? route.path === path : route.path.startsWith(path);
}

watch(
  () => route.fullPath,
  () => {
    mobileMenuOpen.value = false;
  },
);
</script>

<template>
  <div
    class="min-h-screen bg-[#090a0f] text-slate-100 lg:grid lg:grid-cols-[17.5rem_minmax(0,1fr)]"
  >
    <a href="#admin-content" class="sr-only focus:not-sr-only">Chuyển đến nội dung quản trị</a>

    <div
      v-if="mobileMenuOpen"
      class="fixed inset-0 z-40 bg-black/70 backdrop-blur-sm lg:hidden"
      aria-hidden="true"
      @click="mobileMenuOpen = false"
    />

    <aside
      :class="[
        'fixed inset-y-0 left-0 z-50 flex w-[17.5rem] flex-col border-r border-white/10 bg-[#0c0e17] transition-transform lg:sticky lg:top-0 lg:z-20 lg:h-screen lg:translate-x-0',
        mobileMenuOpen ? 'translate-x-0' : '-translate-x-full',
      ]"
    >
      <div class="border-b border-white/10 px-5 py-5">
        <div class="flex items-center justify-between gap-3">
          <AppLink to="/" class="block no-underline"><AppLogo theme="dark" /></AppLink>
          <button
            type="button"
            class="grid h-10 w-10 place-items-center rounded-xl text-slate-400 hover:bg-white/5 hover:text-white lg:hidden"
            aria-label="Đóng menu"
            @click="mobileMenuOpen = false"
          >
            <svg
              class="h-5 w-5"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path stroke-linecap="round" d="m6 6 12 12M18 6 6 18" />
            </svg>
          </button>
        </div>
        <div
          class="mt-4 flex items-center gap-3 rounded-2xl border border-white/10 bg-white/[0.03] p-3"
        >
          <div
            class="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-emerald-500 text-sm font-black text-black"
          >
            {{ (user?.full_name || user?.email || "U")[0]?.toUpperCase() }}
          </div>
          <div class="min-w-0">
            <p class="truncate text-sm font-bold text-white">
              {{ user?.full_name || user?.email }}
            </p>
            <p class="text-[11px] font-bold tracking-wider text-emerald-400 uppercase">
              {{ workspaceLabel }}
            </p>
          </div>
        </div>
      </div>

      <nav class="flex-1 space-y-7 overflow-y-auto px-4 py-5" aria-label="Điều hướng quản trị">
        <section v-for="section in navigationSections" :key="section.label">
          <h2 class="px-3 text-[10px] font-black tracking-[0.2em] text-slate-500 uppercase">
            {{ section.label }}
          </h2>
          <div class="mt-2 space-y-1">
            <AppLink
              v-for="item in section.items"
              :key="item.to"
              :to="item.to"
              :class="[
                'group flex items-center gap-3 rounded-xl border px-3 py-2.5 no-underline transition-colors',
                isActive(item.to)
                  ? 'border-emerald-500/30 bg-emerald-500/12 text-white'
                  : 'border-transparent text-slate-300 hover:border-white/10 hover:bg-white/5 hover:text-white',
              ]"
            >
              <span
                :class="[
                  'grid h-9 w-9 shrink-0 place-items-center rounded-lg',
                  isActive(item.to)
                    ? 'bg-emerald-500 text-black'
                    : 'bg-white/5 text-slate-400 group-hover:text-white',
                ]"
              >
                <svg
                  v-if="item.icon === 'dashboard'"
                  class="h-4 w-4"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path d="M4 13h6V4H4v9Zm10 7h6V11h-6v9ZM4 20h6v-3H4v3Zm10-13h6V4h-6v3Z" />
                </svg>
                <svg
                  v-else-if="item.icon === 'orders'"
                  class="h-4 w-4"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M9 5h6m-6 4h6m-8 11h10a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-2.5a2.5 2.5 0 0 0-5 0H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2Z"
                  />
                </svg>
                <svg
                  v-else-if="item.icon === 'inventory'"
                  class="h-4 w-4"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="m4 7 8-4 8 4-8 4-8-4Zm0 0v10l8 4 8-4V7m-8 4v10"
                  />
                </svg>
                <svg
                  v-else-if="item.icon === 'products'"
                  class="h-4 w-4"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M6 8h12l1 13H5L6 8Zm3 0V6a3 3 0 0 1 6 0v2"
                  />
                </svg>
                <svg
                  v-else-if="item.icon === 'variants'"
                  class="h-4 w-4"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M4 7h16M4 12h16M4 17h10"
                  />
                </svg>
                <svg
                  v-else
                  class="h-4 w-4"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M12 15.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Z"
                  />
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06-2.83 2.83-.06-.06a1.7 1.7 0 0 0-1.88-.34 1.7 1.7 0 0 0-1.03 1.56V21h-4v-.08A1.7 1.7 0 0 0 9 19.36a1.7 1.7 0 0 0-1.88.34l-.06.06-2.83-2.83.06-.06A1.7 1.7 0 0 0 4.63 15 1.7 1.7 0 0 0 3.08 14H3v-4h.08A1.7 1.7 0 0 0 4.64 9a1.7 1.7 0 0 0-.34-1.88l-.06-.06 2.83-2.83.06.06A1.7 1.7 0 0 0 9 4.63 1.7 1.7 0 0 0 10 3.08V3h4v.08A1.7 1.7 0 0 0 15 4.64a1.7 1.7 0 0 0 1.88-.34l.06-.06 2.83 2.83-.06.06A1.7 1.7 0 0 0 19.37 9 1.7 1.7 0 0 0 20.92 10H21v4h-.08A1.7 1.7 0 0 0 19.4 15Z"
                  />
                </svg>
              </span>
              <span class="min-w-0">
                <span class="block text-sm font-bold">{{ item.label }}</span>
                <span
                  class="block truncate text-[11px] font-medium text-slate-500 group-hover:text-slate-400"
                  >{{ item.description }}</span
                >
              </span>
            </AppLink>
          </div>
        </section>
      </nav>

      <div class="border-t border-white/10 p-4">
        <BaseButton
          type="button"
          variant="ghost"
          size="sm"
          block
          :loading="logoutLoading"
          class="justify-start text-slate-400 hover:text-rose-400"
          @click="logout"
        >
          Đăng xuất
        </BaseButton>
      </div>
    </aside>

    <div class="min-w-0">
      <header
        class="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-white/10 bg-[#090a0f]/90 px-4 backdrop-blur-xl sm:px-6 lg:px-8"
      >
        <div class="flex items-center gap-3">
          <button
            type="button"
            class="grid h-10 w-10 place-items-center rounded-xl border border-white/10 text-slate-300 hover:bg-white/5 lg:hidden"
            aria-label="Mở menu quản trị"
            @click="mobileMenuOpen = true"
          >
            <svg
              class="h-5 w-5"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path stroke-linecap="round" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <div>
            <p class="text-[10px] font-bold tracking-widest text-slate-500 uppercase">
              {{ workspaceLabel }}
            </p>
            <p class="text-sm font-black text-white">{{ pageTitle }}</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <AppLink
            to="/"
            class="hidden rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs text-slate-300 no-underline hover:text-white sm:inline-flex"
            >Xem cửa hàng</AppLink
          >
          <ThemeToggle />
        </div>
      </header>

      <main id="admin-content" class="mx-auto w-full max-w-[1480px] p-4 sm:p-6 lg:p-8">
        <slot />
      </main>
    </div>
  </div>
</template>
