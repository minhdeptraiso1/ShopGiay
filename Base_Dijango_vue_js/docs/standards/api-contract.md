# Chuẩn hợp đồng API

## 1. URL, method và status

- API nghiệp vụ có prefix `/api/v1/`; health check hiện ở `/health/` và schema/docs ở `/api/`.
- Giữ trailing slash theo Django hiện tại: mọi endpoint kết thúc bằng `/`.
- URL dùng danh từ `kebab-case` khi nhiều từ; JSON field dùng `snake_case` và frontend giữ nguyên.
- GET đọc, POST tạo/thực thi action, PUT thay toàn bộ, PATCH cập nhật một phần, DELETE xóa.
- Thành công: 200 cho read/update/action có body, 201 cho create, 204 cho thành công không body.
- Lỗi dùng 400 validation, 401 thiếu/hết hạn xác thực, 403 không đủ quyền/CSRF, 404 không có resource,
  409 conflict, 429 throttle, 5xx lỗi server. 403 không kích hoạt refresh token.

Không bọc response thành công hiện tại trong `data`. List có pagination theo DRF; object/action trả schema
trực tiếp. Không đổi hàng loạt response cũ chỉ để chuẩn hóa.

## 2. Error format

Mọi lỗi qua DRF handler có dạng:

```json
{
  "code": "invalid",
  "message": "Dữ liệu chưa hợp lệ.",
  "details": { "field_name": ["Thông báo cụ thể."] },
  "request_id": "client-or-server-request-id"
}
```

`code` ổn định cho logic client; `message` dành cho người dùng; `details` giữ lỗi field/non-field;
`request_id` dùng đối chiếu log. Client phải phân biệt 400, 401, 403, 429, network và 500; không suy diễn
thành công từ lỗi.

## 3. Dữ liệu

- Pagination chuẩn DRF PageNumberPagination: `count`, `next`, `previous`, `results`; mặc định 20 item.
- Datetime dùng ISO 8601 có timezone; backend lưu/serialize timezone-aware UTC, UI đổi sang timezone hiển thị.
- `null` nghĩa là không có giá trị; chuỗi rỗng chỉ dùng khi field cho phép blank và có nghĩa riêng. Field
  optional có thể vắng trong request; response phải theo schema, không thay `null` bằng `""` tùy tiện.
- ID hiện là integer dương (`BigAutoField`) và JSON number. Không giả định UUID cho module mới nếu model
  chưa chọn UUID.
- Enum biểu diễn bằng giá trị ổn định dạng string/integer từ choices, không bằng label dịch.
- Tiền tệ tương lai dùng decimal chính xác serialize thành chuỗi và mã tiền ISO 4217 ở field riêng; không
  dùng float.

## 4. Authentication và CSRF

Login trả `{access, user}` và đặt refresh token cookie HttpOnly. Refresh đọc cookie, rotate/blacklist token
cũ và trả `{access}`. Access token gửi Bearer và chỉ giữ trong memory. Login/refresh/logout dùng CSRF token
từ `/api/v1/auth/csrf/`; logout thành công trả 204. Không lưu token trong local/sessionStorage.

## 5. Thay đổi và OpenAPI

Xóa/đổi tên field, đổi type/nullability/ý nghĩa, siết validation, đổi status/error code hoặc URL là breaking
change. Cần version/migration window và cập nhật frontend đồng bộ. Thêm optional response field thường
backward-compatible nhưng vẫn phải cập nhật schema/test.

`Base_dijango/schema.yml` là snapshot được track, sinh từ drf-spectacular và không sửa tay. Khi đổi API,
cập nhật serializer/schema annotation, sinh lại và chạy `spectacular --validate --fail-on-warn`. CI
validate rồi kiểm tra diff để phát hiện quên commit schema. Hiện schema mô tả endpoint chính nhưng error
response dùng `OpenApiResponse` mô tả ngắn ở một số route, chưa khai báo schema error chung cho mọi
status; xem lộ trình trong architecture decisions.
