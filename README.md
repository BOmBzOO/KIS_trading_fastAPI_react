# KIS Trading System

한국투자증권 API를 이용한 트레이딩 시스템입니다.

## 기술 스택

- **Backend**: FastAPI, SQLModel, Alembic
- **Frontend**: React, TypeScript, Chakra UI
- **Database**: PostgreSQL
- **Infrastructure**: Docker, Docker Compose

## 주요 기능

1. **사용자 관리**
   - 회원가입/로그인
   - 권한 관리 (일반 사용자/관리자)
   - 프로필 관리

2. **계좌 관리**
   - 계좌 등록 및 관리
   - API 키 관리
   - 실계좌/모의계좌 설정
   - Discord 웹훅 설정

## 시작하기

### 사전 요구사항

- Docker
- Docker Compose
- Git

### 설치 및 실행

1. 저장소 클론
```bash
git clone [repository-url]
cd [project-directory]
```

2. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 수정하여 필요한 설정을 입력
```

3. 도커 컨테이너 실행
```bash
docker compose up -d
```

4. 데이터베이스 마이그레이션
```bash
docker compose exec backend alembic upgrade head
```

### API 문서

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 프로젝트 구조

```
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   └── tests/
│   ├── alembic/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
├── docker/
├── docker-compose.yml
└── README.md
```

## 데이터베이스 구조

### 주요 모델

1. **User**
   - 사용자 정보 관리
   - 이메일, 비밀번호, 권한 등

2. **Account**
   - 거래 계좌 정보
   - 계좌번호, 상품코드, 계좌유형 등

3. **AccountAPIConfig**
   - API 설정 정보
   - API 키, 시크릿 키, Discord 웹훅 URL 등

### 관계
- User -(1:N)-> Account: 사용자는 여러 계좌를 가질 수 있음
- Account -(1:1)-> AccountAPIConfig: 각 계좌는 하나의 API 설정을 가짐

## 개발 가이드

### 백엔드 개발

1. 새로운 모델 추가
```python
# app/models.py에 모델 추가
# alembic revision --autogenerate로 마이그레이션 생성
```

2. API 엔드포인트 추가
```python
# app/api/routes/에 라우터 추가
# app/api/deps.py에 필요한 의존성 추가
```

### 프론트엔드 개발

1. 새로운 컴포넌트 추가
```typescript
// src/components/에 컴포넌트 추가
// src/routes/에 라우트 추가
```

2. API 통신
```typescript
// src/api/에 API 호출 함수 추가
```

## 라이센스

MIT License
