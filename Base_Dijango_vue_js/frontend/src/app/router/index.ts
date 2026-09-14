import { createRouter, createWebHistory } from "vue-router";

import LoginPage from "@/modules/auth/pages/LoginPage.vue";
import ProfilePage from "@/modules/profile/pages/ProfilePage.vue";
import HomePage from "@/pages/HomePage.vue";
import NotFoundPage from "@/pages/NotFoundPage.vue";

import { installRouterGuards } from "./guards";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/login", name: "login", component: LoginPage, meta: { guestOnly: true } },
    { path: "/", name: "home", component: HomePage, meta: { requiresAuth: true } },
    { path: "/profile", name: "profile", component: ProfilePage, meta: { requiresAuth: true } },
    { path: "/:pathMatch(.*)*", name: "not-found", component: NotFoundPage },
  ],
  scrollBehavior: () => ({ top: 0 }),
});

installRouterGuards(router);
