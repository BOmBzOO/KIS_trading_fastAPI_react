import uuid
from typing import Any
from fastapi import APIRouter, HTTPException
from sqlmodel import func, select, Session
from sqlalchemy.orm import joinedload

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Account, Account_Create, Account_Public, Accounts_Public, 
    Account_Update, Message
)
from app.api.services.kis_api import get_access_token_KIS   
# LS API 서비스 import 필요
from app.api.services.ls_api import get_access_token_LS

router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.get("/", response_model=Accounts_Public)
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
    
    return Accounts_Public(data=accounts, count=count)

@router.get("/{account_id}", response_model=Account_Public)
def read_account(session: SessionDep, current_user: CurrentUser, account_id: uuid.UUID) -> Any:
    """특정 계정 조회"""
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if not current_user.is_superuser and (account.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    return account

@router.post("/", response_model=Account_Public)
async def create_account(
    *, session: SessionDep, current_user: CurrentUser, account_in: Account_Create
) -> Any:
    """새 계정 생성"""
    access_token = None
    expires_at = None
    
    # 브로커 타입에 따라 다른 API 호출
    if account_in.broker.lower() == "kis":
        access_token, expires_at = get_access_token_KIS(
            app_key=account_in.app_key,
            app_secret=account_in.app_secret,
            acnt_type=account_in.acnt_type
        )
    elif account_in.broker.lower() == "ls":
        access_token, expires_at = get_access_token_LS(
            app_key=account_in.app_key,
            app_secret=account_in.app_secret,
            acnt_type=account_in.acnt_type
        )
    else:
        raise HTTPException(
            status_code=400,
            detail="지원하지 않는 브로커입니다. (지원 브로커: kis, ls)"
        )

    # 임시 계정 객체 생성
    account = Account(
        broker=account_in.broker,
        acnt_name=account_in.acnt_name,
        cano=account_in.cano,
        acnt_prdt_cd=account_in.acnt_prdt_cd,
        acnt_type=account_in.acnt_type,
        hts_id=account_in.hts_id,
        is_active=account_in.is_active,
        app_key=account_in.app_key,
        app_secret=account_in.app_secret,
        discord_webhook_url=account_in.discord_webhook_url,
        access_token=access_token,
        access_token_expired=expires_at,
        approval_key=account_in.approval_key,
        owner_id=current_user.id
    )

    # LS 계정인 경우 계좌 정보 조회
    if account_in.broker.lower() == "ls":
        try:
            account_info = await inquire_account_info_from_LS(account)
            account.cano = account_info.get("cano", "")
            account.acnt_prdt_cd = account_info.get("acnt_prdt_cd", "")
            account.hts_id = account_info.get("hts_id", "")
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"LS 계좌 정보 조회 실패: {str(e)}"
            )

    print(account)
    
    session.add(account)
    session.commit()
    session.refresh(account)
    
    return account

@router.put("/{account_id}", response_model=Account_Public)
def update_account(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    account_id: uuid.UUID,
    account_in: Account_Update,
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
        if account.broker.lower() == "kis":
            access_token, expires_at = get_access_token_KIS(
                app_key=account_data.get('app_key', account.app_key),
                app_secret=account_data.get('app_secret', account.app_secret),
                acnt_type=account_data.get('acnt_type', account.acnt_type)
            )
        elif account.broker.lower() == "ls":
            access_token, expires_at = get_access_token_LS(
                app_key=account_data.get('app_key', account.app_key),
                app_secret=account_data.get('app_secret', account.app_secret),
                acnt_type=account_data.get('acnt_type', account.acnt_type)
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="지원하지 않는 브로커입니다. (지원 브로커: kis, ls)"
            )
            
        account_data['access_token'] = access_token
        account_data['access_token_expired'] = expires_at

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
