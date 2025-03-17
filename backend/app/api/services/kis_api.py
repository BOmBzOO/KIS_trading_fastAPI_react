from datetime import datetime
import requests
from fastapi import HTTPException
from app.models import Account

def get_kis_access_token(app_key: str, app_secret: str, acnt_type: str) -> tuple[str, datetime]:
    """
    KIS API를 통해 access token을 받아옵니다.
    Returns:
        tuple[str, datetime]: (access_token, expires_at)
    """
    base_url = "https://openapi.koreainvestment.com:9443" if acnt_type == "live" else "https://openapivts.koreainvestment.com:29443"
    try:
        response = requests.post(
            f"{base_url}/oauth2/tokenP",
            json={
                "grant_type": "client_credentials",
                "appkey": app_key,
                "appsecret": app_secret
            }
        )
        response.raise_for_status()
        data = response.json()
        
        access_token = data.get("access_token", "")
        expires_at = datetime.strptime(data.get("access_token_token_expired", ""), "%Y-%m-%d %H:%M:%S")
        
        return access_token, expires_at
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"KIS API 토큰 발급 실패: {str(e)}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=f"KIS API 토큰 만료 시간 파싱 실패: {str(e)}"
        )

async def fetch_account_balance(account: Account) -> dict:
    """KIS API를 통해 계좌 잔고를 조회"""
    base_url = "https://openapi.koreainvestment.com:9443" if account.acnt_type == "live" else "https://openapivts.koreainvestment.com:29443"
    
    try:
        response = requests.get(
            f"{base_url}/uapi/domestic-stock/v1/trading/inquire-balance",
            params={
                "CANO": account.cano,
                "ACNT_PRDT_CD": account.acnt_prdt_cd,
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
            headers={
                "authorization": f"Bearer {account.kis_access_token}",
                "appkey": account.app_key,
                "appsecret": account.app_secret,
                "tr_id": "VTTC8434R" if account.acnt_type == "paper" else "TTTC8434R",
                "content-type": "application/json"
            }
        )
        response.raise_for_status()
        return response.json()
        
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"KIS API 잔고 조회 실패: {str(e)}"
        )

async def fetch_daily_trades(account: Account, start_date: str, end_date: str) -> dict:
    """KIS API를 통해 일별 주문체결 내역을 조회"""
    base_url = "https://openapi.koreainvestment.com:9443" if account.acnt_type == "live" else "https://openapivts.koreainvestment.com:29443"
    
    params = {
        "CANO": account.cano,
        "ACNT_PRDT_CD": account.acnt_prdt_cd,
        "INQR_STRT_DT": start_date.replace("-", ""),
        "INQR_END_DT": end_date.replace("-", ""),
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
    
    headers = {
        "authorization": f"Bearer {account.kis_access_token}",
        "appkey": account.app_key,
        "appsecret": account.app_secret,
        "tr_id": "TTTC8001R" if account.acnt_type == "live" else "VTTC8001R",
        "content-type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{base_url}/uapi/domestic-stock/v1/trading/inquire-daily-ccld",
            params=params,
            headers=headers
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get("rt_cd") != "0":
            raise HTTPException(
                status_code=400,
                detail=f"KIS API 오류: {data.get('msg1', '알 수 없는 오류')}"
            )
            
        return data
        
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"KIS API 호출 실패: {str(e)}"
        ) 