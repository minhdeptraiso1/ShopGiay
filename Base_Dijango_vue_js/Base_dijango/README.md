# Django Backend Base

Backend REST dạng modular monolith, dùng Django 5.2 LTS và Python 3.12. Django 5.2 được chọn vì là LTS;
DRF 3.16 hỗ trợ Django 5.2. Dependency chính và phụ được khóa trong `uv.lock`.

## Công nghệ

Django 5.2, Django REST Framework 3.16, PostgreSQL 18, Redis 8, Simple JWT 5.5,
drf-spectacular 0.29, django-environ, django-cors-headers, django-redis, Gunicorn và WhiteNoise.
Test dùng pytest/pytest-django/factory-boy; chất lượng mã dùng Ruff.

## Chạy dự án local bằng VS Code và PowerShell

### 1. Chuẩn bị

Cần cài sẵn:

- Python 3.12 trở lên.
- Python dùng để tạo local tool runner `.tools`; `uv` được khóa ở phiên bản 0.8.22 như CI.
- PostgreSQL 18 đang chạy và đã có database `dijango`.
- VS Code cùng extension **Python** của Microsoft.
- Docker Desktop để chạy PostgreSQL/Redis theo cấu hình mặc định bên dưới; hoặc hai service local tương đương.

Cài local `uv` vào `.tools` để không phụ thuộc PATH hoặc lệnh `uv` global. Chạy tại thư mục
`Base_dijango`; ở máy hoặc checkout mới chạy hai lệnh đầu một lần:

```powershell
py -m venv .tools
.\.tools\Scripts\python.exe -m pip install uv==0.8.22
```

Đặt cache của `uv` trong dự án để tránh lỗi quyền truy cập cache dùng chung ở `AppData`, rồi xác nhận local
runner:

```powershell
$env:UV_CACHE_DIR = "$PWD\.uv-cache"
.\.tools\Scripts\uv.exe --version
```

Kết quả phải bắt đầu bằng `uv 0.8.22`. Thư mục `.tools/` không thuộc source và bị Git ignore, vì vậy cần
tạo lại theo hai lệnh trên khi chuyển sang máy hoặc checkout mới. Mọi lệnh local trong README này dùng
`.\.tools\Scripts\uv.exe`, không cần đóng/mở terminal và không phụ thuộc PATH. Biến `UV_CACHE_DIR` chỉ tồn
tại terminal hiện tại; đặt lại biến này khi mở terminal mới.

### 2. Mở dự án bằng VS Code

Mở **PowerShell**, sau đó chạy:

```powershell
Set-Location <thu-muc-repository>\Base_dijango
code .
```

Trong VS Code:

1. Nhấn `Ctrl+Shift+P`.
2. Chọn `Python: Select Interpreter`.
3. Chọn file `<thu-muc-repository>\Base_dijango\.venv\Scripts\python.exe` nếu môi trường đã tồn tại.
4. Mở terminal từ menu **Terminal → New Terminal**.
5. Nhấn mũi tên cạnh nút dấu cộng của terminal và chọn **PowerShell**.

Tất cả lệnh bên dưới được chạy trong PowerShell của VS Code, tại thư mục `Base_dijango`. Chạy từng lệnh,
đợi lệnh kết thúc và dấu nhắc `PS ...>` xuất hiện lại rồi mới chạy lệnh tiếp theo.

### 3. Tạo và sửa file `.env`

```powershell
Copy-Item .env.example .env
notepad .env
```

Sửa thông tin kết nối PostgreSQL trong `.env`:

```dotenv
DATABASE_URL=postgresql://postgres:MAT_KHAU_POSTGRES@127.0.0.1:5432/dijango
```

Nếu Redis được cài trực tiếp trên Windows và chạy ở cổng mặc định:

```dotenv
REDIS_URL=redis://127.0.0.1:6379/1
```

Nếu Redis chạy bằng Docker Compose của dự án:

```dotenv
REDIS_URL=redis://127.0.0.1:6380/1
```

