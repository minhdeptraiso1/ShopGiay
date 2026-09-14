# Kiến trúc

## Tổng quan

Dự án là **modular monolith**: một deployment Django, nhưng mã nguồn chia theo module nghiệp vụ trong
`apps/`. Django MVT vẫn được giữ: model quản lý dữ liệu; view điều phối HTTP; serializer thay vai trò
biểu diễn/kiểm tra dữ liệu cho REST API. Không có template nghiệp vụ, controller song song hoặc
repository bọc Django ORM.

## Trách nhiệm

- `config/`: URL gốc, ASGI/WSGI và settings theo môi trường.
- `apps/<module>/models.py`: schema, quan hệ, constraint và index.
- `managers.py`: hành vi QuerySet/manager gắn trực tiếp với model.
- `api/serializers.py`: hợp đồng input/output và validation ở biên HTTP.
- `api/views.py`: authentication, permission, điều phối service và response.
- `services.py`: nghiệp vụ ghi; dùng `transaction.atomic` khi có nhiều thay đổi liên quan.
- `selectors.py`: truy vấn đọc phức tạp hoặc dùng lại; truy vấn đơn giản có thể ở view/service.
- `common/`: request ID và exception handler dùng chung thật sự.

Luồng ghi: URL → view → input serializer → service → model/database → output serializer. Luồng đọc:
URL → view → selector (nếu truy vấn đáng kể) → output serializer.

DTO chỉ thêm bằng `dataclass(frozen=True)` khi cần truyền một cấu trúc nội bộ ổn định qua nhiều tầng;
không tạo DTO giống hệt serializer. Enum của model dùng `TextChoices`/`IntegerChoices` và có constraint
DB nếu invariant cần được DB bảo vệ. Accounts hiện không có tập giá trị nghiệp vụ nên không tạo enum giả.

## Thêm module

Tạo app trong `apps/<business_name>`, đăng ký trong settings, giữ API dưới `api/`, sinh migration bằng
`makemigrations`, đọc migration rồi viết test theo hành vi. Chỉ tách file thành package khi file thực sự
lớn; không tạo sẵn thư mục rỗng.

## JWT và logout

Login phát access 5 phút và refresh 7 ngày (đều cấu hình qua env). Mỗi lần refresh sẽ rotate token và
blacklist refresh cũ. Logout chỉ blacklist **refresh token được gửi lên**, sau khi xác nhận token thuộc
user của access token hiện tại. Access token đã phát vẫn dùng được tới khi hết hạn; frontend phải xóa cả
hai token. Cơ chế hiện tại không phát hiện reuse để thu hồi toàn bộ token family và không logout mọi thiết
bị.

