# 디코나이 관제 플랫폼 (SenSa)

산업 현장의 유해가스, 전력, 작업자 위치를 실시간으로 모니터링하고 위험 상황을 즉시 감지하는 지능형 통합 관제 시스템.

중기청 R&D 과제 3차 프로젝트 — Django DRF 기반 관제 서버.

---

## 📋 프로젝트 개요

### 배경

산업 현장에서 발생하는 가스 누출, 전력 이상, 작업자 안전 사고는 대부분 **실시간 감지와 즉시 대응 체계의 부재**에서 비롯된다. 본 프로젝트는 다음을 목표로 한다.

- 다종 센서(유해가스 9종, 전력 3종) 실시간 데이터 수집 및 모니터링
- 작업자 위치 추적과 지오펜스(위험구역) 자동 감지
- 임계치 초과 시 즉시 알람 발생 및 이력 관리
- 권한 기반 관제 운영 (관리자/운영자 역할 분리)

### 개발 단계

| 단계    | 내용                             | 상태       |
| ------- | -------------------------------- | ---------- |
| 1차     | 센서 데이터 수집 프로토타입      | ✅ 완료    |
| 2차     | 데이터 시각화 및 알람 시스템     | ✅ 완료    |
| **3차** | **통합 관제 플랫폼 (본 저장소)** | 🚧 진행 중 |
| 4차     | 배포 및 운영 환경 구축           | 📅 예정    |

---

## 🛠️ 기술 스택

### Backend

- **Django 5.x** — 관제 서버 프레임워크
- **Django REST Framework 3.15+** — RESTful API
- **djangorestframework-simplejwt** — JWT 토큰 인증
- **django-cors-headers** — CORS 설정

### Database

- **SQLite** (개발 환경) — 향후 PostgreSQL로 전환 예정

### Infra & Tools

- **WSL2 (Ubuntu)** — 개발 환경
- **Python 3.11+**
- **Git / GitHub** — 버전 관리

### 향후 도입 예정 (4차)

- FastAPI (실시간 WebSocket 서버)
- Chart.js, Leaflet.js (대시보드 시각화)
- PostgreSQL, Redis, Celery
- Docker, Nginx

---

## ✨ 현재 구현된 기능

### 🔐 사용자 인증 시스템

- **회원가입** (공개 가입 + 역할 고정)
  - 아이디 중복/형식 검증 (4~20자, 영문/숫자/\_)
  - 비밀번호 강도 검증 (8자 이상, Django 4단계 validator)
  - 가입 시 `role=operator` 강제 고정 (자기 권한 상승 방지)
- **로그인 / 로그아웃**
  - 세션 기반 인증 (브라우저 페이지용)
  - JWT 기반 인증 (API 클라이언트용)
  - 이중 인증 구조 병행 지원
- **헤더 사용자 정보 표시**
  - 로그인 상태에 따른 네비게이션 분기
  - 역할별 배지 (관리자/운영자) 시각적 구분
- **로그인 후 아이디 자동 채움** (가입 직후 UX 개선)

### 🛡️ 보안

- **비밀번호 해시 저장** (pbkdf2_sha256, 870,000회 stretching)
- **CSRF 보호** (모든 폼)
- **JWT 토큰 블랙리스트** (로그아웃 시 refresh 토큰 무효화)
- **Open Redirect 방지** (next 파라미터 검증)
- **세션 쿠키 HttpOnly**
- **CORS 화이트리스트**
- **역할 강제 고정** (회원가입 시 `is_staff`, `is_superuser`, `role` 조작 불가)

### 🏗️ 아키텍처

- **페이지 뷰(함수 기반)** + **API 뷰(클래스 기반 Generic)** 분리
- **DRF 관례에 맞춘 ViewSet, CreateAPIView, RetrieveAPIView 활용**
- **CSS/JS 파일 분리** (관심사 분리, 브라우저 캐싱)

---

## 📁 프로젝트 구조

```
SenSa/
├── SenSa/                          # Django 프로젝트 루트
│   ├── manage.py
│   ├── db.sqlite3                  # SQLite DB (gitignore)
│   ├── config/
│   │   ├── settings.py             # Django 설정
│   │   ├── urls.py                 # 루트 URL
│   │   ├── asgi.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── __init__.py
│   │   └── accounts/               # 사용자 인증 앱
│   │       ├── models.py           # 커스텀 User (AbstractUser 확장)
│   │       ├── serializers.py      # Login/User/Signup Serializer
│   │       ├── views.py            # 페이지 뷰(함수) + API 뷰(Generic)
│   │       ├── urls.py
│   │       ├── admin.py
│   │       └── migrations/
│   ├── static/
│   │   ├── css/
│   │   │   ├── components.css      # 공통 컴포넌트
│   │   │   ├── login.css           # 로그인/가입 공통 레이아웃
│   │   │   ├── login-page.css      # 로그인 페이지 전용
│   │   │   └── signup-page.css     # 회원가입 페이지 전용
│   │   └── js/
│   │       ├── login-validation.js # 로그인 폼 검증
│   │       └── signup-validation.js # 회원가입 폼 검증
│   └── templates/
│       ├── base.html               # 공통 레이아웃 (헤더 포함)
│       ├── home.html               # 로그인 후 홈
│       └── accounts/
│           ├── login.html
│           └── signup.html
├── venv/                           # 가상환경 (gitignore)
├── requirements.txt
├── .env                            # 환경변수 (gitignore)
├── .gitignore
└── README.md
```

