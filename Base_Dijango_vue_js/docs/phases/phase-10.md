# Phase 10 - Kiểm thử tổng thể và chuẩn bị triển khai

**Trạng thái:** Planned  
**Nhánh đề xuất:** `phase/10-release-readiness`  
**Điều kiện bắt đầu:** Các phase chức năng đã `Done` hoặc phần hoãn có quyết định được duyệt.

## E2E, security và concurrency

- E2E catalog, đăng ký, giỏ hàng, COD, VNPay sandbox, đơn hàng, đánh giá, đổi hàng và fulfillment.
- Kiểm tra authorization, ownership, concurrent stock, voucher limit, webhook và exchange race.
- Kiểm tra CSRF, CORS, cookie, log redaction, upload validation và rate limit.

## UX, accessibility và performance

- Responsive 375/768/1024/1440; keyboard, focus, label/error semantics và reduced motion.
- Kiểm tra loading/empty/error/offline; đo API và frontend bundle/Web Vitals.

## Migration và release rehearsal

- Chạy migration trên staging có backup; kiểm tra forward và chiến lược forward-fix.
- Hoàn thiện env, backup/restore, deploy, health check, smoke test, rollback và xử lý sự cố.
- Kiểm tra HTTPS, hosts/CORS/CSRF, secure cookies, storage, jobs, quan sát hệ thống và xoay secret.

## Tiêu chí nghiệm thu

- Critical E2E, permission và concurrency pass; không còn P0/P1.
- Không có migration drift hay secret bị track.
- Backup/restore và release/rollback được diễn tập trên môi trường thử nghiệm.
- Chỉ deploy production khi có cho phép riêng.