Tạo hai secret riêng bằng lệnh sau, chạy hai lần và chép hai kết quả khác nhau vào
`DJANGO_SECRET_KEY` và `JWT_SIGNING_KEY`:

```powershell
py -c "import secrets; print(secrets.token_urlsafe(64))"
```

Không commit file `.env`. Nếu mật khẩu PostgreSQL chứa ký tự như `@`, `#`, `/` hoặc `:`, cần
URL-encode mật khẩu trước khi đưa vào `DATABASE_URL`.

### 4. Cài dependency

Từ thư mục `Base_dijango`:

```powershell
.\.tools\Scripts\uv.exe sync --frozen
```

Sau lệnh này, môi trường Python nằm tại `.venv\Scripts\python.exe`. Nếu VS Code chưa nhận ra, thực hiện
lại bước `Python: Select Interpreter`.

### 5. Khởi động PostgreSQL và Redis

#### Cách A — Docker Compose (khuyến nghị)

Mở Docker Desktop và chờ trạng thái **Engine running**, sau đó sửa hai dòng trong `.env`:

```dotenv
DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5433/dijango
REDIS_URL=redis://127.0.0.1:6380/1
```

Khởi động và kiểm tra cả hai service:

```powershell
docker compose up -d db redis
docker compose ps
Test-NetConnection 127.0.0.1 -Port 5433 -InformationLevel Quiet
Test-NetConnection 127.0.0.1 -Port 6380 -InformationLevel Quiet
```

Hai lệnh `Test-NetConnection` phải trả về `True` trước khi chạy migration.

#### Cách B — Service cài trực tiếp trên Windows

Đảm bảo PostgreSQL đã có database `dijango`, Redis đang chạy, rồi dùng đúng tài khoản/mật khẩu trong
`.env`. Cổng mặc định thường là:

```dotenv
DATABASE_URL=postgresql://postgres:MAT_KHAU_POSTGRES@127.0.0.1:5432/dijango
REDIS_URL=redis://127.0.0.1:6379/1
```

### 6. Kiểm tra cấu hình và tạo bảng

Chạy lần lượt:

```powershell
.\.tools\Scripts\uv.exe run python manage.py check
.\.tools\Scripts\uv.exe run python manage.py migrate
.\.tools\Scripts\uv.exe run python manage.py showmigrations
```

- `check` kiểm tra cấu hình Django.
- `migrate` tạo/cập nhật bảng trong database `dijango`.
- `showmigrations` hiển thị migration đã được áp dụng; migration có `[X]` là đã chạy.
- Nếu `migrate` đứng yên hoặc báo connection refused, dừng bằng `Ctrl+C` rồi quay lại bước 5; đó là lỗi
  kết nối PostgreSQL, không phải lỗi migration.

### 7. Tạo tài khoản local để thử API

Không tạo tài khoản bằng migration schema vì migration cũng được chạy ở production. Sau `migrate`, chạy
lệnh seed dành riêng cho development:

```powershell
.\.tools\Scripts\uv.exe run python manage.py seed_dev_user
```

Tài khoản mặc định lấy từ `.env`:

```text
Email: demo@example.com
Password: 123456
```

Lệnh có tính idempotent: nếu user đã tồn tại thì không tạo trùng, không tự đổi mật khẩu và bảo đảm user có
role `CUSTOMER` để dùng API storefront. Muốn đặt lại mật khẩu theo `DEMO_USER_PASSWORD` trong `.env`, chạy:

```powershell
.\.tools\Scripts\uv.exe run python manage.py seed_dev_user --reset-password
```

Tạo hoặc đưa về trạng thái chuẩn ba tài khoản kiểm thử CUSTOMER, STAFF và ADMIN:

```powershell
.\.tools\Scripts\uv.exe run python manage.py seed_dev_accounts
```

| Role | Email | Mật khẩu mặc định | Phạm vi local |
|---|---|---|---|
| CUSTOMER | `customer@example.com` | `123456` | Storefront, cart và order |
| STAFF | `staff@example.com` | `123456` | API vận hành dành cho STAFF/ADMIN |
| ADMIN | `admin@example.com` | `123456` | API admin và Django Admin |

