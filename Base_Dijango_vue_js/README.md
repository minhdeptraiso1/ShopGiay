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
uv sync --frozen
uv run python manage.py migrate
uv run python manage.py seed_dev_user
uv run python manage.py runserver
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

- Email: `demo@example.com`
- Mật khẩu: `123456`

Vite proxy `/api` và `/health` sang backend cổng `8000`, vì vậy local mặc định không cần đặt
`VITE_API_BASE_URL`.

## Kiểm tra chất lượng

Backend (chạy trong `Base_dijango`):

```powershell
uv run ruff check .
uv run ruff format --check .
uv run python manage.py check --settings=config.settings.test
uv run python manage.py makemigrations --check --dry-run --settings=config.settings.test
uv run pytest
uv run python manage.py spectacular --validate --fail-on-warn --file schema.yml --settings=config.settings.test
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
- [Design system frontend](frontend/docs/design-system.md)

## Đưa project hiện tại lên GitHub lần đầu

Chạy tại `D:\Project\Base\Base_djangi_vuejs` sau khi kiểm tra `.env` không được stage:

```powershell
git init
git branch -M main
git add .
git status
git commit -m "chore: initialize Django Vue base repository"
git remote add origin https://github.com/minhdeptraiso1/Base_Dijango_vue_js.git
git push -u origin main
```

Nếu đã có remote `origin`, dùng:

```powershell
git remote set-url origin https://github.com/minhdeptraiso1/Base_Dijango_vue_js.git
git push -u origin main
```

Nếu GitHub báo remote đã có commit (ví dụ README tạo sẵn trên web), không dùng force push. Chạy
`git pull --rebase origin main`, xử lý conflict nếu có, rồi `git push -u origin main`.

