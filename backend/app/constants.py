from datetime import time
from pytz import timezone

# Timezone 설정
KST = timezone('Asia/Seoul')  # 한국 시간대
UTC = timezone('UTC')        # UTC 시간대

# 토큰 관련 설정
TOKEN_REFRESH_THRESHOLD_MINUTES = 30  # 토큰 만료 전 갱신 시작 시간(분)
TOKEN_CHECK_INTERVAL_SECONDS = 60     # 토큰 체크 주기(초)

# 거래 시간 설정
MARKET_START_TIME = time(9, 0)        # 장 시작 시간 (09:00)
MARKET_END_TIME = time(15, 30)        # 장 종료 시간 (15:30)

# 잔고 체크 설정
BALANCE_CHECK_INTERVAL_SECONDS = 60   # 잔고 체크 주기(초)

# 백그라운드 작업 설정
TOKEN_CHECK_INTERVAL = 60  # 토큰 체크 간격(초)
BALANCE_CHECK_INTERVAL = 60  # 잔고 체크 간격(초)

# API 관련 설정
KIS_API_BASE_URL = {
    "paper": "https://openapivts.koreainvestment.com:29443",  # 모의투자 API URL
    "live": "https://openapi.koreainvestment.com:9443"        # 실전투자 API URL
}

# KIS API 엔드포인트
KIS_API_ENDPOINTS = {
    "token": "/oauth2/tokenP",                    # 토큰 발급
    "balance": "/uapi/domestic-stock/v1/trading/inquire-balance",  # 잔고조회
    "daily_trades": "/uapi/domestic-stock/v1/trading/inquire-daily-ccld"  # 일별거래내역
}

# KIS API 트랜잭션 ID
KIS_API_TR_ID = {
    "balance": {
        "paper": "VTTC8434R",  # 모의투자 잔고조회
        "live": "TTTC8434R"    # 실전투자 잔고조회
    },
    "daily_trades": {
        "paper": "VTTC8001R",  # 모의투자 일별거래내역
        "live": "TTTC8001R"    # 실전투자 일별거래내역
    }
}

# KIS API 파라미터
KIS_API_PARAMS = {
    "balance": {
        "AFHR_FLPR_YN": "N",           # 장후 예수금 포함 여부
        "OFL_YN": "",                  # 오프라인 여부
        "INQR_DVSN": "02",             # 조회구분
        "UNPR_DVSN": "01",             # 단가구분
        "FUND_STTL_ICLD_YN": "N",      # 펀드결제금액 포함 여부
        "FNCG_AMT_AUTO_RDPT_YN": "N",  # 융자금액 자동상환 여부
        "PRCS_DVSN": "00",             # 처리구분
        "CTX_AREA_FK100": "",          # 연속조회검색조건
        "CTX_AREA_NK100": ""           # 연속조회키
    },
    "daily_trades": {
        "SLL_BUY_DVSN_CD": "00",       # 매도매수구분코드
        "INQR_DVSN": "00",             # 조회구분
        "PDNO": "",                    # 종목코드
        "CCLD_DVSN": "00",             # 체결구분
        "ORD_GNO_BRNO": "",            # 주문채번
        "ODNO": "",                    # 주문번호
        "INQR_DVSN_3": "00",           # 조회구분3
        "INQR_DVSN_1": "",             # 조회구분1
        "INQR_DVSN_2": "",             # 조회구분2
        "CTX_AREA_FK100": "",          # 연속조회검색조건
        "CTX_AREA_NK100": ""           # 연속조회키
    }
}

# LS API 관련 설정
LS_API_BASE_URL = {
    "paper": "https://openapi.ls-sec.co.kr:8080",  # 모의투자 API URL
    "live": "https://openapi.ls-sec.co.kr:8080"    # 실전투자 API URL
}

# LS API 엔드포인트
LS_API_ENDPOINTS = {
    "token": "/oauth2/token",           # 토큰 발급
    "balance": "/stock/accno",  # 잔고조회
    "daily_trades": "/stock/accno/trades"  # 거래내역조회
}

# LS API 트랜잭션 코드
LS_API_TR_ID = {
    "balance": "t0424",        # 잔고조회 TR 코드
    "daily_trades": "CDPCQ04700"  # 거래내역조회 TR 코드
}

# LS API 파라미터
LS_API_PARAMS = {
    "daily_trades": {
        "QryTp": "0",           # 전체 조회
        "QrySrtDt": "",         # 조회시작일
        "QryEndDt": "",         # 조회종료일
        "SrtNo": "0",           # 시작번호
        "PdptnCode": "01",      # 상품유형코드 (주식)
        "IsuLgclssCode": "01",  # 종목대분류코드 (주식)
        "IsuNo": ""             # 종목번호 (전체)
    }
}

# 로깅 관련 설정
LOG_FORMAT = "%(asctime)s - %(message)s"      # 로그 포맷
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"         # 로그 날짜 포맷 