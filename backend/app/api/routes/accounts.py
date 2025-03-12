import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Account, AccountAPIConfig, AccountCreate, AccountPublic, AccountsPublic, AccountUpdate, Message

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("/", response_model=AccountsPublic)
def read_accounts(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve accounts.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Account)
        count = session.exec(count_statement).one()
        statement = select(Account).offset(skip).limit(limit)
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
            .where(Account.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        accounts = session.exec(statement).all()

    return AccountsPublic(data=accounts, count=count)


@router.get("/{account_id}", response_model=AccountPublic)
def read_account(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get account by ID.
    """
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (account.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return account


@router.post("/", response_model=AccountPublic)
def create_account(
    *, session: SessionDep, current_user: CurrentUser, account_in: AccountCreate
) -> Any:
    """
    Create new account with API configuration.
    """
    # Create account
    account = Account(
        acnt_name=account_in.acnt_name,
        cano=account_in.cano,
        acnt_prdt_cd=account_in.acnt_prdt_cd,
        acnt_type=account_in.acnt_type,
        hts_id=account_in.hts_id,
        is_active=account_in.is_active,
        owner_id=current_user.id,
    )
    session.add(account)
    session.commit()  # ✅ flush() 대신 commit()을 사용하여 account.id 보장
    session.refresh(account)  # ✅ 새로고침하여 account.id가 확실히 존재하도록 함

    # Create API config
    api_config = AccountAPIConfig(
        app_key=account_in.app_key,
        app_secret=account_in.app_secret,
        discord_webhook_url=account_in.discord_webhook_url,
        account_id=account.id,
    )
    session.add(api_config)
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
    """
    Update an account and its API configuration.
    """
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (account.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    # Update account fields
    account_data = account_in.model_dump(
        exclude={"app_key", "app_secret", "discord_webhook_url"},
        exclude_unset=True,
    )
    for field, value in account_data.items():
        setattr(account, field, value)

    # Update API config if it exists, create if it doesn't
    api_config = account.api_config
    api_config_data = account_in.model_dump(
        include={"app_key", "app_secret", "discord_webhook_url"},
        exclude_unset=True,
    )
    
    if api_config_data:
        if api_config is None:
            api_config = AccountAPIConfig(account_id=account.id)
            session.add(api_config)
        for field, value in api_config_data.items():
            setattr(api_config, field, value)

    session.add(account)
    session.commit()
    session.refresh(account)
    return account


@router.delete("/{account_id}")
def delete_account(
    session: SessionDep, current_user: CurrentUser, account_id: uuid.UUID
) -> Message:
    """
    Delete an account.
    """
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (account.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # ✅ AccountAPIConfig 먼저 삭제
    if account.api_config:
        session.delete(account.api_config)

    session.delete(account)  # This will cascade delete the api_config due to the relationship
    session.commit()
    return Message(message="Account deleted successfully")
