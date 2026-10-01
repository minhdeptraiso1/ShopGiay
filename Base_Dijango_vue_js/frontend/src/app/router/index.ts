import { createRouter, createWebHistory } from "vue-router";

import AdminBrandsPage from "@/modules/admin/pages/AdminBrandsPage.vue";
import AdminCatalogSettingsPage from "@/modules/admin/pages/AdminCatalogSettingsPage.vue";
import AdminCategoriesPage from "@/modules/admin/pages/AdminCategoriesPage.vue";
import AdminColorsPage from "@/modules/admin/pages/AdminColorsPage.vue";
import AdminInventoryPage from "@/modules/admin/pages/AdminInventoryPage.vue";
import AdminOrdersPage from "@/modules/admin/pages/AdminOrdersPage.vue";
import AdminProductsPage from "@/modules/admin/pages/AdminProductsPage.vue";
import AdminRecommendationsPage from "@/modules/admin/pages/AdminRecommendationsPage.vue";
import AdminSizesPage from "@/modules/admin/pages/AdminSizesPage.vue";
import AdminVariantsPage from "@/modules/admin/pages/AdminVariantsPage.vue";
import ForgotPasswordPage from "@/modules/auth/pages/ForgotPasswordPage.vue";
import LoginPage from "@/modules/auth/pages/LoginPage.vue";
import RegisterPage from "@/modules/auth/pages/RegisterPage.vue";
import ResetPasswordPage from "@/modules/auth/pages/ResetPasswordPage.vue";
import CartPage from "@/modules/cart/pages/CartPage.vue";
import ProductDetailPage from "@/modules/catalog/pages/ProductDetailPage.vue";
import ProductsPage from "@/modules/catalog/pages/ProductsPage.vue";
import WishlistPage from "@/modules/engagement/pages/WishlistPage.vue";
import AdminEngagementPage from "@/modules/engagement/pages/AdminEngagementPage.vue";
import AdminExchangesPage from "@/modules/exchanges/pages/AdminExchangesPage.vue";
import ExchangeCreatePage from "@/modules/exchanges/pages/ExchangeCreatePage.vue";
import ExchangesPage from "@/modules/exchanges/pages/ExchangesPage.vue";
import OrderDetailPage from "@/modules/orders/pages/OrderDetailPage.vue";
import OrdersPage from "@/modules/orders/pages/OrdersPage.vue";
import ProfilePage from "@/modules/profile/pages/ProfilePage.vue";
import AdminHomePage from "@/pages/AdminHomePage.vue";
import ForbiddenPage from "@/pages/ForbiddenPage.vue";
import HomePage from "@/pages/HomePage.vue";
import NotFoundPage from "@/pages/NotFoundPage.vue";

import { installRouterGuards } from "./guards";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/login", name: "login", component: LoginPage, meta: { guestOnly: true } },
    { path: "/register", name: "register", component: RegisterPage, meta: { guestOnly: true } },
    {
      path: "/forgot-password",
      name: "forgot-password",
      component: ForgotPasswordPage,
      meta: { guestOnly: true },
    },
    { path: "/reset-password", name: "reset-password", component: ResetPasswordPage },
    { path: "/", name: "home", component: HomePage },
    { path: "/products", name: "products", component: ProductsPage },
    { path: "/products/:slug", name: "product-detail", component: ProductDetailPage },
    { path: "/cart", name: "cart", component: CartPage },
    {
      path: "/wishlist",
      name: "wishlist",
      component: WishlistPage,
      meta: { requiresAuth: true },
    },
    { path: "/orders", name: "orders", component: OrdersPage, meta: { requiresAuth: true } },
    {
      path: "/exchanges",
      name: "exchanges",
      component: ExchangesPage,
      meta: { requiresAuth: true },
    },
    {
      path: "/exchanges/new",
      name: "exchange-create",
      component: ExchangeCreatePage,
      meta: { requiresAuth: true },
    },
    {
      path: "/orders/:id",
      name: "order-detail",
      component: OrderDetailPage,
      meta: { requiresAuth: true },
    },
    { path: "/profile", name: "profile", component: ProfilePage, meta: { requiresAuth: true } },
    {
      path: "/profile/addresses",
      redirect: "/profile",
    },
    {
      path: "/admin",
      name: "admin-home",
      component: AdminHomePage,
      meta: { requiresAuth: true, requiredRoles: ["STAFF", "ADMIN"] },
    },
    {
      path: "/admin/catalog-settings",
      name: "admin-catalog-settings",
      component: AdminCatalogSettingsPage,
      meta: { requiresAuth: true, requiredRoles: ["ADMIN"] },
    },
    {
      path: "/admin/products",
      name: "admin-products",
      component: AdminProductsPage,
      meta: { requiresAuth: true, requiredRoles: ["ADMIN"] },
    },
    {
      path: "/admin/recommendations",
      name: "admin-recommendations",
      component: AdminRecommendationsPage,
      meta: { requiresAuth: true, requiredRoles: ["STAFF", "ADMIN"] },
    },
    {
      path: "/admin/categories",
      name: "admin-categories",
      component: AdminCategoriesPage,
      meta: { requiresAuth: true, requiredRoles: ["ADMIN"] },
    },
    {
      path: "/admin/brands",
      name: "admin-brands",
      component: AdminBrandsPage,
      meta: { requiresAuth: true, requiredRoles: ["ADMIN"] },
    },
    {
      path: "/admin/sizes",
      name: "admin-sizes",
      component: AdminSizesPage,
      meta: { requiresAuth: true, requiredRoles: ["ADMIN"] },
    },
    {
      path: "/admin/colors",
      name: "admin-colors",
      component: AdminColorsPage,
      meta: { requiresAuth: true, requiredRoles: ["ADMIN"] },
    },
    {
      path: "/admin/variants",
      name: "admin-variants",
      component: AdminVariantsPage,
      meta: { requiresAuth: true, requiredRoles: ["ADMIN"] },
    },
    {
      path: "/admin/inventory",
      name: "admin-inventory",
      component: AdminInventoryPage,
      meta: { requiresAuth: true, requiredRoles: ["STAFF", "ADMIN"] },
    },
    {
      path: "/admin/orders",
      name: "admin-orders",
      component: AdminOrdersPage,
      meta: { requiresAuth: true, requiredRoles: ["STAFF", "ADMIN"] },
    },
    {
      path: "/admin/engagement",
      name: "admin-engagement",
      component: AdminEngagementPage,
      meta: { requiresAuth: true, requiredRoles: ["STAFF", "ADMIN"] },
    },
    {
      path: "/admin/exchanges",
      name: "admin-exchanges",
      component: AdminExchangesPage,
      meta: { requiresAuth: true, requiredRoles: ["STAFF", "ADMIN"] },
    },
    { path: "/403", name: "forbidden", component: ForbiddenPage },
    { path: "/:pathMatch(.*)*", name: "not-found", component: NotFoundPage },
  ],
  scrollBehavior: () => ({ top: 0 }),
});

installRouterGuards(router);
