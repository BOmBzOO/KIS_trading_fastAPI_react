# KIS/LS 증권 트레이딩 플랫폼

## 프로젝트 소개
이 프로젝트는 한국투자증권(KIS)과 LS증권의 API를 활용하여 주식 거래 및 계좌 관리를 할 수 있는 웹 기반 트레이딩 플랫폼입니다.

## 주요 기능
- KIS/LS 증권 계좌 연동 및 관리
- 실시간 잔고 조회
- 일별 거래 내역 조회
- 분별 데이터 수집 및 저장
- 자동 토큰 갱신
- 백그라운드 작업 관리

## 기술 스택
### 백엔드
- FastAPI
- SQLModel
- PostgreSQL
- Redis
- Celery

### 프론트엔드
- React
- TypeScript
- Material-UI
- Chart.js

## 설치 및 실행
### 환경 설정
1. Python 3.8 이상 설치
2. Node.js 16 이상 설치
3. PostgreSQL 설치
4. Redis 설치

### 백엔드 설정
```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
cd backend
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일을 수정하여 필요한 설정값 입력

# 데이터베이스 마이그레이션
alembic upgrade head

# 서버 실행
uvicorn app.main:app --reload
```

### 프론트엔드 설정
```bash
# 의존성 설치
cd frontend
npm install

# 개발 서버 실행
npm run dev
```

## API 문서
- 백엔드 API 문서: http://localhost:8000/docs
- 프론트엔드: http://localhost:3000

## 프로젝트 구조
```
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   └── services/
│   │   ├── core/
│   │   ├── models/
│   │   └── schemas/
│   ├── alembic/
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── public/
└── docker/
```

## 환경 변수
### 백엔드 (.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
```

### 프론트엔드 (.env)
```
REACT_APP_API_URL=http://localhost:8000
```

## 라이선스
이 프로젝트는 MIT 라이선스를 따릅니다.
