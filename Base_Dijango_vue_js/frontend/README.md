# Vue frontend

Frontend Vue 3 + TypeScript strict cho Django REST API. Access token chỉ nằm trong bộ nhớ; refresh token
do backend giữ trong cookie `HttpOnly`, nên JavaScript không thể đọc hoặc lưu token này.

## Chạy local

Thực hiện phần cài PostgreSQL, Redis, `.env` và backend theo `../README.md`. Sau đó mở terminal thứ hai
từ root repository và chạy:

```powershell
cd frontend
corepack enable
corepack prepare pnpm@11.19.0 --activate
pnpm install --frozen-lockfile
pnpm dev
```

Mở <http://localhost:5173> và đăng nhập bằng `demo@example.com` / `123456`. Vite proxy `/api` và
`/health` đến `http://127.0.0.1:8000`, vì vậy local không cần đặt `VITE_API_BASE_URL`.

## Cấu trúc

- `src/components`: component dùng lại (`BaseButton`, `BaseInput`, `FormField`, alert/toast/link).
- `src/layouts`: layout đăng nhập và layout ứng dụng.
- `src/modules/auth`: API, store Pinia, schema Zod, auth lifecycle và trang đăng nhập.
- `src/modules/profile`: API, validation và trang cập nhật `full_name`.
- `src/lib/http`: Axios client, chuẩn hóa lỗi và CSRF.
- `src/app/router`: route `/login`, `/`, `/profile`, 404 và route guards.

Design system dùng Inter, màu primary xanh dương, nền xanh rất nhạt, khoảng cách theo lưới 4/8 px,
focus ring rõ ràng và breakpoint mobile-first. Chi tiết ở `docs/design-system.md`.

## Auth, CSRF và nhiều tab

Trước login/refresh/logout, client lấy CSRF token từ `GET /api/v1/auth/csrf/` rồi gửi header
`X-CSRFToken`; mọi request bật `withCredentials`. Login trả access token và user trong JSON, còn refresh
token chỉ được đặt trong cookie `HttpOnly`. Khi access token hết hạn, Axios chỉ retry đúng một lần sau
response `401`; response `403`, lỗi mạng hoặc lỗi server không tự xóa phiên.

Trong cùng một tab, refresh dùng single-flight. Giữa nhiều tab, Web Locks tuần tự hóa refresh và
BroadcastChannel phát sự kiện logout/session. Trình duyệt không hỗ trợ Web Locks vẫn hoạt động bằng
single-flight từng tab, nhưng không thể đảm bảo tuyệt đối hai tab không đồng thời xoay refresh token.

Logout xóa access/user trong bộ nhớ trước. Nếu backend đang offline, frontend giữ một cờ
`logout-pending` không nhạy cảm trong localStorage và thử logout lại; frontend không thể tự xóa cookie
`HttpOnly`. Không lưu access/refresh token trong localStorage hay sessionStorage.

Production nên phục vụ frontend và API cùng HTTPS origin qua reverse proxy. Nếu khác origin, khai báo
chính xác `CORS_ALLOWED_ORIGINS` và `CSRF_TRUSTED_ORIGINS`, bật credentials, giữ
`REFRESH_TOKEN_COOKIE_SECURE=true`, đồng thời cân nhắc `SameSite` theo topology thực tế.

## Kiểm tra

```cmd
pnpm typecheck
pnpm lint
pnpm format:check
pnpm test
pnpm build
pnpm exec playwright install chromium
pnpm test:e2e
```

Playwright cần backend ở cổng `8000`, frontend ở `5173`, PostgreSQL/Redis hoạt động và tài khoản demo đã
được seed. Không chạy lệnh cài Chromium mỗi lần nếu máy đã có browser Playwright.