`seed_dev_accounts` có tính idempotent: mỗi lần chạy sẽ bảo đảm đúng role/flag và đặt lại mật khẩu của ba
tài khoản theo `DEMO_USER_PASSWORD`. ADMIN được bật `is_staff` và `is_superuser`; STAFF được bật
`is_staff` nhưng không phải superuser.

Tạo catalog local gồm 6 sản phẩm, 30 biến thể, ảnh ngoài và tồn kho ban đầu dựa trên dữ liệu storefront:

```powershell
.\.tools\Scripts\uv.exe run python manage.py seed_catalog
```

`seed_catalog` có tính idempotent và không đặt lại số lượng tồn của biến thể đã tồn tại, nên chạy lại
không làm mất các thay đổi kho khi test. Lệnh chỉ hoạt động khi `DEBUG=True`.

Tạo mã giảm giá `WELCOME10` và banner mẫu cho Phase 5:

```powershell
.\.tools\Scripts\uv.exe run python manage.py seed_engagement
```

Lệnh có tính idempotent, chỉ chạy khi `DEBUG=True` và không tạo trùng dữ liệu khi chạy lại.

Có thể đổi `DEMO_USER_EMAIL` và `DEMO_USER_PASSWORD` trong `.env`. Các lệnh seed bị vô hiệu hóa khi
`DEBUG=False`, vì vậy không tạo credential test trong production. `123456` là mật khẩu yếu, chỉ dùng để
thử local. Django lưu password hash bằng `set_password()`, không lưu chuỗi `123456` trực tiếp trong DB.

### 8. Tạo tài khoản quản trị

Đây là bước tùy chọn, chỉ cần khi muốn đăng nhập Django Admin:

```powershell
.\.tools\Scripts\uv.exe run python manage.py createsuperuser
```

Nhập email và mật khẩu theo hướng dẫn trên terminal.

### 9. Chạy backend

```powershell
.\.tools\Scripts\uv.exe run python manage.py runserver
```

Không đóng terminal đang chạy server. Nhấn `Ctrl+C` khi muốn dừng.

#### Cấu hình email reset mật khẩu

`EMAIL_BACKEND=auto` tự chọn cách gửi theo cấu hình trong `.env`:

- Chưa điền đủ `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`: email được in ở terminal backend.
- Đã điền đủ ba giá trị: backend dùng SMTP để gửi email thật.

Ví dụ cấu hình SMTP dùng TLS:

```dotenv
FRONTEND_BASE_URL=http://localhost:5173
DEFAULT_FROM_EMAIL=no-reply@example.com
EMAIL_BACKEND=auto
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-smtp-user
EMAIL_HOST_PASSWORD=your-smtp-app-password
EMAIL_USE_TLS=true
EMAIL_USE_SSL=false
EMAIL_TIMEOUT=10
```

Sau khi thay `.env`, khởi động lại backend để settings được nạp lại. Không dùng mật khẩu email thông
thường nếu provider hỗ trợ app password/SMTP credential và không commit file `.env`.

#### Cấu hình VNPay sandbox

Secret chỉ đặt trong `.env` local:

```dotenv
PAYMENT_RESERVATION_MINUTES=15
VNPAY_PAYMENT_URL=https://sandbox.vnpayment.vn/paymentv2/vpcpay.html
VNPAY_TMN_CODE=your-sandbox-tmn-code
VNPAY_HASH_SECRET=your-rotated-sandbox-secret
VNPAY_RETURN_URL=http://localhost:5173/payment/vnpay-return
VNPAY_VERSION=2.1.0
VNPAY_COMMAND=pay
VNPAY_ORDER_TYPE=other
```

Đăng ký IPN tại VNPay trỏ tới `https://<public-backend>/api/v1/payments/vnpay/ipn/`. VNPay không thể gọi
`localhost`; local end-to-end cần HTTPS tunnel. Return URL chỉ đưa browser về frontend, còn IPN đã ký mới
được backend dùng để xác nhận thanh toán.