---

## 🚀 빠른 시작

### 필수 환경

- Python 3.11+
- WSL2 (Windows) 또는 Linux/macOS
- Git

### 1. 저장소 클론

```bash
git clone https://github.com/kingnh0328-blip/SenSa.git
cd SenSa
```

### 2. 가상환경 생성 및 패키지 설치

```bash
python3 -m venv venv
source venv/bin/activate            # Linux/WSL/macOS
# 또는 venv\Scripts\activate        # Windows

pip install --upgrade pip
pip install -r requirements.txt
```

### 3. 환경변수 설정

프로젝트 루트에 `.env` 파일 생성:

```env
SECRET_KEY=your-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
```

> 💡 운영 배포 시 `SECRET_KEY`는 반드시 무작위 값으로 변경 필수.

### 4. 데이터베이스 초기화

```bash
cd SenSa
python manage.py makemigrations accounts
python manage.py migrate
```

### 5. 관리자 계정 생성

```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@deconai.com
# Password: admin1234 (개발용)
```

### 6. 개발 서버 실행

```bash
python manage.py runserver 0.0.0.0:8000
```

### 7. 브라우저에서 확인

- **메인**: http://localhost:8000/
- **로그인**: http://localhost:8000/accounts/login/
- **회원가입**: http://localhost:8000/accounts/signup/
- **Django Admin**: http://localhost:8000/admin/

---

## 🔑 API 명세

### 페이지 URL (Django Template)

| Method    | Path                | 설명                         | 인증 |
| --------- | ------------------- | ---------------------------- | ---- |
| GET       | `/`                 | 홈 (로그인 상태에 따라 분기) | -    |
| GET       | `/home/`            | 로그인 후 홈 페이지          | 필수 |
| GET, POST | `/accounts/login/`  | 로그인 페이지                | -    |
| GET, POST | `/accounts/signup/` | 회원가입 페이지              | -    |
| GET       | `/accounts/logout/` | 로그아웃                     | 필수 |

### API 엔드포인트 (JWT)

| Method | Path                           | 설명                           | 인증 |
| ------ | ------------------------------ | ------------------------------ | ---- |
| POST   | `/api/accounts/login/`         | JWT 로그인 (토큰 발급)         | -    |
| POST   | `/api/accounts/signup/`        | 회원가입                       | -    |
| POST   | `/api/accounts/logout/`        | JWT 로그아웃 (토큰 블랙리스트) | 필수 |
| GET    | `/api/accounts/me/`            | 내 정보 조회                   | 필수 |
| POST   | `/api/accounts/token/refresh/` | Access 토큰 갱신               | -    |

### API 사용 예시

**로그인**:

```bash
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin1234"}'
```

응답:

```json
{
  "access": "eyJ...",
  "refresh": "eyJ...",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin",
    "role_display": "관리자"
  }
}
```

**내 정보 조회**:

```bash
curl http://localhost:8000/api/accounts/me/ \
  -H "Authorization: Bearer <access_token>"
```

**회원가입**:

```bash
curl -X POST http://localhost:8000/api/accounts/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "StrongPass2026!",
    "password_confirm": "StrongPass2026!",
    "email": "new@example.com",
    "department": "관제팀"
  }'
```

---

## 👥 사용자 역할 체계

| 역할                  | 권한                                             | 생성 방법                         |
| --------------------- | ------------------------------------------------ | --------------------------------- |
| **관리자 (admin)**    | 모든 기능 + Django Admin 접근 + 사용자 role 변경 | `createsuperuser` 명령어로만 생성 |
| **운영자 (operator)** | 대시보드 조회, CRUD                              | 회원가입 시 자동 부여 (기본값)    |

### 운영자 → 관리자 승격

일반 사용자가 관리자가 되려면:

1. 운영자로 회원가입
2. 기존 관리자가 Django Admin (`/admin/`)에 로그인
3. "사용자" 메뉴에서 대상 사용자 선택
4. `role`을 `admin`으로 변경, `Staff status` 체크
5. 저장 → 다음 로그인부터 관리자 권한 적용

---

## 🗺️ 로드맵

### v0.1 — 인증 뼈대 (현재)

- [x] 사용자 모델 (커스텀 User)
- [x] 로그인 / 로그아웃
- [x] 회원가입
- [x] JWT 인증 API
- [x] 헤더 / 네비게이션

### v0.2 — 대시보드 (예정)

- [ ] 센서 장비 관리 (Device CRUD)
- [ ] 지오펜스 관리 (GeoFence CRUD + Leaflet)
- [ ] 알람 이력 (AlertEvent)
- [ ] 작업자 조회 (Worker)
- [ ] 비밀번호 변경 페이지

