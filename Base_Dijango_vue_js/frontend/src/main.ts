import { createPinia } from "pinia";
import { createApp } from "vue";

import App from "@/app/App.vue";
import { router } from "@/app/router";
import "@/assets/styles/main.css";
import { configureAuthTransport } from "@/lib/http/client";
import { onAuthEvent } from "@/modules/auth/composables/coordination";
import { refreshAccessToken } from "@/modules/auth/composables/refresh";
import { useAuthStore } from "@/modules/auth/stores/auth";

const app = createApp(App);
const pinia = createPinia();
app.use(pinia);
app.use(router);

const auth = useAuthStore();
configureAuthTransport({
  getAccessToken: () => auth.accessToken,
  refreshAccessToken,
  onSessionInvalid: () => {
    auth.clearSession();
    void router.replace({ name: "login" });
  },
});

onAuthEvent((event) => {
  if (event.type !== "logout") return;
  auth.clearSession();
  auth.markLogoutPending(false);
  void router.replace({ name: "login" });
});

app.mount("#app");
