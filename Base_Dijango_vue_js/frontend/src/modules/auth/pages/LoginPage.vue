<script setup lang="ts">
import { storeToRefs } from "pinia";
import { useField, useForm } from "vee-validate";
import { computed, ref } from "vue";
import { useRoute } from "vue-router";

import BaseButton from "@/components/base/BaseButton.vue";
import BaseInput from "@/components/base/BaseInput.vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import FormField from "@/components/form/FormField.vue";
import AuthLayout from "@/layouts/AuthLayout.vue";
import { toAppError } from "@/lib/http/errors";
import { loginSchema } from "@/modules/auth/schemas";
import { useAuthStore } from "@/modules/auth/stores/auth";

import { useAuth } from "../composables/useAuth";

const route = useRoute();
const authStore = useAuthStore();
const { bootstrapError, logoutPending, logoutError } = storeToRefs(authStore);
const { login, logout, loginLoading, logoutLoading } = useAuth();
const formError = ref("");

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

const submit = handleSubmit(async (values) => {
  formError.value = "";
  try {
    await login(values, safeRedirect.value);
  } catch (error) {
    const appError = toAppError(error);
    Object.entries(appError.fields).forEach(([field, message]) => {
      if (field === "email" || field === "password") setFieldError(field, message);
    });
    if (Object.keys(appError.fields).length === 0) formError.value = appError.message;
  }
});
</script>

<template>
  <AuthLayout>
    <template #title>Đăng nhập</template>
    <template #subtitle>Sử dụng tài khoản đã được quản trị viên tạo.</template>

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
      <AppAlert v-else-if="bootstrapError" variant="error">{{ bootstrapError }}</AppAlert>
      <AppAlert v-if="formError" variant="error" title="Không thể đăng nhập">
        {{ formError }}
      </AppAlert>

      <form class="space-y-5" novalidate @submit="submit">
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

        <BaseButton type="submit" block :loading="loginLoading">Đăng nhập</BaseButton>
      </form>
    </div>
  </AuthLayout>
</template>
