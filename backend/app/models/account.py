import uuid
from datetime import datetime
from pytz import timezone
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import TIMESTAMP, Column, Index, text, UniqueConstraint
from typing import Optional, List
from app.models.kis import Kis_Daily_Trade, Kis_Minutely_Balance
from app.models.ls import Ls_Daily_Trade, Ls_Minutely_Balance
from app.models.user import User
from zoneinfo import ZoneInfo

class Account_Base(SQLModel):
    """계좌 기본 모델"""
    broker: str = Field(default="KIS", max_length=10, description="증권사 구분 (KIS/LS)")
    acnt_name: str = Field(max_length=255, description="계좌명")
    cano: str = Field(default=None, max_length=20, description="계좌번호")
    acnt_prdt_cd: Optional[str] = Field(default=None, max_length=20, description="계좌상품코드")
    acnt_type: str = Field(max_length=50, description="계좌유형 (paper/live)")
    hts_id: Optional[str] = Field(default=None, max_length=50, description="HTS ID")
    is_active: bool = Field(default=True, description="계좌 활성화 여부")
    app_key: str = Field(max_length=255, description="API 앱키")
    app_secret: str = Field(max_length=255, description="API 시크릿키")
    approval_key: Optional[str] = Field(default=None, max_length=255, description="승인키")
    discord_webhook_url: Optional[str] = Field(default=None, max_length=255, description="디스코드 웹훅 URL")
    access_token: Optional[str] = Field(default=None, max_length=1024, description="접근 토큰")
    access_token_expired: Optional[datetime] = Field(
        default=None,
        sa_column=Column(TIMESTAMP(timezone=True), nullable=True),
        description="토큰 만료일시"
    )
    mac_address: Optional[str] = Field(default=None, max_length=12, description="MAC 주소 (LS 증권 법인 계좌용)")

    class Config:
        json_schema_extra = {
            "example": {
                "broker": "KIS",
                "acnt_name": "주식계좌1",
                "cano": "50123456",
                "acnt_prdt_cd": "01",
                "acnt_type": "live",
                "hts_id": "user123",
                "is_active": True,
                "app_key": "PSQcX5TxxxxxxxxxxxxxxxxxxxxxxxxxxxxxY=",
                "app_secret": "gXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx=",
                "approval_key": "PSQcX5TxxxxxxxxxxxxxxxxxxxxxxxxxxxxxY=",
                "discord_webhook_url": "https://discord.com/api/webhooks/xxx/xxx"
            }
        }

# Properties to receive on account creation
class Account_Create(Account_Base):
    class Config:
        json_schema_extra = {
            "example": {
                "broker": "KIS",
                "acnt_name": "주식계좌1",
                "cano": "50123456",
                "acnt_prdt_cd": "01",
                "acnt_type": "live",
                "hts_id": "user123",
                "is_active": True,
                "app_key": "PSQcX5TxxxxxxxxxxxxxxxxxxxxxxxxxxxxxY=",
                "app_secret": "gXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx=",
                "approval_key": "PSQcX5TxxxxxxxxxxxxxxxxxxxxxxxxxxxxxY=",
                "discord_webhook_url": "https://discord.com/api/webhooks/xxx/xxx"
            }
        }

# Properties to receive on account update
class Account_Update(Account_Base):
    """계좌 수정 모델"""
    broker: Optional[str] = Field(default=None, max_length=10, description="증권사 구분 (KIS/LS)")
    cano: Optional[str] = Field(default=None, max_length=20, description="계좌번호")
    acnt_prdt_cd: Optional[str] = Field(default=None, max_length=20, description="계좌상품코드")
    hts_id: Optional[str] = Field(default=None, max_length=50, description="HTS ID")
    is_active: Optional[bool] = None
    app_key: Optional[str] = Field(default=None, max_length=255, description="API 앱키")
    app_secret: Optional[str] = Field(default=None, max_length=255, description="API 시크릿키")
    discord_webhook_url: Optional[str] = Field(default=None, max_length=255, description="디스코드 웹훅 URL")
    access_token: Optional[str] = Field(default=None, max_length=1024, description="접근 토큰")
    access_token_expired: Optional[datetime] = Field(
        default=None,
        sa_column=Column(TIMESTAMP(timezone=True), nullable=True),
        description="토큰 만료일시"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "broker": "KIS",
                "acnt_name": "주식계좌1",
                "cano": "50123456",
                "acnt_prdt_cd": "01",
                "acnt_type": "live",
                "hts_id": "user123",
                "is_active": True,
                "app_key": "PSQcX5TxxxxxxxxxxxxxxxxxxxxxxxxxxxxxY=",
                "app_secret": "gXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx=",
                "discord_webhook_url": "https://discord.com/api/webhooks/xxx/xxx",
                "access_token": "eyJhbGciOiJIxxxxxxxxxxxxx",
                "access_token_expired": "2024-03-19T15:30:00+09:00",
                "approval_key": "PSQcX5TxxxxxxxxxxxxxxxxxxxxxxxxxxxxxY="
            }
        }