Chạy định kỳ để giải phóng giữ hàng hết hạn và xem giao dịch cần đối soát:

```powershell
.\.tools\Scripts\uv.exe run python manage.py release_expired_reservations
.\.tools\Scripts\uv.exe run python manage.py reconcile_vnpay_payments
```

Các địa chỉ sử dụng:

- Swagger: <http://127.0.0.1:8000/api/docs/>
- ReDoc: <http://127.0.0.1:8000/api/redoc/>
- Django Admin: <http://127.0.0.1:8000/admin/>
- Liveness: <http://127.0.0.1:8000/health/live/>
- Readiness PostgreSQL/Redis: <http://127.0.0.1:8000/health/ready/>

### 10. Những lần chạy sau

Mở VS Code và chạy lại dự án bằng PowerShell:

```powershell
Set-Location <thu-muc-repository>\Base_dijango
code .
docker compose up -d db redis
docker compose ps
$env:UV_CACHE_DIR = "$PWD\.uv-cache"
.\.tools\Scripts\uv.exe run python manage.py migrate
.\.tools\Scripts\uv.exe run python manage.py seed_dev_accounts
.\.tools\Scripts\uv.exe run python manage.py runserver
```

Có thể bỏ qua `docker compose up` nếu PostgreSQL và Redis local đã chạy và `.env` trỏ đúng cổng. Không
cần chạy lại lệnh seed hoặc `createsuperuser`, trừ khi muốn đưa mật khẩu/role test về cấu hình mặc định hay
tạo thêm tài khoản quản trị.

### 11. Lỗi thường gặp

- `uv is not recognized`: đây là bình thường nếu chưa cài global. Dùng đúng
  `.\.tools\Scripts\uv.exe`; nếu file chưa tồn tại thì tạo lại `.tools` theo bước 1. Không dùng
  `.tools\bin\uv.exe`; `bin` là cấu trúc Unix, không phải Windows.
- `failed to open ... AppData\\Local\\uv\\cache ... Access is denied`: chạy
  `$env:UV_CACHE_DIR = "$PWD\.uv-cache"` trong terminal hiện tại rồi chạy lại lệnh `uv.exe`.
- Dấu nhắc `>>`: PowerShell đang nhận một khối lệnh nhiều dòng, thường do `Shift+Enter`. Nhấn `Ctrl+C` để
  hủy nếu cần, rồi chạy từng lệnh bằng `Enter` và chờ dấu nhắc `PS ...>` quay lại.
- `migrate` không có output: PostgreSQL chưa sẵn sàng. Chạy `docker compose ps` và
  `Test-NetConnection 127.0.0.1 -Port 5433 -InformationLevel Quiet`.
- `permission denied ... docker_engine` hoặc không đọc được `.docker\config.json`: mở Docker Desktop bằng
  đúng tài khoản Windows đang chạy terminal; đóng/mở lại terminal. Nếu vẫn lỗi, kiểm tra quyền Docker
  Desktop trước khi chạy lại `docker compose up`.
- `password authentication failed`: sửa user/mật khẩu trong `DATABASE_URL` của `.env`.
- `connection refused` ở cổng `5432` hoặc `5433`: kiểm tra PostgreSQL service và cổng trong `.env`.
- Readiness báo Redis lỗi: kiểm tra `REDIS_URL`, Docker Desktop và `docker compose ps`.
- `'code' is not recognized`: mở dự án trực tiếp từ VS Code hoặc cài lệnh `code` vào PATH.
- Port `8000` đang được dùng: chạy `... manage.py runserver 8001` và truy cập cổng `8001`.

Schema OpenAPI: <http://127.0.0.1:8000/api/schema/>. Tài liệu API mở mặc định ở local và tắt mặc định
ở production.

## Chạy Docker

```powershell
docker compose up --build -d db redis
docker compose run --rm backend python manage.py migrate
docker compose run --rm backend python manage.py seed_dev_user
docker compose run --rm backend python manage.py createsuperuser
docker compose up --build backend
```

