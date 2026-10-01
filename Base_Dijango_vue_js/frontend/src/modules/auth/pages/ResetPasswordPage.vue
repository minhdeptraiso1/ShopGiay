<script setup lang="ts">
import { useField, useForm } from "vee-validate";
import { computed, ref } from "vue";
import { useRoute } from "vue-router";

import BaseButton from "@/components/base/BaseButton.vue";
import BaseInput from "@/components/base/BaseInput.vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import FormField from "@/components/form/FormField.vue";
import AppLink from "@/components/navigation/AppLink.vue";
import AuthLayout from "@/layouts/AuthLayout.vue";
import { toAppError } from "@/lib/http/errors";
import { useToastStore } from "@/app/stores/toast";
import { confirmPasswordReset } from "@/modules/auth/api";
import { passwordResetConfirmSchema } from "@/modules/auth/schemas";

const route = useRoute();
const toast = useToastStore();
const uid = computed(() => (typeof route.query.uid === "string" ? route.query.uid : ""));
const token = computed(() => (typeof route.query.token === "string" ? route.query.token : ""));
const linkValid = computed(() => Boolean(uid.value && token.value));
const loading = ref(false);
const error = ref("");
const completed = ref(false);
const { handleSubmit, setFieldError } = useForm({
  validationSchema: passwordResetConfirmSchema,
  initialValues: { password: "", passwordConfirm: "" },
});
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

const submit = handleSubmit(async (values) => {
  if (!linkValid.value) return;
  loading.value = true;
  error.value = "";
  try {
    await confirmPasswordReset({
      uid: uid.value,
      token: token.value,
      new_password: values.password,
      new_password_confirm: values.passwordConfirm,
    });
    completed.value = true;
    toast.show("Cập nhật mật khẩu thành công.", "success");
  } catch (requestError) {
    const appError = toAppError(requestError);
    if (appError.fields.new_password) setFieldError("password", appError.fields.new_password);
    else if (appError.fields.new_password_confirm) {
      setFieldError("passwordConfirm", appError.fields.new_password_confirm);
    } else {
      error.value = appError.fields.token || appError.message;
      toast.show(error.value, "error");
    }
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <AuthLayout>
    <template #title>Đặt mật khẩu mới</template>
    <template #subtitle>Chọn mật khẩu mạnh và không dùng lại mật khẩu cũ.</template>

    <AppAlert v-if="completed" variant="success" title="Đã cập nhật mật khẩu">
      Bạn có thể <AppLink to="/login">đăng nhập bằng mật khẩu mới</AppLink>.
    </AppAlert>
    <AppAlert v-else-if="!linkValid" variant="error" title="Liên kết không hợp lệ">
      Liên kết thiếu thông tin. Hãy <AppLink to="/forgot-password">gửi yêu cầu mới</AppLink>.
    </AppAlert>
    <template v-else>
      <form class="space-y-5" novalidate @submit="submit">
        <FormField
          v-slot="field"
          label="Mật khẩu mới"
          name="password"
          :error="passwordError"
          required
        >
          <BaseInput
            v-model="password"
            :id="field.id"
            name="new_password"
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
            name="new_password_confirm"
            type="password"
            autocomplete="new-password"
            :invalid="field.invalid"
            :aria-describedby="field.describedBy"
            required
            @blur="blurPasswordConfirm"
          />
        </FormField>
        <BaseButton type="submit" block :loading="loading" class="mt-2 text-sm font-black uppercase tracking-wider">
          Lưu mật khẩu mới
        </BaseButton>
      </form>
    </template>
  </AuthLayout>
</template>
