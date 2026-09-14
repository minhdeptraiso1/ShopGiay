# Phase 9 - Kiểm thử tổng thể và chuẩn bị triển khai

**Trạng thái:** Planned  
**Nhánh đề xuất:** `phase/09-release-readiness`  
**Điều kiện bắt đầu:** Các phase chức năng đã `Done` hoặc phần hoãn có quyết định được duyệt.

## Sprint 1 - E2E, security và concurrency

- E2E guest catalog, registration, address, cart, COD, online payment sandbox, order tracking, review,
  return/refund và admin fulfillment.
- Kiểm tra horizontal/vertical authorization và object ownership với ID của user khác.
- Test concurrent stock, voucher limit, duplicate order, duplicate/out-of-order webhook và refund race.
- Kiểm tra CSRF, CORS, cookie flags, secret/log redaction, upload validation và rate limit assumptions.

## Sprint 2 - UX, accessibility và performance

- Responsive tại 375/768/1024/1440; keyboard, focus, label/error semantics và reduced motion.
- Kiểm tra loading/empty/error/offline ở các luồng quan trọng.
- Đo API list/detail/checkout/recommendation và frontend bundle/Web Vitals trên dữ liệu gần thực tế.
- Sửa regression trong phạm vi; thay đổi kiến trúc/performance lớn phải trình duyệt.

## Sprint 3 - Migration và release rehearsal

- Chạy migration trên bản sao/staging có backup; kiểm tra forward và rollback/forward-fix strategy.
- Tài liệu env names, local/staging/prod, seed/demo không chứa credential production.
- Runbook backup/restore, deploy, health check, smoke test, rollback và incident contacts.
- Production checklist: HTTPS/reverse proxy, hosts/CORS/CSRF, secure cookies, storage, scheduled jobs,
  observability, database/Redis backup và secret rotation.

## Quality gates cuối

```powershell
cd Base_dijango
uv run ruff check .
uv run ruff format --check .
uv run python manage.py check --settings=config.settings.test
uv run python manage.py makemigrations --check --dry-run --settings=config.settings.test
uv run pytest --cov --cov-report=term-missing
uv run python manage.py spectacular --validate --fail-on-warn --file schema.yml --settings=config.settings.test

cd ..\frontend
pnpm typecheck
pnpm lint
pnpm format:check
pnpm test
pnpm build
pnpm test:e2e
```

## Tiêu chí nghiệm thu

- Critical E2E, permission và concurrency scenarios pass.
- Không có migration drift, secret bị track hoặc blocker P0/P1 chưa xử lý.
- Backup/restore và release/rollback được diễn tập trên môi trường thử nghiệm.
- Hướng dẫn vận hành đủ để người khác triển khai và rollback.
- Bản ở trạng thái `Awaiting acceptance`; chỉ deploy production khi có cho phép riêng.

## Ngoài phạm vi tự động

Không push, merge, xóa dữ liệu, chạy migration production, đổi DNS, tạo tài nguyên trả phí hoặc deploy thật
nếu chưa được người dùng cho phép rõ ràng.

