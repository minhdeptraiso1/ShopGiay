# Design system frontend

Thiết kế được tạo theo workflow UI UX Pro Max với truy vấn “admin account portal professional minimal
light responsive”. Hướng chọn là **Soft UI Evolution**: sáng, chuyên nghiệp, depth nhẹ và tương phản rõ;
không dùng gradient tím, biểu đồ hay icon trang trí.

- Màu: primary `#1E40AF`, nền `#EFF6FF`, surface trắng, text `#172554`, border `#BFDBFE`.
- Trạng thái: success `#15803D`, warning `#A16207`, error `#B91C1C`; luôn kèm chữ, không chỉ dùng màu.
- Chữ: Inter nếu có, sau đó dùng system sans; body 16px trên mobile, line-height 1.5.
- Khoảng cách: nhịp 4/8px; section 24–32px; control cao tối thiểu 44px.
- Bo góc: 8/12/16px; shadow xanh rất nhẹ để phân cấp surface.
- Focus: ring xanh 3px, không xóa outline nếu không có thay thế.
- Motion: 180ms cho hover/focus; tôn trọng `prefers-reduced-motion`.
- Layout: mobile-first từ 320px, kiểm tra chính ở 375/768/1024/1440px; content tối đa 1120px.

Token nguồn nằm ở `src/assets/styles/tokens.css`. Mọi button/input/label/error dùng component trong
`src/components`; biến thể mới phải mở rộng prop `variant`/`size`, không sao chép nhóm class sang page.
