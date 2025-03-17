from datetime import time

# 토큰 관련 설정
TOKEN_REFRESH_THRESHOLD_MINUTES = 30  # 토큰 만료 전 갱신 시작 시간(분)
TOKEN_CHECK_INTERVAL_SECONDS = 60     # 토큰 체크 주기(초)

# 거래 시간 설정
MARKET_START_TIME = time(9, 0)        # 장 시작 시간
MARKET_END_TIME = time(15, 30)        # 장 종료 시간

# 잔고 체크 설정
BALANCE_CHECK_INTERVAL_SECONDS = 60   # 잔고 체크 주기(초)

# API 관련 설정
KIS_API_BASE_URL = {
    "paper": "https://openapivts.koreainvestment.com:29443",
    "live": "https://openapi.koreainvestment.com:9443"
}

# 로깅 관련 설정
LOG_FORMAT = "%(asctime)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S" 