Compose tạo database/Redis riêng trong named volumes (host ports 5433/6380). Container chạy non-root bằng Gunicorn; migration
là bước release riêng, không chạy trong mỗi worker. WhiteNoise phục vụ static đã `collectstatic` để Django
Admin hoạt động; media lớn nên đưa ra object storage/reverse proxy ở dự án cụ thể.

## Frontend và auth

Frontend Vue nằm trong thư mục `frontend`. Xem [hướng dẫn frontend](../frontend/README.md) để chạy bằng
VS Code/CMD, kiểm thử và hiểu cấu trúc source.

Luồng auth không trả refresh token trong JSON. Backend đặt refresh token vào cookie `HttpOnly`; frontend
giữ access token trong memory và gửi CSRF header cho login/refresh/logout. Có thể thử nhanh qua giao diện:

```cmd
cd /d <thu-muc-repository>\frontend
pnpm install --frozen-lockfile
pnpm dev
```

Mở <http://localhost:5173>, dùng `demo@example.com` / `123456`. Logout thu hồi refresh token trong cookie;
access token đã phát vẫn tồn tại đến khi hết hạn, nhưng frontend xóa nó khỏi memory ngay khi logout.
Chạy định kỳ `.\.tools\Scripts\uv.exe run python manage.py flushexpiredtokens` (ví dụ cron hằng ngày).

## Kiểm tra

Test cần PostgreSQL riêng. Khi `DATABASE_URL` trỏ tới `dijango`, Django pytest tạo/xóa
`test_dijango`; Redis test dùng DB 15 và `REDIS_KEY_PREFIX` riêng. Không trỏ test vào tài khoản DB không
có quyền tạo database.

```powershell
.\.tools\Scripts\uv.exe run ruff check .
.\.tools\Scripts\uv.exe run ruff format --check .
.\.tools\Scripts\uv.exe run python manage.py check --settings=config.settings.test
.\.tools\Scripts\uv.exe run python manage.py makemigrations --check --dry-run --settings=config.settings.test
.\.tools\Scripts\uv.exe run pytest --cov --cov-report=term-missing
.\.tools\Scripts\uv.exe run python manage.py spectacular --validate --fail-on-warn --file schema.yml --settings=config.settings.test
```

`makemigrations` sinh file mô tả thay đổi model; phải đọc và commit file đó. `migrate` áp các file chưa
chạy vào DB. Xem trạng thái bằng `showmigrations`. Trong môi trường dùng chung không sửa/xóa migration đã
chạy; tạo migration mới. Trước rollback (`migrate <app> <migration_trước>`), đọc reverse operation và
sao lưu DB vì data migration/xóa cột có thể không đảo ngược an toàn.

## Production

Dùng `config.settings.production`; các biến secret/DB/Redis/hosts/CORS/CSRF bắt buộc và thiếu sẽ fail fast.
Chỉ tin `X-Forwarded-Proto` khi ứng dụng nằm sau reverse proxy do mình kiểm soát. Bật HTTPS redirect,
secure cookies và HSTS; đặt CORS origin cụ thể. Schema/docs tắt trừ khi bật rõ ràng. DRF throttling dùng
Redis chia sẻ và nhận IP theo `REMOTE_ADDR`; reverse proxy phải ghi đè header từ client và truyền đúng IP.
Mặc định `DRF_NUM_PROXIES=0` nên throttle dùng `REMOTE_ADDR`. Sau reverse proxy, đặt đúng số proxy tin
cậy và cấu hình proxy ghi đè header do client gửi; cấu hình sai có thể gom mọi client hoặc cho giả IP.
Throttle hỗ trợ giảm tải, không thay thế rate limit ở edge, chống brute-force hay DDoS.

Phase 1 đã có đăng ký công khai cho CUSTOMER, quên/đặt lại mật khẩu, role/permission và quản lý địa chỉ.
Giới hạn hiện tại: chưa có MFA, social login, Celery/Kafka hoặc cơ chế thu hồi toàn bộ JWT family. Xem thêm
[tài liệu kiến trúc](docs/architecture.md).
