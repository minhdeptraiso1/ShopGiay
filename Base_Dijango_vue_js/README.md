# Base Django REST Framework + Vue.js

Repository mẫu gồm backend Django REST Framework và frontend Vue 3. Dự án dùng PostgreSQL, Redis,
JWT (refresh token trong cookie `HttpOnly`), CSRF, OpenAPI, TypeScript strict và các quality gate dùng
chung giữa local/CI.

## Cấu trúc repository

```text
.
├── Base_dijango/       # Django 5.2 + DRF
├── frontend/           # Vue 3 + TypeScript + Vite
├── docs/standards/     # Quy ước phát triển FE/BE/API
└── AGENTS.md           # Quy trình bắt buộc trước khi sửa code
```

> Tên thư mục `Base_dijango` được giữ nguyên để không làm hỏng đường dẫn/import hiện có.

## Yêu cầu

- Git.
- Python 3.12–3.14 và [uv](https://docs.astral.sh/uv/).
- Node.js 24 và pnpm 11.19.0 (nên bật qua Corepack).
- Docker Desktop để chạy PostgreSQL và Redis. Có thể dùng dịch vụ cài local nếu sửa `.env` tương ứng.

## Clone và chạy local

### 1. Clone repository

```powershell
git clone https://github.com/minhdeptraiso1/Base_Dijango_vue_js.git
cd Base_Dijango_vue_js
```

### 2. Khởi động PostgreSQL và Redis

```powershell
cd Base_dijango
docker compose up -d db redis
Copy-Item .env.example .env
```

Mở `Base_dijango/.env` và đổi hai dòng sau để khớp cổng Docker Compose:

```dotenv
DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5433/dijango
REDIS_URL=redis://127.0.0.1:6380/1
```

Tạo hai secret khác nhau rồi thay vào `DJANGO_SECRET_KEY` và `JWT_SIGNING_KEY`:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Chạy lệnh trên hai lần. Không commit `.env`.

### 3. Cài và chạy backend

Vẫn tại thư mục `Base_dijango`:

```powershell
py -m venv .tools
.\.tools\Scripts\python.exe -m pip install uv==0.8.22
$env:UV_CACHE_DIR = "$PWD\.uv-cache"
.\.tools\Scripts\uv.exe --version
.\.tools\Scripts\uv.exe sync --frozen
```

Thư mục `.tools` bị Git ignore nên ở máy hoặc checkout mới chỉ cần chạy hai lệnh đầu một lần. Sau khi
`UV_CACHE_DIR` chỉ cần đặt một lần cho mỗi terminal PowerShell. Sau khi PostgreSQL trả về `True`, chạy
riêng từng lệnh và đợi dấu nhắc PowerShell xuất hiện lại:

```powershell
.\.tools\Scripts\uv.exe run python manage.py migrate
```

```powershell
.\.tools\Scripts\uv.exe run python manage.py seed_dev_user
```

Tạo thêm ba tài khoản kiểm thử theo role:

```powershell
.\.tools\Scripts\uv.exe run python manage.py seed_dev_accounts
```

Tạo catalog mẫu gồm 6 mẫu giày, tất thể thao, bình xịt vệ sinh, bộ bàn chải, biến thể, ảnh và tồn kho để
storefront có dữ liệu thật:

```powershell
.\.tools\Scripts\uv.exe run python manage.py seed_catalog
```

Tạo voucher `WELCOME10` và banner mẫu cho Phase 5:

```powershell
.\.tools\Scripts\uv.exe run python manage.py seed_engagement
```

```powershell
.\.tools\Scripts\uv.exe run python manage.py runserver
```

Backend chạy tại <http://127.0.0.1:8000>. Khi `API_DOCS_ENABLED=true`, Swagger ở
<http://127.0.0.1:8000/api/docs/>.

### 4. Cài và chạy frontend

Mở terminal thứ hai tại root repository:

```powershell
cd frontend
corepack enable
corepack prepare pnpm@11.19.0 --activate
pnpm install --frozen-lockfile
pnpm dev
```

Mở <http://localhost:5173>. Tài khoản dev mặc định:

| Role | Email | Mật khẩu mặc định |
|---|---|---|
| Demo CUSTOMER | `demo@example.com` | `123456` |
| CUSTOMER | `customer@example.com` | `123456` |
| STAFF | `staff@example.com` | `123456` |
| ADMIN | `admin@example.com` | `123456` |

Mật khẩu thực tế lấy từ `DEMO_USER_PASSWORD` trong `Base_dijango/.env`. Hai lệnh seed chỉ chạy khi
`DEBUG=True`; không dùng các tài khoản này ở production.

Vite proxy `/api` và `/health` sang backend cổng `8000`, vì vậy local mặc định không cần đặt
`VITE_API_BASE_URL`.

Các màn Phase 5 dùng để kiểm thử:

- Khách hàng: `/wishlist`, `/cart` (áp voucher), `/products/{slug}` (wishlist và đánh giá).
- STAFF: `/admin/engagement` để duyệt/từ chối đánh giá.
- ADMIN: `/admin/engagement` để quản lý thêm voucher và banner.

Các màn Phase 6 dùng để kiểm thử:

- CUSTOMER: mở đơn `completed` tại `/orders/{id}`, chọn **Yêu cầu đổi hàng**, hoặc theo dõi tại
  `/exchanges`.
- STAFF/ADMIN: `/admin/exchanges` để duyệt, nhận hàng, kiểm hàng, chuẩn bị giao đổi và hoàn tất.

Các màn Phase 7 dùng để kiểm thử:

- Mọi khách: `/` xem sản phẩm phổ biến; `/products/{slug}` xem sản phẩm tương tự và đồ đi kèm.
- Khách đã đăng nhập: `/` có thêm gợi ý cá nhân hóa từ lịch sử tương tác.
- STAFF/ADMIN: `/admin/recommendations` xem request, impression, CTR, add-to-cart, purchase và coverage.
- Tự hoàn tồn reservation đổi hàng hết hạn (chạy định kỳ trong production):

```powershell
cd Base_dijango
.\.tools\Scripts\uv.exe run python manage.py release_expired_exchanges
```

Thanh toán VNPay truyền URL chi tiết đơn hiện tại làm `vnp_ReturnUrl`, vì vậy sau thanh toán trình duyệt
quay lại đúng `/orders/{id}`. Frontend gửi toàn bộ tham số `vnp_*` về backend; backend chỉ cập nhật thanh
toán sau khi xác minh checksum, merchant, amount, mã giao dịch và ownership. IPN vẫn phải cấu hình để xử
lý giao dịch khi khách đóng trình duyệt trước khi quay về website.

Khi STAFF chuyển đơn sang `shipped`, khách hàng có nút **Đã nhận được hàng** trên chi tiết đơn. Sau khi
xác nhận, đơn thành `completed`; khách có thể chọn **Đánh giá sản phẩm** cho từng order item.

> Để test VNPay end-to-end, `vnp_ReturnUrl` có thể là frontend local, nhưng IPN phải là URL backend HTTPS
> public (ví dụ `https://<domain>/api/v1/payments/vnpay/ipn/`) và phải khai báo trong Merchant Admin.
> Không đưa `VNPAY_HASH_SECRET`, thông tin đăng nhập merchant hoặc dữ liệu thẻ test vào Git.

## Kiểm tra chất lượng

Backend (chạy trong `Base_dijango`):

```powershell
.\.tools\Scripts\uv.exe run ruff check .
.\.tools\Scripts\uv.exe run ruff format --check .
.\.tools\Scripts\uv.exe run python manage.py check --settings=config.settings.test
.\.tools\Scripts\uv.exe run python manage.py makemigrations --check --dry-run --settings=config.settings.test
.\.tools\Scripts\uv.exe run pytest
.\.tools\Scripts\uv.exe run python manage.py spectacular --validate --fail-on-warn --file schema.yml --settings=config.settings.test
```

Frontend (chạy trong `frontend`):

```powershell
pnpm typecheck
pnpm lint
pnpm format:check
pnpm test
pnpm build
```

E2E cần backend, frontend, PostgreSQL, Redis và user demo đang chạy:

```powershell
pnpm exec playwright install chromium
pnpm test:e2e
```

## Tài liệu phát triển

Trước khi sửa code, đọc [AGENTS.md](AGENTS.md) và file `AGENTS.md` trong phạm vi tương ứng:

- [Chuẩn frontend](docs/standards/frontend.md)
- [Chuẩn backend](docs/standards/backend.md)
- [Hợp đồng API](docs/standards/api-contract.md)
- [Quyết định kiến trúc](docs/standards/architecture-decisions.md)
- [Kiến trúc backend](Base_dijango/docs/architecture.md)
- [API Phase 3 cho frontend](docs/phases/phase-03-backend-api.md)
- [API Phase 4 cho frontend](docs/phases/phase-04-backend-api.md)
- [Design system frontend](frontend/docs/design-system.md)

## Kiểm tra repository Git

Chạy tại thư mục repository và kiểm tra `.env` không được stage trước khi commit:

```powershell
git status
git remote -v
```

Không thay remote, push, force-push hoặc pull/rebase khi chưa kiểm tra thay đổi local và chưa được người
duy trì repository cho phép.

