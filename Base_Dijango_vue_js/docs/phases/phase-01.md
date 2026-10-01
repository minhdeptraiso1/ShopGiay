# Phase 1 - Tài khoản, phân quyền và khung giao diện

**Trạng thái:** Done
**Nhánh đề xuất:** `phase/01-accounts-rbac`  
**Điều kiện bắt đầu:** Phase 0 Done; chốt email provider hoặc cho phép backend console trong local.

## Phạm vi và quyết định mặc định

- Khách tự đăng ký thành CUSTOMER; đặt hàng bắt buộc đăng nhập.
- Dùng Django Groups làm role bundle `CUSTOMER`, `STAFF`, `ADMIN`; backend kiểm tra permission và ownership.
- `is_superuser` dành cho quản trị hệ thống, không thay cho business role thông thường.
- Storefront có route public; admin layout chỉ cho STAFF/ADMIN theo permission.

## Sprint 1 - Đăng ký và RBAC xuyên suốt

| ID | Loại | Công việc | Phụ thuộc | Đầu ra / nghiệm thu | Trạng thái |
|---|---|---|---|---|---|
| P01-S01-DB01 | DB | Seed Groups/permissions idempotent; gán CUSTOMER khi đăng ký | P0 | Role tồn tại ổn định, migration/data migration an toàn | Completed |
| P01-S01-BE01 | BE | Registration service/API và policy active/password | DB01 | User tạo đúng role, email unique CI, password hash | Completed |
| P01-S01-BE02 | BE | Permission helpers và output role/effective permissions | DB01 | API không dựa vào nút ẩn ở FE | Completed |
| P01-S01-FE01 | FE | Trang đăng ký, validation, loading/error/success | BE01 | Đăng ký rồi đăng nhập được | Completed |
| P01-S01-TEST01 | Test | Test role assignment, escalation và contract | BE/FE | Không tự gán STAFF/ADMIN qua payload | Completed |

## Sprint 2 - Hồ sơ và địa chỉ

| ID | Loại | Công việc | Phụ thuộc | Đầu ra / nghiệm thu | Trạng thái |
|---|---|---|---|---|---|
| P01-S02-DB01 | DB | Address thuộc User, default flag và index ownership | S01 | Tối đa một địa chỉ mặc định/user | Completed |
| P01-S02-BE01 | BE | CRUD `/api/v1/account/addresses/` | DB01 | Chỉ chủ sở hữu đọc/sửa/xóa | Completed |
| P01-S02-FE01 | FE | Profile và quản lý địa chỉ responsive | BE01 | Có empty/loading/error và chọn mặc định | Completed |
| P01-S02-TEST01 | Test | API/component test ownership | BE/FE | User A không truy cập address user B | Completed |

## Sprint 3 - Reset password và layout

- `POST /api/v1/auth/password-reset/` luôn trả thông báo trung tính.
- `POST /api/v1/auth/password-reset/confirm/` dùng token một lần, có expiry.
- Bổ sung storefront layout, admin layout, route meta permissions và trang 403.
- Email local có thể dùng console backend nhưng nghiệm thu tích hợp thật cần provider đã chốt.

## API và dữ liệu dự kiến

- API: registration, password reset, address CRUD; mở rộng `auth/me` với role/quyền cần thiết.
- Bảng: `accounts_address`; Django `auth_group`, `auth_permission` và quan hệ user-group.
- Màn hình: đăng ký, quên/đặt lại mật khẩu, hồ sơ, địa chỉ, storefront shell, admin shell, 403.

## Ma trận tối thiểu

| Năng lực | Guest | CUSTOMER | STAFF | ADMIN |
|---|---:|---:|---:|---:|
| Xem storefront | Có | Có | Có | Có |
| Sửa hồ sơ/địa chỉ của mình | Không | Có | Có | Có |
| Truy cập vận hành | Không | Không | Theo permission | Có |
| Quản lý nhân viên/quyền | Không | Không | Không | Có |

## Tiêu chí nghiệm thu

Đăng ký/login/logout/reset/profile/address chạy FE-API-DB; permission và ownership có test; route public
không ép login; không thể privilege escalation; OpenAPI và E2E cập nhật.

## Kết quả thực hiện

- Migration tạo ba role `CUSTOMER`, `STAFF`, `ADMIN`, backfill customer hiện có và thêm bảng địa chỉ với
  constraint tối đa một địa chỉ mặc định trên mỗi user.
- Hoàn tất API đăng ký, reset mật khẩu token một lần, `auth/me` có role/quyền, CRUD địa chỉ theo ownership
  và endpoint admin được bảo vệ ở backend.
- Hoàn tất các màn hình đăng ký, quên/đặt lại mật khẩu, hồ sơ/địa chỉ, storefront shell, admin shell và 403;
  route guard chỉ hỗ trợ UX, backend vẫn là nơi quyết định quyền.
- Local dùng console email, test dùng LocMem. Production fail-fast nếu thiếu cấu hình email và frontend URL.
- Backend test: 33 pass, coverage 91%. Frontend unit/component: 16 pass. Playwright: 4 pass trên desktop và
  mobile. Migration rehearsal và OpenAPI validation pass trên SQLite/LocMem fallback.
- Chưa xác minh lại integration bằng PostgreSQL/Redis thật do Docker API không khả dụng trong môi trường.

## Cần chốt trước khi duyệt

Email provider production vẫn cần cấu hình khi triển khai. Hiện tại Django Groups cho phép nhiều role,
đăng ký công khai chỉ gán `CUSTOMER`; địa chỉ bắt buộc người nhận, số điện thoại, tỉnh, huyện, xã và chi tiết.

## Approval gate

Phase 1 được người dùng nghiệm thu khi yêu cầu chuyển sang Phase 2 ngày 2026-09-14.
