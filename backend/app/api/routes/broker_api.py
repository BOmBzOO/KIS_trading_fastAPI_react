from datetime import datetime, timedelta
import uuid
from typing import Any, List, Optional, Union
from fastapi import APIRouter, HTTPException, BackgroundTasks
from sqlmodel import Session

from app.api.deps import CurrentUser, SessionDep
from app.models.account import Account
from app.models.kis import Kis_Daily_Trade, Kis_Daily_Trade_Base, Kis_Minutely_Balance, Kis_Daily_Trade_Response, Kis_Balance_Response
from app.models.ls import Ls_Daily_Trade, Ls_Minutely_Balance, Ls_Balance_Response, Ls_Daily_Trade_Response, Ls_Daily_Trade_Base
from app.api.services.kis_api import get_access_token_KIS, inquire_balance_from_KIS, inquire_daily_ccld_from_KIS
from app.api.services.ls_api import get_access_token_LS, inquire_balance_from_LS, inquire_daily_ccld_from_LS
from app.api.services.background_tasks import start_background_tasks, stop_background_tasks, should_refresh_token
from app.api.services.kis_trade_service import process_trade_data_KIS, update_account_daily_trades_KIS
from app.api.services.ls_trade_service import process_trade_data_LS, update_account_daily_trades_LS
from app.constants import KST

router = APIRouter(prefix="/broker", tags=["broker-api"])

# 시작/종료 이벤트 핸들러는 그대로 유지
@router.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 백그라운드 태스크 시작"""
    start_background_tasks()

@router.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 백그라운드 태스크 중지"""
    stop_background_tasks()

def refresh_token_if_needed_kis(account: Account) -> None:
    """계정의 토큰이 만료되어가는 경우 갱신"""
    if should_refresh_token(account.access_token_expired):
        try:
            access_token, expires_at = get_access_token_KIS(
                app_key=account.app_key,
                app_secret=account.app_secret,
                acnt_type=account.acnt_type
            )
            account.access_token = access_token
            account.access_token_expired = expires_at
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"토큰 갱신 실패: {str(e)}"
            )

def refresh_token_if_needed_ls(account: Account) -> None:
    """LS 계정의 토큰이 만료되어가는 경우 갱신"""
    if should_refresh_token(account.access_token_expired):
        try:
            access_token, expires_at = get_access_token_LS(
                app_key=account.app_key,
                app_secret=account.app_secret,
                acnt_type=account.acnt_type
            )
            account.access_token = access_token
            account.access_token_expired = expires_at
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"토큰 갱신 실패: {str(e)}"
            )

