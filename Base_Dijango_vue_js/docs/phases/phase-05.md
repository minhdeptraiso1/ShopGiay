# Phase 5 - Khuyến mãi, yêu thích và đánh giá

**Trạng thái:** Planned  
**Nhánh đề xuất:** `phase/05-engagement`  
**Điều kiện bắt đầu:** Phase 4 Done; chốt chính sách voucher và moderation.

## Sprint 1 - Voucher

- DB: Voucher, rule/eligibility, usage reservation/redemption và per-order allocation.
- API admin CRUD; customer validate/apply trong quote và order.
- Backend kiểm tra active window, minimum spend, product/category scope, global/per-user limit.
- Khóa/counter atomic để nhiều checkout không vượt giới hạn.
- Phân bổ giảm giá theo order line bằng largest remainder để phục vụ hoàn tiền chính xác.

## Sprint 2 - Wishlist

- DB unique user+product; API list/toggle/remove có ownership.
- FE nút yêu thích ở list/detail và trang wishlist.
- Ghi event wishlist từ backend sau khi mutation thành công; không tin event giả từ client.

## Sprint 3 - Review và moderation

- Chỉ CUSTOMER có order line đủ điều kiện mới được đánh giá; một review/order line theo policy.
- Review có rating, nội dung, trạng thái moderation và audit action.
- Public chỉ thấy review approved; STAFF chỉ moderate khi có permission.
- Xử lý sản phẩm đã ẩn và user bị deactivate mà không phá lịch sử.

## Sprint 4 - Banner/content

- Banner/content block có lịch hiển thị, vị trí và trạng thái.
- Admin editor tối thiểu; storefront fallback khi ảnh hoặc nội dung thiếu.

## API/bảng chính

`/vouchers/validate/`, `/admin/vouchers/`, `/wishlist/`, `/products/{id}/reviews/`, `/admin/reviews/`,
`/banners/`; bảng voucher/usage/allocation, wishlist, review và banner.

## Tiêu chí nghiệm thu

Voucher được tính lại lúc đặt hàng và không oversubscribe; wishlist ownership đúng; review bắt buộc đã mua
và có moderation; banner chỉ hiện đúng lịch; event recommendation liên quan được ghi có nguồn xác thực.

