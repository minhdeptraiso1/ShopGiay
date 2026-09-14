# Phase 6 - Đổi trả và hoàn tiền

**Trạng thái:** Planned  
**Nhánh đề xuất:** `phase/06-returns-refunds`  
**Điều kiện bắt đầu:** Phase 5 Done; chốt cửa sổ đổi trả, điều kiện hàng và cách trả tiền COD.

## Mục tiêu

Hỗ trợ đổi size, trả hàng và hoàn tiền theo từng order line/số lượng, có phê duyệt, nhận/kiểm hàng và ledger
riêng; không hoàn quá số đã thanh toán.

## Sprint 1 - Customer request

- DB: `ReturnRequest`, `ReturnItem`, loại exchange/return, reason, evidence và status history.
- API/customer UI chọn order line, quantity còn đủ điều kiện và gửi request idempotent.
- Backend kiểm tra owner, thời hạn, trạng thái đơn, quantity đã request/return trước đó.

## Sprint 2 - Review, receive và inspect

- STAFF kiểm tra/nhận hàng theo permission; ADMIN hoặc permission riêng phê duyệt.
- Tách `approved`, `received`, `inspected`, `rejected`, `resolved`.
- Chỉ hàng qua kiểm tra và bán lại được mới nhập stock available; hàng lỗi đi disposition riêng.
- Exchange target variant được giữ tồn có thời hạn.

## Sprint 3 - Refund và exchange settlement

- DB: Refund, RefundAttempt, refund allocation theo payment/order line, provider reference unique.
- Tổng completed/pending refund không vượt số thực trả trừ refund trước.
- Online refund qua provider có retry/idempotency; COD có workflow bằng chứng chuyển khoản/thủ công.
- Đổi variant tính chênh lệch giữa giá hiện hành của hàng mới và net paid allocation của hàng cũ.

## Lỗi bắt buộc xử lý

Request quantity trùng, approve đồng thời, hàng nhận thiếu, target variant hết tồn, refund trùng, provider
timeout, refund callback đến muộn, đơn chưa paid và thay đổi quyết định sau inspection.

## Tiêu chí nghiệm thu

Partial return/exchange chạy FE-API-DB; permission/ownership đúng; stock chỉ quay lại sau inspection; refund
có ledger/trạng thái riêng, không vượt trần và chịu được retry; audit trail đầy đủ.

## Cần chốt trước khi duyệt

Số ngày đổi trả, lý do hợp lệ, ai chịu phí ship, policy chênh lệch giá và thông tin nhận hoàn COD.

