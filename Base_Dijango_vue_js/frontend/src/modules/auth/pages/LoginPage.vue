<script setup lang="ts">
import { storeToRefs } from "pinia";
import { useField, useForm } from "vee-validate";
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";

import BaseButton from "@/components/base/BaseButton.vue";
import BaseInput from "@/components/base/BaseInput.vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import FormField from "@/components/form/FormField.vue";
import AppLink from "@/components/navigation/AppLink.vue";
import AuthLayout from "@/layouts/AuthLayout.vue";
import { toAppError } from "@/lib/http/errors";
import { useToastStore } from "@/app/stores/toast";
import { loginSchema } from "@/modules/auth/schemas";
import { useAuthStore } from "@/modules/auth/stores/auth";

import { useAuth } from "../composables/useAuth";

const route = useRoute();
const authStore = useAuthStore();
const toast = useToastStore();
const { bootstrapError, logoutPending, logoutError } = storeToRefs(authStore);
const { login, logout, loginLoading, logoutLoading } = useAuth();
const formError = ref("");

watch(
  bootstrapError,
  (err: string | null) => {
    if (err) {
      toast.show(err, "error");
    }
  },
  { immediate: true },
);

const { handleSubmit, setFieldError } = useForm({
  validationSchema: loginSchema,
  initialValues: { email: "", password: "" },
});
const { value: email, errorMessage: emailError, handleBlur: blurEmail } = useField<string>("email");
const {
  value: password,
  errorMessage: passwordError,
  handleBlur: blurPassword,
} = useField<string>("password");

const safeRedirect = computed(() => {
  const redirect = typeof route.query.redirect === "string" ? route.query.redirect : "/";
  return redirect.startsWith("/") && !redirect.startsWith("//") ? redirect : "/";
});
const registrationCompleted = computed(() => route.query.registered === "1");

const submit = handleSubmit(async (values) => {
  formError.value = "";
  try {
    await login(values, safeRedirect.value);
  } catch (error) {
    const appError = toAppError(error);
    let hasFieldErrors = false;
    Object.entries(appError.fields).forEach(([field, message]) => {
      if (field === "email" || field === "password") {
        setFieldError(field, message);
        hasFieldErrors = true;
      }
    });
    if (!hasFieldErrors) {
      formError.value = appError.message;
      toast.show(appError.message, "error");
    }
  }
});
</script>

<template>
  <AuthLayout>
    <template #title>Đăng nhập</template>
    <template #subtitle>Đăng nhập để quản lý tài khoản và địa chỉ nhận hàng.</template>

    <div class="space-y-4">

      <AppAlert v-if="logoutPending" variant="warning" title="Đang chờ thu hồi phiên">
        <span v-if="logoutError">{{ logoutError }}</span>
        <span v-else>Yêu cầu đăng xuất trước đó chưa hoàn tất.</span>
        <BaseButton
          class="mt-3"
          size="sm"
          variant="secondary"
          :loading="logoutLoading"
          @click="logout"
        >
          Thử đăng xuất lại
        </BaseButton>
      </AppAlert>
      <AppAlert v-if="registrationCompleted" variant="success">
        Tạo tài khoản thành công. Bạn có thể đăng nhập ngay.
      </AppAlert>

      <form class="space-y-5" novalidate @submit.prevent="submit">
        <FormField v-slot="field" label="Email" name="email" :error="emailError" required>
          <BaseInput
            v-model="email"
            :id="field.id"
            name="email"
            type="email"
            autocomplete="email"
            placeholder="ban@example.com"
            :invalid="field.invalid"
            :aria-describedby="field.describedBy"
            required
            @blur="blurEmail"
          />
        </FormField>

        <FormField v-slot="field" label="Mật khẩu" name="password" :error="passwordError" required>
          <BaseInput
            v-model="password"
            :id="field.id"
            name="password"
            type="password"
            autocomplete="current-password"
            :invalid="field.invalid"
            :aria-describedby="field.describedBy"
            required
            @blur="blurPassword"
          />
        </FormField>

        <BaseButton type="submit" block :loading="loginLoading" class="mt-2 text-sm font-black uppercase tracking-wider">
          Đăng nhập
        </BaseButton>
      </form>
      <div class="flex flex-wrap items-center justify-between gap-3 pt-2 text-sm">
        <AppLink to="/forgot-password" class="text-xs font-semibold text-slate-400 hover:text-emerald-400 no-underline">
          Quên mật khẩu?
        </AppLink>
        <span class="text-xs text-slate-400">
          Chưa có tài khoản?
          <AppLink to="/register" class="ml-1 font-bold text-emerald-400 hover:text-emerald-300 no-underline">
            Đăng ký
          </AppLink>
        </span>
      </div>
    </div>
  </AuthLayout>
</template>
