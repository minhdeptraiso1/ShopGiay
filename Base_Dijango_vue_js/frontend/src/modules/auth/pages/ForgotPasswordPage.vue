<script setup lang="ts">
import { useField, useForm } from "vee-validate";
import { ref } from "vue";

import BaseButton from "@/components/base/BaseButton.vue";
import BaseInput from "@/components/base/BaseInput.vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import FormField from "@/components/form/FormField.vue";
import AppLink from "@/components/navigation/AppLink.vue";
import AuthLayout from "@/layouts/AuthLayout.vue";
import { toAppError } from "@/lib/http/errors";
import { useToastStore } from "@/app/stores/toast";
import { requestPasswordReset } from "@/modules/auth/api";
import { passwordResetRequestSchema } from "@/modules/auth/schemas";

const toast = useToastStore();
const loading = ref(false);
const error = ref("");
const success = ref("");
const { handleSubmit, setFieldError } = useForm({
  validationSchema: passwordResetRequestSchema,
  initialValues: { email: "" },
});
const { value: email, errorMessage: emailError, handleBlur } = useField<string>("email");

const submit = handleSubmit(async (values) => {
  loading.value = true;
  error.value = "";
  success.value = "";
  try {
    success.value = await requestPasswordReset(values.email);
    toast.show(success.value, "success");
  } catch (requestError) {
    const appError = toAppError(requestError);
    if (appError.fields.email) setFieldError("email", appError.fields.email);
    else {
      error.value = appError.message;
      toast.show(appError.message, "error");
    }
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <AuthLayout>
    <template #title>Quên mật khẩu</template>
    <template #subtitle>Nhập email và chúng tôi sẽ gửi hướng dẫn nếu tài khoản tồn tại.</template>

    <AppAlert v-if="success" class="mb-5" variant="success">{{ success }}</AppAlert>
    <form class="space-y-5" novalidate @submit="submit">
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
          @blur="handleBlur"
        />
      </FormField>
      <BaseButton type="submit" block :loading="loading" class="mt-2 text-sm font-black uppercase tracking-wider">
        Gửi hướng dẫn
      </BaseButton>
    </form>
    <p class="mt-6 text-center text-xs text-slate-400">
      <AppLink to="/login" class="font-bold text-emerald-400 hover:text-emerald-300 no-underline">
        ← Quay lại đăng nhập
      </AppLink>
    </p>
  </AuthLayout>
</template>