### v0.3 — 실시간 연동 (예정)

- [ ] FastAPI WebSocket 서버 연동
- [ ] Chart.js 실시간 차트
- [ ] 센서 시뮬레이터
- [ ] 지도 기반 작업자/지오펜스 표시

### v1.0 — 배포 (예정)

- [ ] PostgreSQL 전환
- [ ] Redis + Celery (비동기 처리)
- [ ] Docker 컨테이너화
- [ ] Nginx 리버스 프록시
- [ ] HTTPS 적용
- [ ] Rate Limiting (django-axes)

---

## 🌿 브랜치 전략

```
main                  # 배포 가능한 안정 버전
├── dev_csw.v.0.1     # 개발자 개인 브랜치 (ex: csw)
├── dev_khn.v.0.1     # 개발자 개인 브랜치 (ex: khn)
└── feature/xxx       # 기능 단위 브랜치 (필요 시)
```

### 작업 흐름

```bash
# 1. 최신 main 동기화
git checkout main
git pull origin main

# 2. 본인 브랜치로 이동
git checkout dev_csw.v.0.1
git merge main

# 3. 작업 후 커밋
git add .
git commit -m "feat: 기능 설명"

# 4. 본인 브랜치로 push
git push origin dev_csw.v.0.1

# 5. GitHub에서 main으로 PR 생성
```

### 커밋 메시지 규칙

| 타입       | 용도      | 예시                                |
| ---------- | --------- | ----------------------------------- |
| `feat`     | 새 기능   | `feat: accounts 앱 JWT 인증 구현`   |
| `fix`      | 버그 수정 | `fix: 로그인 실패 메시지 오타 수정` |
| `refactor` | 리팩토링  | `refactor: API를 Generic 뷰로 전환` |
| `docs`     | 문서      | `docs: README 업데이트`             |
| `chore`    | 설정/기타 | `chore: requirements.txt 갱신`      |
| `style`    | 스타일    | `style: CSS 파일 분리`              |
| `test`     | 테스트    | `test: 로그인 API 테스트 추가`      |

---

## 🧪 테스트

### 동작 검증 체크리스트

- [ ] 루트(`/`) 접근 시 비로그인이면 로그인 페이지로 이동
- [ ] 회원가입 성공 후 로그인 페이지에 아이디 자동 채움
- [ ] admin / admin1234로 로그인 성공
- [ ] 헤더에 사용자명 + 역할 배지 표시
- [ ] 로그아웃 후 페이지 접근 차단
- [ ] JWT API 로그인 → `/api/accounts/me/` 호출 성공
- [ ] 중복 아이디 가입 시도 시 에러 표시
- [ ] 비밀번호 불일치 시 에러 표시
- [ ] 회원가입 후 role이 `operator`로 저장됨 (SQLite 확인)

### SQLite 직접 확인

```bash
sqlite3 SenSa/db.sqlite3
```

```sql
SELECT id, username, role, is_staff, is_superuser FROM accounts_user;
.quit
```

---

## 🐛 트러블슈팅

### DB 관련

- **`no such table: accounts_user`** → `python manage.py migrate` 실행
- **`AUTH_USER_MODEL refers to model that has not been installed`** → `INSTALLED_APPS`에 `apps.accounts` 확인
- **`database is locked`** → Django shell 열려있지 않은지 확인, 서버 재시작

### 인증 관련

- **403 CSRF verification failed** → 폼에 `{% csrf_token %}` 포함 확인
- **JWT 토큰으로 API 호출 실패** → `Authorization: Bearer <토큰>` 헤더 형식 확인
- **로그인해도 계속 로그인 페이지로 튕김** → 브라우저 쿠키 허용 확인, `127.0.0.1` 대신 `localhost` 시도

### 모듈 관련

- **`ModuleNotFoundError: No module named 'apps.accounts'`** → `apps/__init__.py` 파일 생성 확인
- **venv 활성화 안 됨** → `source venv/bin/activate` (Linux/WSL), 경로 확인

---

## 👨‍💻 개발팀

| 이름   | 역할                 | GitHub                                                 |
| ------ | -------------------- | ------------------------------------------------------ |
| 김나현 | 프로젝트 리드        | [@kingnh0328-blip](https://github.com/kingnh0328-blip) |
| 최서원 | 백엔드 / 인증 시스템 | [@normalframe1094](https://github.com/normalframe1094) |

---

## 📄 라이선스

본 프로젝트는 중기청 R&D 과제의 산출물로, 내부 사용을 목적으로 합니다.

---

## 📚 참고 자료

- [Django 공식 문서](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Simple JWT 문서](https://django-rest-framework-simplejwt.readthedocs.io/)
- [OWASP 웹 보안 가이드](https://owasp.org/www-project-web-security-testing-guide/)

---

> **문의 및 이슈**: [GitHub Issues](https://github.com/kingnh0328-blip/SenSa/issues)
