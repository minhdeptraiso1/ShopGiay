# Kế hoạch phát triển theo phase

Tài liệu này là mục lục triển khai website bán giày. Mỗi phase là một approval gate độc lập; duyệt
roadmap hoặc checkout một nhánh không đồng nghĩa với duyệt triển khai phase tiếp theo.

## Quy trình trạng thái

`Planned -> Awaiting approval -> In progress -> Awaiting acceptance -> Done`

Chỉ chuyển sang `In progress` khi có xác nhận rõ như `Duyệt Phase 2` hoặc `Bắt đầu Phase 2`. Chỉ chuyển
sang `Done` sau khi người dùng nghiệm thu. Khi bị chặn, ghi `Blocked` kèm nguyên nhân và phương án.

## Quy trình Git đề xuất

Từ nhánh đã nghiệm thu của phase trước:

```powershell
git switch main
git pull --ff-only
git switch -c phase/00-base
```

Thay `00-base` bằng tên nhánh trong bảng. Không push, merge, xóa nhánh hoặc deploy nếu chưa được cho
phép. Trước khi bắt đầu luôn kiểm tra `git status --short` để không ghi đè thay đổi hiện có.

| Phase | File | Nhánh đề xuất | Phụ thuộc | Trạng thái ban đầu |
|---|---|---|---|---|
| 0 | [Khảo sát và chuẩn hóa base](phase-00.md) | `phase/00-base` | Không | Awaiting approval |
| 1 | [Tài khoản, phân quyền, khung UI](phase-01.md) | `phase/01-accounts-rbac` | Phase 0 Done | Planned |
| 2 | [Sản phẩm, biến thể và kho](phase-02.md) | `phase/02-catalog-inventory` | Phase 1 Done | Planned |
| 3 | [Giỏ hàng và COD](phase-03.md) | `phase/03-cart-cod` | Phase 2 Done | Done |
| 4 | [Xử lý đơn và thanh toán online](phase-04.md) | `phase/04-fulfillment-payment` | Phase 3 Done | Done |
| 5 | [Khuyến mãi, yêu thích, đánh giá](phase-05.md) | `phase/05-engagement` | Phase 4 Done | Awaiting acceptance |
| 6 | [Đổi hàng](phase-06.md) | `phase/06-exchanges` | Phase 5 Done | Planned |
| 7 | [Recommendation System](phase-07.md) | `phase/07-recommendations` | Event từ Phase 2-6 | Awaiting acceptance |
| 8 | [Báo cáo và vận hành](phase-08.md) | `phase/08-reporting-operations` | Phase 7 Done | Planned |
| 9 | [Kiểm thử và release readiness](phase-09.md) | `phase/09-release-readiness` | Phase 1-8 Done | Planned |

## Quy ước dùng chung

- Backend là nguồn quyết định về quyền, ownership, giá, giảm giá, tồn và trạng thái.
- API giữ `/api/v1/`, trailing slash, JSON `snake_case`, success không envelope và error
  `code/message/details/request_id`.
- Tiền dùng decimal và mã tiền tệ; không dùng floating point.
- Luồng ghi nhạy cảm phải có transaction, concurrency control và idempotency phù hợp.
- Đơn hàng lưu snapshot sản phẩm, SKU, size, màu, giá và giảm giá.
- Không hard-delete dữ liệu đã được giao dịch tham chiếu.
- Mỗi sprint phải cho ra một lát cắt chạy được từ UI qua API tới database.
- Khi hoàn tất một phase, cập nhật checklist, kết quả test, blocker và chuyển sang
  `Awaiting acceptance`; không tự bắt đầu phase tiếp theo.
