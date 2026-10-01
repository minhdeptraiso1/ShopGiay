<script setup lang="ts">
import { useField, useForm } from "vee-validate";
import { ref } from "vue";
import { useRouter } from "vue-router";

import BaseButton from "@/components/base/BaseButton.vue";
import BaseInput from "@/components/base/BaseInput.vue";
import FormField from "@/components/form/FormField.vue";
import AppLink from "@/components/navigation/AppLink.vue";
import AuthLayout from "@/layouts/AuthLayout.vue";
import { toAppError } from "@/lib/http/errors";
import { useToastStore } from "@/app/stores/toast";
import { registerRequest } from "@/modules/auth/api";
import { registerSchema } from "@/modules/auth/schemas";

const router = useRouter();
const loading = ref(false);
const formError = ref("");

function notifyToast(message: string, variant: "error" | "success" = "error") {
  try {
    useToastStore().show(message, variant);
  } catch {
    // Fallback when rendered without pinia in tests
  }
}
const { handleSubmit, setFieldError } = useForm({
  validationSchema: registerSchema,
  initialValues: { fullName: "", email: "", password: "", passwordConfirm: "" },
});
const {
  value: fullName,
  errorMessage: fullNameError,
  handleBlur: blurFullName,
} = useField<string>("fullName");
const { value: email, errorMessage: emailError, handleBlur: blurEmail } = useField<string>("email");
const {
  value: password,
  errorMessage: passwordError,
  handleBlur: blurPassword,
} = useField<string>("password");
const {
  value: passwordConfirm,
  errorMessage: passwordConfirmError,
  handleBlur: blurPasswordConfirm,
} = useField<string>("passwordConfirm");

const fieldMap: Record<string, "fullName" | "email" | "password" | "passwordConfirm"> = {
  full_name: "fullName",
  email: "email",
  password: "password",
  password_confirm: "passwordConfirm",
};

const submit = handleSubmit(async (values) => {
  loading.value = true;
  formError.value = "";
  try {
    await registerRequest({
      email: values.email,
      full_name: values.fullName,
      password: values.password,
      password_confirm: values.passwordConfirm,
    });
    await router.replace({ name: "login", query: { registered: "1" } });
  } catch (error) {
    const appError = toAppError(error);
    let hasFieldErrors = false;
    Object.entries(appError.fields).forEach(([field, message]) => {
      const formField = fieldMap[field];
      if (formField) {
        setFieldError(formField, message);
        hasFieldErrors = true;
      }
    });
    if (!hasFieldErrors) {
      formError.value = appError.message;
      notifyToast(appError.message, "error");
    }
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <AuthLayout>
    <template #title>Tạo tài khoản</template>
    <template #subtitle>Đăng ký để lưu địa chỉ và chuẩn bị cho trải nghiệm mua sắm.</template>

    <form class="space-y-5" novalidate @submit.prevent="submit">
      <FormField v-slot="field" label="Họ và tên" name="fullName" :error="fullNameError" required>
        <BaseInput
          v-model="fullName"
          :id="field.id"
          name="full_name"
          autocomplete="name"
          :invalid="field.invalid"
          :aria-describedby="field.describedBy"
          required
          @blur="blurFullName"
        />
      </FormField>
      <FormField v-slot="field" label="Email" name="email" :error="emailError" required>
        <BaseInput
          v-model="email"
          :id="field.id"
          name="email"
          type="email"
          autocomplete="email"
          :invalid="field.invalid"
          :aria-describedby="field.describedBy"
          required
          @blur="blurEmail"
        />
      </FormField>
      <FormField
        v-slot="field"
        label="Mật khẩu"
        name="password"
        help="Dùng ít nhất 8 ký tự và tránh mật khẩu quá phổ biến."
        :error="passwordError"
        required
      >
        <BaseInput
          v-model="password"
          :id="field.id"
          name="password"
          type="password"
          autocomplete="new-password"
          :invalid="field.invalid"
          :aria-describedby="field.describedBy"
          required
          @blur="blurPassword"
        />
      </FormField>
      <FormField
        v-slot="field"
        label="Nhập lại mật khẩu"
        name="passwordConfirm"
        :error="passwordConfirmError"
        required
      >
        <BaseInput
          v-model="passwordConfirm"
          :id="field.id"
          name="password_confirm"
          type="password"
          autocomplete="new-password"
          :invalid="field.invalid"
          :aria-describedby="field.describedBy"
          required
          @blur="blurPasswordConfirm"
        />
      </FormField>
      <BaseButton type="submit" block :loading="loading" class="mt-2 text-sm font-black uppercase tracking-wider">
        Đăng ký
      </BaseButton>
    </form>

    <p class="mt-6 text-center text-xs text-slate-400">
      Đã có tài khoản?
      <AppLink to="/login" class="ml-1 font-bold text-emerald-400 hover:text-emerald-300 no-underline">
        Đăng nhập ngay
      </AppLink>
    </p>
  </AuthLayout>
</template>
