# Phase 6 - Đổi hàng

**Trạng thái:** Awaiting acceptance
**Nhánh đề xuất:** `phase/06-exchanges`
**Điều kiện bắt đầu:** Phase 5 Done; chốt cửa sổ đổi hàng, điều kiện sản phẩm và phí vận chuyển.

> Phase này chỉ xử lý đổi size/màu trong cùng sản phẩm. Không làm trả hàng lấy tiền, hoàn tiền COD,
> hoàn tiền VNPay hoặc đổi sang sản phẩm khác.

## Mục tiêu

Cho phép khách yêu cầu đổi một phần/toàn bộ số lượng của từng order line sang variant khác thuộc cùng
sản phẩm. Quy trình có phê duyệt, nhận hàng, kiểm hàng, giữ tồn variant mới, giao hàng thay thế và audit
history; không phát sinh refund hoặc payment settlement.

## Chính sách mặc định đề xuất

- Chỉ đơn `completed` mới được yêu cầu đổi.
- Cửa sổ đổi hàng: 30 ngày tính từ lúc đơn hoàn tất.
- Chỉ đổi size/màu sang variant đang hoạt động của chính sản phẩm đã mua.
- Giữ nguyên giá trị đã thanh toán; không thu thêm và không hoàn phần chênh lệch.
- Một order item có thể đổi từng phần, nhưng tổng quantity đã yêu cầu/đã đổi không vượt quantity mua.
- Chỉ hàng còn đủ điều kiện bán lại mới cộng về tồn available sau inspection.
- Variant thay thế được giữ tồn có thời hạn; hết hạn hoặc request bị từ chối/hủy phải hoàn reservation.

## Sprint 1 - Customer exchange request

- DB: `ExchangeRequest`, `ExchangeItem`, reason, evidence và status history.
- API/UI customer chọn order line, quantity và variant size/màu muốn đổi.
- Request có idempotency key; backend kiểm tra ownership, thời hạn, order status, cùng product và quantity
  còn đủ điều kiện.
- Customer xem danh sách/chi tiết tiến trình và chỉ được hủy trước khi nhân viên duyệt.

## Sprint 2 - Duyệt, nhận và kiểm hàng

- STAFF xem queue, tiếp nhận hàng, ghi quantity thực nhận, tình trạng và ghi chú kiểm tra.
- ADMIN hoặc permission riêng phê duyệt/từ chối trường hợp ngoại lệ.
- State machine: `pending -> approved -> received -> inspected -> replacement_ready ->
  replacement_shipped -> completed`;
  nhánh kết thúc khác là `rejected` hoặc `cancelled`.
- Chỉ hàng qua inspection và bán lại được mới tạo stock movement cộng tồn; hàng lỗi chuyển disposition
  riêng và không đi vào available stock.

## Sprint 3 - Giữ tồn và giao sản phẩm thay thế

- Giữ tồn target variant bằng reservation có expiry ngay khi request được duyệt.
- Khi inspection đạt, xác nhận xuất variant thay thế và tạo stock movement/audit tương ứng.
- Lưu shipment/tracking tối thiểu cho lượt giao đổi; hoàn reservation nếu request thất bại hoặc hết hạn.
- Hoàn tất request chỉ khi quantity nhận, quantity đạt inspection và quantity xuất thay thế khớp rule.
- Không tạo `Refund`, `RefundAttempt`, cổng thanh toán hoặc thông tin tài khoản ngân hàng.

## API/UI dự kiến

- Customer: `/exchanges/`, `/exchanges/{id}/`, action `cancel`, `confirm-received` và form tại chi tiết đơn.
- STAFF/ADMIN: `/admin/exchanges/`, action approve/reject/receive/inspect/prepare/ship.
- Customer UI: tạo yêu cầu, chọn variant thay thế, gửi bằng chứng và theo dõi timeline.
- Staff UI: queue, kiểm nhận từng item, disposition hàng cũ và chuẩn bị hàng thay thế.

## Kết quả triển khai 2026-09-29

- Backend đã có `ExchangeRequest`, `ExchangeItem`, reservation và status history; migration
  `exchanges.0001_initial` đã áp dụng trên PostgreSQL local.
- Customer API/UI đã hỗ trợ tạo yêu cầu từ đơn hoàn tất, chọn variant cùng sản phẩm, theo dõi và hủy khi
  còn `pending`. Mọi lần tạo đều dùng idempotency key có kiểm tra fingerprint payload.
- STAFF/ADMIN API/UI đã có queue và đầy đủ action `approve`, `reject`, `receive`, `inspect`, `prepare`,
  `ship`, stale-state protection và audit actor/note. Khách xác nhận nhận hàng đổi để hoàn tất.
- Duyệt yêu cầu trừ tồn target bằng reservation; reject/hết hạn hoàn tồn; hoàn tất chỉ cộng lại hàng cũ
  đã kiểm đạt. Command vận hành: `python manage.py release_expired_exchanges`.
- VNPay nhận `return_url` cùng origin cho từng payment attempt. Frontend truyền URL chi tiết đơn hiện tại,
  gửi signed return params về backend để xác minh và dọn query string; IPN dùng chung processor idempotent
  và vẫn là kênh server-to-server bắt buộc ở production.
- Customer có action xác nhận đã nhận khi đơn `shipped`; đơn chuyển `completed`, COD chuyển `paid` và UI
  mở liên kết đánh giá từng sản phẩm đã mua.
- Không có model/API/UI hoàn tiền; số tiền đơn hàng và payment không bị thay đổi bởi exchange.

## Kiểm thử đã chạy

- Backend: 84 test pass bằng SQLite fallback; Django check, migration drift và Ruff pass. PostgreSQL local
  hiện chưa chạy test được do mật khẩu trong `.env` không khớp instance ở cổng 5432.
- Frontend: 27 Vitest test pass, TypeScript/production build pass.
- VNPay sandbox end-to-end vẫn cần public HTTPS IPN URL được khai báo trong Merchant Admin; return về UI
  không được dùng thay IPN để xác nhận đã thanh toán.

## Lỗi bắt buộc xử lý

Request quantity trùng, approve đồng thời, hàng nhận thiếu, target variant không cùng sản phẩm, target hết
tồn, reservation hết hạn, request bị hủy sau khi đã giữ tồn, inspection không đạt và action dùng stale
state.

## Tiêu chí nghiệm thu

Partial exchange chạy đầy đủ FE-API-DB; permission/ownership đúng; không đổi vượt quantity đã mua; target
stock được giữ/giải phóng nguyên tử; stock hàng cũ chỉ quay lại sau inspection; state machine và audit trail
đầy đủ; không có bất kỳ luồng hoàn tiền nào.

## Giá trị cấu hình hiện tại cần nghiệm thu

Cửa sổ đổi là 30 ngày và thời gian giữ target variant là 1.440 phút. Lý do đang nhập tự do; phí giao đổi,
điều kiện tem/hộp/đã sử dụng và quyền duyệt ngoại lệ cần được chốt trước production.
