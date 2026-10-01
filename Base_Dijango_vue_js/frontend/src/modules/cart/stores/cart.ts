import { defineStore } from "pinia";
import { computed, ref } from "vue";

import { useToastStore } from "@/app/stores/toast";
import { toAppError } from "@/lib/http/errors";
import { useAuthStore } from "@/modules/auth/stores/auth";
import {
  addToCart,
  fetchCart,
  removeCartItem,
  updateCartItemQuantity,
} from "../api";
import type { Cart } from "../types";

export const useCartStore = defineStore("cart", () => {
  const cart = ref<Cart | null>(null);
  const loading = ref(false);
  const error = ref("");

  const auth = useAuthStore();
  const toast = useToastStore();

  const itemCount = computed(() => {
    if (!cart.value?.items) return 0;
    return cart.value.items.reduce((sum, item) => sum + item.quantity, 0);
  });

  const subtotal = computed(() => cart.value?.subtotal || "0");

  async function loadCart() {
    if (!auth.isAuthenticated) {
      cart.value = null;
      return;
    }
    loading.value = true;
    error.value = "";
    try {
      cart.value = await fetchCart();
    } catch (err) {
      // Non-blocking for guests or new carts
      console.debug("[Cart] Failed to load cart:", err);
    } finally {
      loading.value = false;
    }
  }

  async function addItem(
    variantId: number,
    quantity: number = 1,
    recommendationContextId?: string,
  ): Promise<boolean> {
    if (!auth.isAuthenticated) {
      toast.show("Vui lòng đăng nhập để thêm sản phẩm vào giỏ hàng.", "error");
      return false;
    }
    loading.value = true;
    try {
      await addToCart(variantId, quantity, recommendationContextId);
      await loadCart();
      toast.show("Đã thêm sản phẩm vào giỏ hàng!", "success");
      return true;
    } catch (err) {
      const appErr = toAppError(err);
      toast.show(appErr.message || "Không thể thêm vào giỏ hàng.", "error");
      return false;
    } finally {
      loading.value = false;
    }
  }

  async function setItemQuantity(itemId: number, quantity: number): Promise<boolean> {
    if (quantity < 1 || quantity > 99) return false;
    loading.value = true;
    try {
      await updateCartItemQuantity(itemId, quantity);
      await loadCart();
      return true;
    } catch (err) {
      const appErr = toAppError(err);
      toast.show(appErr.message || "Không thể cập nhật số lượng.", "error");
      return false;
    } finally {
      loading.value = false;
    }
  }

  async function removeItem(itemId: number): Promise<boolean> {
    loading.value = true;
    try {
      await removeCartItem(itemId);
      await loadCart();
      toast.show("Đã xóa sản phẩm khỏi giỏ hàng.", "info");
      return true;
    } catch (err) {
      const appErr = toAppError(err);
      toast.show(appErr.message || "Không thể xóa sản phẩm.", "error");
      return false;
    } finally {
      loading.value = false;
    }
  }

  return {
    cart,
    loading,
    error,
    itemCount,
    subtotal,
    loadCart,
    addItem,
    setItemQuantity,
    removeItem,
  };
});
