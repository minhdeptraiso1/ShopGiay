<script setup lang="ts">
import { storeToRefs } from "pinia";
import { useField, useForm } from "vee-validate";
import { ref } from "vue";

import BaseButton from "@/components/base/BaseButton.vue";
import BaseInput from "@/components/base/BaseInput.vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import FormField from "@/components/form/FormField.vue";
import AppLayout from "@/layouts/AppLayout.vue";
import { useAuthStore } from "@/modules/auth/stores/auth";
import { useProfile } from "@/modules/profile/composables/useProfile";
import { profileSchema } from "@/modules/profile/schemas";

const auth = useAuthStore();
const { user } = storeToRefs(auth);
const { loading, error, updateProfile } = useProfile();
const submitError = ref("");
const { handleSubmit } = useForm({
  validationSchema: profileSchema,
  initialValues: { fullName: user.value?.full_name || "" },
});
const { value: fullName, errorMessage: fullNameError, handleBlur } = useField<string>("fullName");

const submit = handleSubmit(async (values) => {
  submitError.value = "";
  try {
    await updateProfile(values.fullName);
  } catch {
    submitError.value = error.value;
  }
});
</script>

<template>
  <AppLayout>
    <section class="max-w-2xl space-y-6">
      <header>
        <p class="text-sm font-semibold text-[var(--color-primary)]">Tài khoản</p>
        <h1 class="mt-1 text-3xl font-bold tracking-tight">Hồ sơ cá nhân</h1>
        <p class="mt-2 text-[var(--color-text-muted)]">Bạn chỉ có thể cập nhật họ và tên.</p>
      </header>

      <AppAlert v-if="submitError" variant="error">{{ submitError }}</AppAlert>

      <form
        class="space-y-5 rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-white p-5 shadow-[var(--shadow-surface)] sm:p-6"
        novalidate
        @submit="submit"
      >
        <FormField
          v-slot="field"
          label="Email"
          name="profile-email"
          help="Email không thể thay đổi."
        >
          <BaseInput
            :model-value="user?.email || ''"
            :id="field.id"
            name="profile-email"
            type="email"
            autocomplete="email"
            :aria-describedby="field.describedBy"
            disabled
          />
        </FormField>

        <FormField v-slot="field" label="Họ và tên" name="fullName" :error="fullNameError">
          <BaseInput
            v-model="fullName"
            :id="field.id"
            name="full_name"
            autocomplete="name"
            :invalid="field.invalid"
            :aria-describedby="field.describedBy"
            @blur="handleBlur"
          />
        </FormField>

        <div class="flex justify-end">
          <BaseButton type="submit" :loading="loading">Lưu thay đổi</BaseButton>
        </div>
      </form>
    </section>
  </AppLayout>
</template>
