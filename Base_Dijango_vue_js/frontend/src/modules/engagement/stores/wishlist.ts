import { computed, ref } from "vue";
import { defineStore } from "pinia";

import { fetchWishlist, removeWishlist, toggleWishlist } from "../api";
import type { WishlistItem } from "../types";

export const useWishlistStore = defineStore("wishlist", () => {
  const items = ref<WishlistItem[]>([]);
  const loading = ref(false);
  const loaded = ref(false);
  const error = ref("");
  const count = computed(() => items.value.length);

  function has(productId: number): boolean {
    return items.value.some((item) => item.product.id === productId);
  }

  async function load(force = false): Promise<void> {
    if (loading.value || (loaded.value && !error.value && !force)) return;
    loading.value = true;
    error.value = "";
    try {
      items.value = await fetchWishlist();
      loaded.value = true;
    } catch {
      error.value = "Không thể tải danh sách yêu thích.";
      loaded.value = true;
    } finally {
      loading.value = false;
    }
  }

  async function toggle(productId: number): Promise<boolean> {
    const active = await toggleWishlist(productId);
    await load(true);
    return active;
  }

  async function remove(productId: number): Promise<void> {
    await removeWishlist(productId);
    items.value = items.value.filter((item) => item.product.id !== productId);
  }

  function clear(): void {
    items.value = [];
    loaded.value = false;
    error.value = "";
  }

  return { items, loading, loaded, error, count, has, load, toggle, remove, clear };
});
