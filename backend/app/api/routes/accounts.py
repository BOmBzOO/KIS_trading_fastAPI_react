from datetime import datetime, timedelta
import uuid
from typing import Any, List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from sqlmodel import func, select, Session
from sqlalchemy.orm import joinedload

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Account, AccountCreate, AccountPublic, AccountsPublic, 
    AccountUpdate, Message, DailyTrade, DailyTradeBase, 
    MinutelyBalance, DailyTradeResponse, BalanceResponse
)
from app.api.services.kis_api import get_kis_access_token, fetch_account_balance, fetch_daily_trades
from app.api.services.background_tasks import (
    start_background_tasks, stop_background_tasks, 
    should_refresh_token
)
from app.api.services.trade_service import process_trade_data

router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 백그라운드 태스크 시작"""
    start_background_tasks()

@router.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 백그라운드 태스크 중지"""
    stop_background_tasks()

def refresh_token_if_needed(account: Account) -> None:
    """계정의 토큰이 만료되어가는 경우 갱신"""
    if should_refresh_token(account.access_token_expired):
        try:
            access_token, expires_at = get_kis_access_token(
                app_key=account.app_key,
                app_secret=account.app_secret,
                acnt_type=account.acnt_type
            )
            account.kis_access_token = access_token
            account.access_token_expired = expires_at
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"토큰 갱신 실패: {str(e)}"
            )

