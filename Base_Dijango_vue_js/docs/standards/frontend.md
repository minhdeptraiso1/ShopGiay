# Chuẩn phát triển frontend

## 1. Kiến trúc và trách nhiệm

Code mới dùng Vue 3 Composition API, `<script setup lang="ts">` và TypeScript strict. Không dùng
Options API, `any` hoặc `@ts-ignore` để né lỗi; ngoại lệ tích hợp code cũ phải ghi lý do tại chỗ.

- `src/pages` và `src/modules/*/pages`: ghép layout/UI và nối composable; không chứa HTTP chi tiết.
- `src/components`: UI dùng chung, nhận props và phát events; không phụ thuộc nghiệp vụ cụ thể.
- `src/modules/*/components`: UI chỉ thuộc một module.
- `src/modules/*/composables`: điều phối use case, side effect và hành vi tái sử dụng.
- `src/modules/*/stores`: Pinia state thực sự dùng chung. State cục bộ ở component/composable.
- `src/modules/*/api`: endpoint và chuyển dữ liệu qua HTTP client chung.
- `src/modules/*/types`: hợp đồng dữ liệu; `schemas`: validation form bằng Zod/VeeValidate.
- `src/lib`: hạ tầng dùng chung, không chứa nghiệp vụ module.

Component, page, layout là `PascalCase.vue`; composable là `useSomething.ts`. Khi tách thành file riêng,
API/store/schema/type dùng `<module>.api.ts`, `<module>.store.ts`, `<module>.schema.ts`,
`<module>.types.ts`; các `index.ts` hiện tại được chấp nhận đến khi module cần tách, không đổi hàng loạt.
Biến/hàm dùng `camelCase`, hằng bất biến dùng `UPPER_SNAKE_CASE`.

Source hiện dùng `interface` cho object contract và `type` cho union/event; tiếp tục cách này. Event template
dùng kebab-case, khai báo emit có kiểu trong script. Props/emits phải rõ kiểu, không mutate props.

## 2. State và Vue

- Dùng `computed` cho dữ liệu suy ra; `watch` chỉ cho side effect cần thiết.
- Không dùng `watch` để giữ hai state đồng bộ khi có thể có một nguồn dữ liệu.
- Không đưa dữ liệu chỉ một page dùng vào Pinia và không persist toàn bộ store.
- Không tạo Controller/Repository class chỉ để bọc composable hoặc API call.
- Pages có thể quyết định navigation/toast; API module chỉ trả dữ liệu hoặc throw lỗi chuẩn hóa.

## 3. Import và dependency

Dùng `@/` khi import xuyên module hoặc từ hạ tầng/shared. Dùng đường dẫn tương đối cho file gần trong cùng
module. Module nghiệp vụ có thể phụ thuộc `components`, `lib`, `app` contract chung; shared không import từ
module nghiệp vụ. Tránh import vòng và không tạo barrel export rộng làm mờ nguồn symbol.

Không thêm dependency nếu Vue/Pinia/VeeValidate/Zod/Axios hoặc helper hiện có đáp ứng rõ ràng. pnpm và
`pnpm-lock.yaml` là nguồn dependency duy nhất.

## 4. Component và accessibility

Phải tái sử dụng `BaseButton`, `BaseLabel`, `BaseInput`, `FormField`, feedback và navigation component
hiện có. HTML `button`, `input`, `label`, `select`, `textarea` gốc chỉ nằm trong base component, hoặc ngoại
lệ semantic được giải thích khi chưa có base component phù hợp.

- Mở rộng `variant`, `size`, state hoặc slot thay vì copy component.
- Button mặc định `type="button"`; submit phải khai báo `type="submit"`.
- Control có loading/disabled/error/focus khi phù hợp; loading phải ngăn submit lặp.
- Label liên kết bằng `for`/`id`; ID mỗi instance phải duy nhất; error dùng `aria-describedby`.
- Không trim password. Không dùng button thay link hoặc ngược lại.
- Keyboard và focus ring phải hoạt động; không dùng màu làm tín hiệu duy nhất.
- Không dùng `!important`/`:deep()` rải rác. Ngoại lệ hiện hành: `!important` trong media query
  `prefers-reduced-motion` ở stylesheet toàn cục để vô hiệu motion.

Ví dụ form đúng:

```vue
<form @submit="submit">
  <FormField v-slot="field" label="Email" name="email" :error="emailError" required>
    <BaseInput
      v-model="email"
      :id="field.id"
      type="email"
      :invalid="field.invalid"
      :aria-describedby="field.describedBy"
    />
  </FormField>
  <BaseButton type="submit" :loading="isSubmitting">Lưu</BaseButton>
</form>
```

Sai vì viết lại control, thiếu base behavior và accessibility:

```vue
<input v-model="email" class="rounded border p-2" />
<button @click="save">Lưu</button>
```

Thêm variant: mở rộng union prop và mapping class trong `BaseButton.vue`, đặt default tương thích, thêm
test render/state; không copy toàn bộ class của button sang page.

## 5. Design system

Nguồn chính thức là `frontend/docs/design-system.md` và `src/assets/styles/tokens.css`. Thiết kế hiện hành
ưu tiên web app sáng, chuyên nghiệp, mobile-first; dùng token semantic thay giá trị màu/spacing/radius/font
hardcode ở page. Giá trị đặc thù chỉ chấp nhận khi token không biểu đạt đúng nhu cầu và không phá hệ thống.

UI UX Pro Max được dùng để rà soát: focus rõ, phản hồi loading, ARIA đồng bộ state, contrast tối thiểu
4.5:1 cho chữ thường, motion 150–300ms và `prefers-reduced-motion`. Khuyến nghị cyberpunk từ truy vấn tổng
quát không được áp dụng vì mâu thuẫn design system Soft UI Evolution hiện có; ưu tiên source hợp lý.

## 6. HTTP và authentication

- Chỉ dùng `src/lib/http/client.ts`; API module không tạo Axios client mới.
- Endpoint tập trung trong module API, giữ JSON `snake_case` đúng backend, không mapping tùy tiện.
- Dùng `toAppError` và phân biệt validation/401/403/429/network/5xx.
- Không dùng mock data che API lỗi; tránh toast trùng inline error.
- Access token chỉ ở memory; refresh token chỉ ở cookie HttpOnly. Không lưu token trong local/sessionStorage.
- Cookie-auth endpoint dùng CSRF. Refresh single-flight, retry request tối đa một lần; 403 không refresh.
- `authClient` tách interceptor để login/refresh/logout không lặp. Giữ điều phối logout/refresh hiện tại.
- Không báo logout server thành công nếu request thất bại; cờ `logout-pending` không chứa secret là ngoại lệ
  Web Storage đã được chấp nhận.

## 7. Kiểm tra

Vitest test hành vi component/composable; Playwright test luồng tích hợp quan trọng. Bug nên có regression
test khi khả thi. Với UI nhỏ, chạy component test và kiểm tra trực quan ở 375/768/1024/1440px, keyboard,
focus và reduced motion. ESLint/TypeScript tự kiểm tra kiểu và nhiều lỗi code; ranh giới tầng, việc tái sử
dụng base control và chất lượng UX vẫn cần code review.

