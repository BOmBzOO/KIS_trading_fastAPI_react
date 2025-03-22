from datetime import datetime
import requests
from fastapi import HTTPException
from app.models.account import Account
from app.constants import (
    KIS_API_BASE_URL,
    KIS_API_ENDPOINTS,
    KIS_API_TR_ID,
    KIS_API_PARAMS
)
from typing import Any

def get_access_token_KIS(app_key: str, app_secret: str, acnt_type: str) -> tuple[str, datetime]:
    """
    KIS API를 통해 access token을 받아옵니다.
    Returns:
        tuple[str, datetime]: (access_token, expires_at)
    """
    base_url = KIS_API_BASE_URL[acnt_type]
    try:
        response = requests.post(
            f"{base_url}{KIS_API_ENDPOINTS['token']}",
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

async def inquire_balance_from_KIS(account: Account) -> Any:
    """KIS API를 통한 잔고 조회"""
    base_url = KIS_API_BASE_URL[account.acnt_type]
    
    try:
        response = requests.get(
            f"{base_url}{KIS_API_ENDPOINTS['balance']}",
            params={
                "CANO": account.cano,
                "ACNT_PRDT_CD": account.acnt_prdt_cd,
                **KIS_API_PARAMS["balance"]
            },
            headers={
                "authorization": f"Bearer {account.access_token}",
                "appkey": account.app_key,
                "appsecret": account.app_secret,
                "tr_id": KIS_API_TR_ID["balance"][account.acnt_type],
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

async def inquire_daily_ccld_from_KIS(account: Account, start_date: str, end_date: str) -> dict:
    """KIS API를 통해 일별 주문체결 내역을 조회"""
    base_url = KIS_API_BASE_URL[account.acnt_type]
    
    params = {
        "CANO": account.cano,
        "ACNT_PRDT_CD": account.acnt_prdt_cd,
        "INQR_STRT_DT": start_date.replace("-", ""),
        "INQR_END_DT": end_date.replace("-", ""),
        **KIS_API_PARAMS["daily_trades"]
    }
    
    headers = {
        "authorization": f"Bearer {account.access_token}",
        "appkey": account.app_key,
        "appsecret": account.app_secret,
        "tr_id": KIS_API_TR_ID["daily_trades"][account.acnt_type],
        "content-type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{base_url}{KIS_API_ENDPOINTS['daily_trades']}",
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