# Database model
class Account(Account_Base, table=True):
    """계좌 테이블"""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="계좌 ID")
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE", description="소유자 ID")
    owner: Optional["User"] = Relationship(back_populates="accounts")
    owner_name: Optional[str] = None
    
    # 일별 데이터 관계
    kis_daily_trades: List["Kis_Daily_Trade"] = Relationship(back_populates="account", cascade_delete=True)
    kis_minutely_balances: List["Kis_Minutely_Balance"] = Relationship(back_populates="account", cascade_delete=True)
    ls_daily_trades: List["Ls_Daily_Trade"] = Relationship(back_populates="account", cascade_delete=True)
    ls_minutely_balances: List["Ls_Minutely_Balance"] = Relationship(back_populates="account", cascade_delete=True)
    
    # 실시간 데이터 관계
    kis_balances: List["Kis_Balance"] = Relationship(back_populates="account")
    kis_trades: List["Kis_Trade"] = Relationship(back_populates="account")
    ls_balances: List["Ls_Balance"] = Relationship(back_populates="account")
    ls_trades: List["Ls_Trade"] = Relationship(back_populates="account")
    
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(ZoneInfo("Asia/Seoul")),
        sa_column=Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP")),
        description="생성일시"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(ZoneInfo("Asia/Seoul")),
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("CURRENT_TIMESTAMP"),
            onupdate=lambda: datetime.now(ZoneInfo("Asia/Seoul"))
        ),
        description="수정일시"
    )

    def __init__(self, **data):
        super().__init__(**data)
        if self.owner:
            self.owner_name = self.owner.full_name if self.owner.full_name else self.owner.email

    class Config:
        table_name = "accounts"
        description = "계좌 정보 테이블"

    __table_args__ = (
        UniqueConstraint('owner_id', 'cano', name='uix_owner_acnt'),
        Index('ix_accounts_owner', 'owner_id'),
        Index('ix_accounts_broker', 'broker'),
        Index('ix_accounts_type', 'acnt_type'),
    )

# Properties to return via API
class Account_Public(Account_Base):
    """계좌 공개 모델"""
    id: uuid.UUID
    owner_id: uuid.UUID
    owner_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    access_token: Optional[str] = Field(default=None, max_length=1024)
    access_token_expired: Optional[datetime] = Field(default=None)
    approval_key: Optional[str] = Field(default=None, max_length=255)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "owner_id": "123e4567-e89b-12d3-a456-426614174111",
                "broker": "KIS",
                "owner_name": "홍길동",
                "acnt_name": "주식계좌1",
                "cano": "50123456",
                "acnt_prdt_cd": "01",
                "acnt_type": "live",
                "hts_id": "user123",
                "is_active": True,
                "app_key": "PSQcX5TxxxxxxxxxxxxxxxxxxxxxxxxxxxxxY=",
                "app_secret": "gXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx=",
                "discord_webhook_url": "https://discord.com/api/webhooks/xxx/xxx",
                "access_token": "eyJhbGciOiJIxxxxxxxxxxxxx",
                "access_token_expired": "2024-03-19T15:30:00+09:00",
                "approval_key": "PSQcX5TxxxxxxxxxxxxxxxxxxxxxxxxxxxxxY="
            }
        }

class Accounts_Public(SQLModel):
    """계좌 목록 공개 모델"""
    data: list[Account_Public]
    count: int

    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "owner_id": "123e4567-e89b-12d3-a456-426614174111",
                        "owner_name": "홍길동",
                        "acnt_name": "주식계좌1",
                        "cano": "50123456",
                        "acnt_prdt_cd": "01",
                        "acnt_type": "live",
                        "hts_id": "user123",
                        "is_active": True,
                        "app_key": "PSQcX5TxxxxxxxxxxxxxxxxxxxxxxxxxxxxxY=",
                        "app_secret": "gXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx=",
                        "approval_key": "PSQcX5TxxxxxxxxxxxxxxxxxxxxxxxxxxxxxY=",
                        "discord_webhook_url": "https://discord.com/api/webhooks/xxx/xxx",
                        "access_token": "eyJhbGciOiJIxxxxxxxxxxxxx",
                        "access_token_expired": "2024-03-19T15:30:00+09:00"
                    }
                ],
                "count": 1
            }
        } 