@router.get("/{broker}/{account_id}/balance", response_model=Union[Kis_Balance_Response, Ls_Balance_Response])
async def get_account_balance(
    broker: str,
    account_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """계좌 잔고 조회"""
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if not current_user.is_superuser and (account.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    if broker.upper() != account.broker.upper():
        raise HTTPException(status_code=400, detail=f"Account broker mismatch. Expected: {account.broker}, Got: {broker.upper()}")

    if account.is_active:
        if broker.upper() == "KIS":
            refresh_token_if_needed_kis(account)
            session.commit()
            return await inquire_balance_from_KIS(account)
        elif broker.upper() == "LS":
            refresh_token_if_needed_ls(account)
            session.commit()
            return await inquire_balance_from_LS(account)
        else:
            raise HTTPException(status_code=400, detail="Unsupported broker")

@router.post("/{broker}/{account_id}/token/refresh")
def refresh_account_token(
    broker: str,
    account_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """계정 토큰 수동 갱신"""
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if not current_user.is_superuser and (account.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    if broker.upper() != account.broker.upper():
        raise HTTPException(status_code=400, detail=f"Account broker mismatch. Expected: {account.broker}, Got: {broker.upper()}")

    if not account.is_active:
        raise HTTPException(status_code=400, detail="Account is not active")

    try:
        if broker.upper() == "KIS":
            access_token, expires_at = get_access_token_KIS(
                app_key=account.app_key,
                app_secret=account.app_secret,
                acnt_type=account.acnt_type
            )
        elif broker.upper() == "LS":
            access_token, expires_at = get_access_token_LS(
                app_key=account.app_key,
                app_secret=account.app_secret,
                acnt_type=account.acnt_type
            )
            print(access_token, expires_at)
        else:
            raise HTTPException(status_code=400, detail="Unsupported broker")
        
        account.access_token = access_token
        account.access_token_expired = expires_at
        
        session.add(account)
        session.commit()
        session.refresh(account)
        
        return account
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refresh token: {str(e)}"
        )

@router.post("/{broker}/{account_id}/trades/daily", response_model=Union[Kis_Daily_Trade_Response, Ls_Daily_Trade_Response])
async def update_daily_trades(
    broker: str,
    account_id: uuid.UUID,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    background_tasks: BackgroundTasks = None,
    session: SessionDep = None,
    current_user: CurrentUser = None,
) -> Any:
    """일별 주문체결 내역 업데이트"""
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if not current_user.is_superuser and (account.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    if broker.upper() != account.broker.upper():
        raise HTTPException(status_code=400, detail=f"Account broker mismatch. Expected: {account.broker}, Got: {broker.upper()}")

    if not account.is_active:
        raise HTTPException(status_code=400, detail="Account is not active")

    try:
        if broker.upper() == "KIS":
            refresh_token_if_needed_kis(account)
            session.commit()
            return await inquire_daily_ccld_from_KIS(account, start_date, end_date)
        elif broker.upper() == "LS":
            refresh_token_if_needed_ls(account)
            session.commit()
            return await inquire_daily_ccld_from_LS(account, start_date, end_date)
        else:
            raise HTTPException(status_code=400, detail="Unsupported broker")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update daily trades: {str(e)}"
        )

@router.get("/{broker}/{account_id}/trades/daily", response_model=Union[List[Kis_Daily_Trade_Base], List[Ls_Daily_Trade_Base]])
async def get_daily_trades(
    broker: str,
    account_id: uuid.UUID,
    start_date: str,
    end_date: Optional[str] = None,
    stock_code: Optional[str] = None,
    session: SessionDep = None,
    current_user: CurrentUser = None,
) -> Any:
    """일별 주문체결 내역 조회"""
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if not current_user.is_superuser and (account.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    if broker.upper() != account.broker.upper():
        raise HTTPException(status_code=400, detail=f"Account broker mismatch. Expected: {account.broker}, Got: {broker.upper()}")

    if not account.is_active:
        raise HTTPException(status_code=400, detail="Account is not active")

    try:
        if broker.upper() == "KIS":
            refresh_token_if_needed_kis(account)
            session.commit()
            return await inquire_daily_ccld_from_KIS(account, start_date, end_date)
        elif broker.upper() == "LS":
            refresh_token_if_needed_ls(account)
            session.commit()
            return await inquire_daily_ccld_from_LS(account, start_date, end_date)
        else:
            raise HTTPException(status_code=400, detail="Unsupported broker")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get daily trades: {str(e)}"
        )

@router.get("/{broker}/{account_id}/balance/minutely", response_model=Union[Kis_Balance_Response, Ls_Balance_Response])
async def get_minutely_balance(
    broker: str,
    account_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """분별 잔고 조회"""
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if not current_user.is_superuser and (account.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    if broker.upper() != account.broker.upper():
        raise HTTPException(status_code=400, detail=f"Account broker mismatch. Expected: {account.broker}, Got: {broker.upper()}")

    if account.is_active:
        if broker.upper() == "KIS":
            refresh_token_if_needed_kis(account)
            session.commit()
            return await inquire_balance_from_KIS(account)
        elif broker.upper() == "LS":
            refresh_token_if_needed_ls(account)
            session.commit()
            return await inquire_balance_from_LS(account)
        else:
            raise HTTPException(status_code=400, detail="Unsupported broker")

@router.get("/{broker}/{account_id}/trades/minutely", response_model=Union[List[Kis_Daily_Trade], List[Ls_Daily_Trade]])
async def get_minutely_trades(
    broker: str,
    account_id: uuid.UUID,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    session: SessionDep = None,
    current_user: CurrentUser = None,
) -> Any:
    """분별 거래내역 조회"""
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if not current_user.is_superuser and (account.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    # 기본값으로 오늘 데이터 조회
    if not end_time:
        end_time = datetime.now(KST)
    if not start_time:
        start_time = end_time.replace(hour=9, minute=0, second=0, microsecond=0)
        if end_time.hour >= 15 and end_time.minute >= 30:
            end_time = end_time.replace(hour=15, minute=30, second=0, microsecond=0)

    # 브로커별 쿼리 생성
    if broker.upper() == "KIS":
        query = session.query(Kis_Minutely_Balance).filter(
            Kis_Minutely_Balance.account_id == account_id,
            Kis_Minutely_Balance.timestamp >= start_time,
            Kis_Minutely_Balance.timestamp <= end_time
        )
    elif broker.upper() == "LS":
        query = session.query(Ls_Minutely_Balance).filter(
            Ls_Minutely_Balance.account_id == account_id,
            Ls_Minutely_Balance.timestamp >= start_time,
            Ls_Minutely_Balance.timestamp <= end_time
        )
    else:
        raise HTTPException(status_code=400, detail="Unsupported broker")

    # 정렬 및 실행
    balances = query.order_by(
        Kis_Minutely_Balance.timestamp.asc() if broker.upper() == "KIS" 
        else Ls_Minutely_Balance.timestamp.asc()
    ).all()
    
    return balances 