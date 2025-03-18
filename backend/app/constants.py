from datetime import time
from pytz import timezone

# Timezone 설정
KST = timezone('Asia/Seoul')
UTC = timezone('UTC')

# 토큰 관련 설정
TOKEN_REFRESH_THRESHOLD_MINUTES = 30  # 토큰 만료 전 갱신 시작 시간(분)
TOKEN_CHECK_INTERVAL_SECONDS = 60     # 토큰 체크 주기(초)

# 거래 시간 설정
MARKET_START_TIME = time(9, 0)        # 장 시작 시간
MARKET_END_TIME = time(15, 30)        # 장 종료 시간

# 잔고 체크 설정
BALANCE_CHECK_INTERVAL_SECONDS = 60   # 잔고 체크 주기(초)

# 백그라운드 작업 설정
TOKEN_CHECK_INTERVAL = 60  # 토큰 체크 간격(초)
BALANCE_CHECK_INTERVAL = 60  # 잔고 체크 간격(초)

# API 관련 설정
KIS_API_BASE_URL = {
    "paper": "https://openapivts.koreainvestment.com:29443",
    "live": "https://openapi.koreainvestment.com:9443"
}

# KIS API 엔드포인트
KIS_API_ENDPOINTS = {
    "token": "/oauth2/tokenP",
    "balance": "/uapi/domestic-stock/v1/trading/inquire-balance",
    "daily_trades": "/uapi/domestic-stock/v1/trading/inquire-daily-ccld"
}

# KIS API 트랜잭션 ID
KIS_API_TR_ID = {
    "balance": {
        "paper": "VTTC8434R",
        "live": "TTTC8434R"
    },
    "daily_trades": {
        "paper": "VTTC8001R",
        "live": "TTTC8001R"
    }
}

# KIS API 파라미터
KIS_API_PARAMS = {
    "balance": {
        "AFHR_FLPR_YN": "N",
        "OFL_YN": "",
        "INQR_DVSN": "02",
        "UNPR_DVSN": "01",
        "FUND_STTL_ICLD_YN": "N",
        "FNCG_AMT_AUTO_RDPT_YN": "N",
        "PRCS_DVSN": "00",
        "CTX_AREA_FK100": "",
        "CTX_AREA_NK100": ""
    },
    "daily_trades": {
        "SLL_BUY_DVSN_CD": "00",
        "INQR_DVSN": "00",
        "PDNO": "",
        "CCLD_DVSN": "00",
        "ORD_GNO_BRNO": "",
        "ODNO": "",
        "INQR_DVSN_3": "00",
        "INQR_DVSN_1": "",
        "INQR_DVSN_2": "",
        "CTX_AREA_FK100": "",
        "CTX_AREA_NK100": ""
    }
}

# 로깅 관련 설정
LOG_FORMAT = "%(asctime)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S" 