@router.get("/", response_model=AccountsPublic)
def read_accounts(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """계정 목록 조회"""
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Account)
        count = session.exec(count_statement).one()
        statement = (
            select(Account)
            .options(joinedload(Account.owner))
            .offset(skip)
            .limit(limit)
        )
        accounts = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Account)
            .where(Account.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Account)
            .options(joinedload(Account.owner))
            .where(Account.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        accounts = session.exec(statement).all()

    # 각 계정의 토큰 상태를 확인하고 필요한 경우 갱신
    for account in accounts:
        if account.is_active:
            refresh_token_if_needed(account)
    
    session.commit()
    return AccountsPublic(data=accounts, count=count)

@router.get("/{account_id}", response_model=AccountPublic)
def read_account(session: SessionDep, current_user: CurrentUser, account_id: uuid.UUID) -> Any:
    """특정 계정 조회"""
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if not current_user.is_superuser and (account.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    if account.is_active:
        refresh_token_if_needed(account)
        session.commit()
    
    return account

@router.post("/", response_model=AccountPublic)
def create_account(
    *, session: SessionDep, current_user: CurrentUser, account_in: AccountCreate
) -> Any:
    """새 계정 생성"""
    access_token, expires_at = get_kis_access_token(
        app_key=account_in.app_key,
        app_secret=account_in.app_secret,
        acnt_type=account_in.acnt_type
    )

    account = Account(
        acnt_name=account_in.acnt_name,
        cano=account_in.cano,
        acnt_prdt_cd=account_in.acnt_prdt_cd,
        acnt_type=account_in.acnt_type,
        hts_id=account_in.hts_id,
        is_active=account_in.is_active,
        app_key=account_in.app_key,
        app_secret=account_in.app_secret,
        discord_webhook_url=account_in.discord_webhook_url,
        kis_access_token=access_token,
        access_token_expired=expires_at,
        owner_id=current_user.id
    )
    
    session.add(account)
    session.commit()
    session.refresh(account)
    
    return account

@router.put("/{account_id}", response_model=AccountPublic)
def update_account(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    account_id: uuid.UUID,
    account_in: AccountUpdate,
) -> Any:
    """계정 정보 업데이트"""
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if not current_user.is_superuser and (account.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    account_data = account_in.model_dump(exclude_unset=True)
    
    # 자격 증명 관련 필드가 업데이트되면 토큰 갱신
    credentials_updated = any(field in account_data for field in ['app_key', 'app_secret', 'acnt_type'])
    if credentials_updated and account.is_active:
        access_token, expires_at = get_kis_access_token(
            app_key=account_data.get('app_key', account.app_key),
            app_secret=account_data.get('app_secret', account.app_secret),
            acnt_type=account_data.get('acnt_type', account.acnt_type)
        )
        account_data['kis_access_token'] = access_token
        account_data['access_token_expired'] = expires_at
    elif account.is_active:
        refresh_token_if_needed(account)

    for field, value in account_data.items():
        setattr(account, field, value)

    session.add(account)
    session.commit()
    session.refresh(account)
    return account

@router.delete("/{account_id}")
def delete_account(
    session: SessionDep, current_user: CurrentUser, account_id: uuid.UUID
) -> Message:
    """계정 삭제"""
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if not current_user.is_superuser and (account.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    session.delete(account)
    session.commit()
    return Message(message="Account deleted successfully")

@router.get("/{account_id}/balance", response_model=BalanceResponse)
async def get_account_balance(
    session: SessionDep,
    current_user: CurrentUser,
    account_id: uuid.UUID
) -> Any:
    """계좌 잔고 조회"""
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if not current_user.is_superuser and (account.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    if account.is_active:
        refresh_token_if_needed(account)
        session.commit()
    
    return await fetch_account_balance(account)

@router.post("/{account_id}/token_refresh", response_model=AccountPublic)
def refresh_account_token(
    session: SessionDep,
    current_user: CurrentUser,
    account_id: uuid.UUID
) -> Any:
    """계정 토큰 수동 갱신"""
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if not current_user.is_superuser and (account.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    if not account.is_active:
        raise HTTPException(status_code=400, detail="Account is not active")

    try:
        access_token, expires_at = get_kis_access_token(
            app_key=account.app_key,
            app_secret=account.app_secret,
            acnt_type=account.acnt_type
        )
        
        account.kis_access_token = access_token
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

@router.post("/{account_id}/update-daily-trades", response_model=DailyTradeResponse)
async def update_daily_trades(
    account_id: uuid.UUID,
    start_date: str | None = None,
    end_date: str | None = None,
    background_tasks: BackgroundTasks = None,
    session: SessionDep = None,
    current_user: CurrentUser = None,
) -> Any:
    """일별 주문체결 내역 업데이트"""
    errors = []
    updated_count = 0

    try:
        # 날짜 범위 설정
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        # 계좌 정보 조회 및 권한 확인
        account = session.get(Account, account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        if not current_user.is_superuser and (account.owner_id != current_user.id):
            raise HTTPException(status_code=400, detail="Not enough permissions")

        # 토큰 상태 확인 및 갱신
        if account.is_active:
            refresh_token_if_needed(account)
            session.commit()

        # KIS API 호출
        trade_data = await fetch_daily_trades(account, start_date, end_date)
        
        if not trade_data.get("output1"):
            return DailyTradeResponse(
                message="조회된 거래 내역이 없습니다.",
                updated_count=0,
                start_date=start_date,
                end_date=end_date,
                error_count=0,
                errors=[]
            )

        # DB 업데이트
        try:
            for trade in process_trade_data(trade_data, str(account_id)):
                try:
                    statement = select(DailyTrade).where(
                        DailyTrade.account_id == account_id,
                        DailyTrade.order_date == trade.order_date,
                        DailyTrade.order_no == trade.order_no
                    )
                    existing_trade = session.exec(statement).first()

                    if existing_trade:
                        # 기존 거래 업데이트
                        for key, value in trade.model_dump().items():
                            setattr(existing_trade, key, value)
                    else:
                        # 새 거래 추가
                        session.add(trade)

                    updated_count += 1

                except Exception as e:
                    errors.append(f"거래 데이터 처리 실패 (주문번호: {trade.order_no}): {str(e)}")
                    continue

            session.commit()

        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=500, detail=f"데이터베이스 저장 실패: {str(e)}")

        return DailyTradeResponse(
            message=f"일별 주문체결 내역이 업데이트되었습니다. (총 {updated_count}건)",
            updated_count=updated_count,
            start_date=start_date,
            end_date=end_date,
            error_count=len(errors),
            errors=errors
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"데이터 업데이트 실패: {str(e)}"
        )

@router.get("/{account_id}/daily-trades", response_model=List[DailyTradeBase])
async def get_daily_trades(
    account_id: uuid.UUID,
    start_date: str,
    end_date: str | None = None,
    stock_code: str | None = None,
    session: SessionDep = None,
    current_user: CurrentUser = None,
) -> Any:
    """일별 주문체결 내역 조회"""
    # 권한 확인
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if not current_user.is_superuser and (account.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    # 쿼리 생성
    query = session.query(DailyTrade).filter(
        DailyTrade.account_id == account_id,
        DailyTrade.order_date >= start_date.replace("-", "")
    )

    if end_date:
        query = query.filter(DailyTrade.order_date <= end_date.replace("-", ""))
    if stock_code:
        query = query.filter(DailyTrade.stock_code == stock_code)

    # 정렬 및 실행
    trades = query.order_by(DailyTrade.order_date.desc(), DailyTrade.order_time.desc()).all()
    return trades

@router.get("/{account_id}/minutely-balances", response_model=List[MinutelyBalance])
async def get_minutely_balances(
    account_id: uuid.UUID,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    session: SessionDep = None,
    current_user: CurrentUser = None,
) -> Any:
    """분당 잔고 데이터 조회"""
    # 권한 확인
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if not current_user.is_superuser and (account.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    # 기본값으로 오늘 데이터 조회
    if not end_time:
        end_time = datetime.now()
    if not start_time:
        start_time = end_time.replace(hour=9, minute=0, second=0, microsecond=0)
        if end_time.hour >= 15 and end_time.minute >= 30:
            end_time = end_time.replace(hour=15, minute=30, second=0, microsecond=0)

    # 쿼리 생성
    query = session.query(MinutelyBalance).filter(
        MinutelyBalance.account_id == account_id,
        MinutelyBalance.timestamp >= start_time,
        MinutelyBalance.timestamp <= end_time
    )

    # 정렬 및 실행
    balances = query.order_by(MinutelyBalance.timestamp.asc()).all()
    return balances
