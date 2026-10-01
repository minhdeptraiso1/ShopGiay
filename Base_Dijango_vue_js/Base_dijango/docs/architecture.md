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
DB nếu invariant cần được DB bảo vệ.

## Tài khoản và phân quyền

Ba business role `CUSTOMER`, `STAFF`, `ADMIN` được lưu bằng Django Groups. Đăng ký công khai chỉ gán
`CUSTOMER`; client không được gửi role. `is_superuser` được ánh xạ thành quyền quản trị hệ thống nhưng
không thay thế kiểm tra backend. `auth/me` trả role và effective permissions để frontend dựng UX; mọi API
nhạy cảm vẫn kiểm tra permission hoặc ownership ở backend.

Địa chỉ giao hàng thuộc user. Service dùng transaction và row lock khi đổi địa chỉ mặc định; database có
conditional unique constraint để đảm bảo tối đa một default/user. Mọi lookup chi tiết đều scope theo user,
vì vậy địa chỉ của user khác được trả như không tồn tại.

Reset mật khẩu dùng token generator của Django, phản hồi trung tính ở bước yêu cầu để hạn chế dò email và
token tự mất hiệu lực sau lần đổi mật khẩu thành công. Local gửi email ra console; production phải cấu hình
frontend URL và email backend/provider rõ ràng.

## Thêm module

Tạo app trong `apps/<business_name>`, đăng ký trong settings, giữ API dưới `api/`, sinh migration bằng
`makemigrations`, đọc migration rồi viết test theo hành vi. Chỉ tách file thành package khi file thực sự
lớn; không tạo sẵn thư mục rỗng.

## Catalog, tồn kho và event

`apps.catalog` sở hữu catalog, variant, inventory và interaction event nền. Product chỉ chứa nội dung và
trạng thái publish; SKU, Decimal price, VND currency, size, color và tồn thuộc variant. Size thuộc brand để
không suy diễn size giữa các thương hiệu. Public selector chỉ đọc product published và prefetch variant,
inventory, image để tránh N+1.

Inventory balance là snapshot hiện tại; mọi service điều chỉnh khóa row variant/balance trong transaction
và tạo stock movement append-only chứa delta, before/after, reason và actor. Event client chỉ nhận allowlist
view/impression/click với schema version và idempotency UUID; purchase về sau chỉ do backend tạo.

## Cart, checkout và COD order

`apps.orders` sở hữu cart và order. Cart chỉ giữ variant/quantity và luôn đọc giá catalog hiện hành.
Checkout quote nhận address cùng danh sách cart item thuộc user, tải lại price/stock và tính subtotal,
shipping/discount/total ở backend.

Tạo COD khóa user và các inventory balance theo thứ tự ổn định trong một transaction. Idempotency UUID
được unique theo user và gắn với fingerprint request: retry cùng payload trả order cũ, còn dùng key cho
payload khác bị từ chối. Order/OrderItem lưu snapshot địa chỉ, tên sản phẩm, SKU, size, màu và mọi thành
phần tiền. Tồn được trừ khi order được tạo; customer chỉ tự hủy ở `pending_confirmation`, khi đó service
hoàn tồn và ghi status history/stock movement đúng một lần.

## Fulfillment và VNPay

STAFF/ADMIN đọc order queue qua selector và chỉ đổi trạng thái bằng state machine trong service. Client
phải gửi `expected_updated_at`; service khóa order row và trả conflict nếu dữ liệu đã stale. Mọi transition
ghi actor, old/new status và note vào status history. VNPay đã thanh toán không thể hủy nếu chưa có quy
quy trình hoàn tiền; refund hiện nằm ngoài phạm vi sản phẩm.

Order `vnpay` trừ available balance khi tạo và sinh `InventoryReservation` active có expiry 15 phút. URL
thanh toán dùng request reference riêng, idempotency UUID và HMAC-SHA512 trên query đã sắp xếp. Chỉ IPN
được ký hợp lệ, đúng merchant, amount và currency mới có quyền xác nhận paid; browser Return URL không
được cập nhật payment. IPN/event trùng được xử lý idempotent và không đổi tồn lần hai. Thành công capture
reservation; thất bại, hủy hoặc expiry hoàn balance qua stock movement.

Command `release_expired_reservations` thực thi định kỳ để hoàn giữ hàng; `reconcile_vnpay_payments` báo
các attempt/event cần đối soát. Không lưu raw IPN payload hoặc secret vào database/log.

## Engagement và khuyến mãi

`apps.engagement` sở hữu voucher, usage/allocation, wishlist, review và banner. Quote chỉ hiển thị kết quả
ước tính; khi tạo order, service khóa voucher và kiểm tra lại thời hạn, minimum spend, phạm vi cùng giới
hạn sử dụng trong cùng transaction với tồn kho. Discount được phân bổ nguyên đồng theo largest remainder
và lưu trên order line để bảo toàn tổng tiền và giá trị thực từng sản phẩm. VNPay giữ usage ở `reserved`,
IPN thành công chuyển `redeemed`; hủy/expiry chuyển `released`. COD được redeem ngay khi tạo.

Wishlist luôn scope theo user và event add/remove chỉ được backend ghi sau mutation thành công. Review chỉ
được tạo từ order item của chính user khi order `completed`; public selector chỉ trả `approved`, còn mọi
chỉnh sửa của customer đưa review về `pending`. STAFF/ADMIN được moderation, nhưng chỉ ADMIN quản lý
voucher/banner. Banner public được lọc theo trạng thái, vị trí và khoảng thời gian tại backend.

## JWT và logout

Login phát access 5 phút và refresh 7 ngày (đều cấu hình qua env). Mỗi lần refresh sẽ rotate token và
blacklist refresh cũ. Logout không yêu cầu access token: endpoint xác thực CSRF, blacklist refresh token
trong cookie nếu có rồi luôn xóa cookie. Thiết kế idempotent này cho phép kết thúc phiên ngay cả khi access
token đã hết hạn. Access token đã phát vẫn dùng được tới khi hết hạn; frontend phải xóa access token khỏi
memory ngay khi logout. Cơ chế hiện tại không phát hiện reuse để thu hồi toàn bộ token family và không
logout mọi thiết bị.

