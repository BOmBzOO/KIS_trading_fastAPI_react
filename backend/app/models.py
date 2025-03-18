import uuid
from datetime import datetime
from pytz import timezone

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import TIMESTAMP, Column, Index, UniqueConstraint, text, JSON

# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    accounts: list["Account"] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int
    

#########################################################################
# Shared properties
class AccountBase(SQLModel):
    acnt_name: str | None = Field(default=None, max_length=50)
    cano: str = Field(max_length=20)
    acnt_prdt_cd: str = Field(max_length=20)
    acnt_type: str = Field(max_length=10)  # live 또는 virtual
    hts_id: str = Field(max_length=50)
    is_active: bool = True
    app_key: str = Field(max_length=255)
    app_secret: str = Field(max_length=1024)
    discord_webhook_url: str | None = Field(default=None, max_length=255)

    class Config:
        json_schema_extra = {
            "example": {
                "acnt_name": "주식계좌1",
                "cano": "50123456",
                "acnt_prdt_cd": "01",
                "acnt_type": "live",
                "hts_id": "user123",
                "is_active": True,
                "app_key": "PSQcX5TxxxxxxxxxxxxxxxxxxxxxxxxxxxxxY=",
                "app_secret": "gXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx=",
                "discord_webhook_url": "https://discord.com/api/webhooks/xxx/xxx"
            }
        }

# Properties to receive on account creation
class AccountCreate(AccountBase):
    class Config:
        json_schema_extra = {
            "example": {
                "acnt_name": "주식계좌1",
                "cano": "50123456",
                "acnt_prdt_cd": "01",
                "acnt_type": "live",
                "hts_id": "user123",
                "is_active": True,
                "app_key": "PSQcX5TxxxxxxxxxxxxxxxxxxxxxxxxxxxxxY=",
                "app_secret": "gXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx=",
                "discord_webhook_url": "https://discord.com/api/webhooks/xxx/xxx"
            }
        }

# Properties to receive on account update
class AccountUpdate(SQLModel):
    acnt_name: str | None = Field(default=None, max_length=50)
    cano: str | None = Field(default=None, max_length=20)
    acnt_prdt_cd: str | None = Field(default=None, max_length=20)
    acnt_type: str | None = Field(default=None, max_length=10)
    hts_id: str | None = Field(default=None, max_length=50)
    is_active: bool | None = None
    app_key: str | None = Field(default=None, max_length=255)
    app_secret: str | None = Field(default=None, max_length=1024)
    discord_webhook_url: str | None = Field(default=None, max_length=255)
    kis_access_token: str | None = Field(default=None, max_length=1024)
    access_token_expired: datetime | None = Field(default=None, sa_column=Column(TIMESTAMP(timezone=True)))

    class Config:
        json_schema_extra = {
            "example": {
                "acnt_name": "주식계좌1",
                "cano": "50123456",
                "acnt_prdt_cd": "01",
                "acnt_type": "live",
                "hts_id": "user123",
                "is_active": True,
                "app_key": "PSQcX5TxxxxxxxxxxxxxxxxxxxxxxxxxxxxxY=",
                "app_secret": "gXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx=",
                "discord_webhook_url": "https://discord.com/api/webhooks/xxx/xxx",
                "kis_access_token": "eyJhbGciOiJIxxxxxxxxxxxxx",
                "access_token_expired": "2024-03-19T15:30:00+09:00"
            }
        }

class DailyTradeBase(SQLModel):
    # output1 필드
    order_date: str = Field(max_length=8, description="주문일자 (YYYYMMDD)")
    stock_code: str = Field(max_length=10, description="종묩코드")
    stock_name: str = Field(max_length=50, description="종목명")
    order_no: str = Field(max_length=10, description="주문번호")
    order_time: str = Field(max_length=6, description="주문시각 (HHMMSS)")
    order_type: str = Field(max_length=2, description="매매구분코드 (01:매도, 02:매수)")
    order_price: float = Field(description="주문단가")
    order_qty: int = Field(description="주문수량")
    trade_price: float = Field(default=0, description="체결단가")
    trade_qty: int = Field(default=0, description="체결수량")
    trade_amount: float = Field(default=0, description="체결금액")
    trade_time: str | None = Field(default=None, max_length=6, description="체결시각")
    total_trade_qty: int = Field(default=0, description="총체결수량")
    remaining_qty: int = Field(default=0, description="주문잔량")
    cancel_qty: int = Field(default=0, description="취소수량")
    
    # output1의 추가 필드들
    original_order_no: str | None = Field(default=None, max_length=10, description="원주문번호")
    order_type_name: str | None = Field(default=None, max_length=20, description="주문구분명")
    order_type_detail_name: str | None = Field(default=None, max_length=20, description="매매구분명")
    cancel_yn: str | None = Field(default=None, max_length=1, description="취소여부")
    loan_date: str | None = Field(default=None, max_length=8, description="대출일자")
    order_branch_no: str | None = Field(default=None, max_length=5, description="주문점번호")
    order_media_code: str | None = Field(default=None, max_length=2, description="주문매체구분코드")
    reject_qty: int = Field(default=0, description="거부수량")
    trade_condition_name: str | None = Field(default=None, max_length=20, description="체결조건명")
    inqr_ip_addr: str | None = Field(default=None, max_length=20, description="조회 IP주소")
    order_method_code: str | None = Field(default=None, max_length=2, description="주문처리구분코드")
    order_info_code: str | None = Field(default=None, max_length=2, description="주문정보분류코드")
    info_update_time: str | None = Field(default=None, max_length=6, description="정보변경시각")
    phone_number: str | None = Field(default=None, max_length=20, description="연락전화번호")
    product_type_code: str | None = Field(default=None, max_length=3, description="상품유형코드")
    exchange_code: str | None = Field(default=None, max_length=2, description="거래소코드")
    order_material_code: str | None = Field(default=None, max_length=2, description="주문매체유형코드")
    order_org_no: str | None = Field(default=None, max_length=5, description="주문조직번호")
    reserve_order_end_date: str | None = Field(default=None, max_length=8, description="예약주문종료일자")
    exchange_id_code: str | None = Field(default=None, max_length=3, description="거래소ID구분코드")
    stop_condition_price: float = Field(default=0, description="스탑조건가격")
    stop_effect_time: str | None = Field(default=None, max_length=14, description="스탑발동시각")

    # output2 필드들 (일별 합산 정보)
    total_order_qty_sum: int | None = Field(default=None, description="총주문수량")
    total_trade_qty_sum: int | None = Field(default=None, description="총체결수량")
    total_trade_amt_sum: float | None = Field(default=None, description="총체결금액")
    estimated_tax_amt: float | None = Field(default=None, description="추정제비용합")
    avg_trade_price: float | None = Field(default=None, description="매수평균가격")

class DailyTrade(DailyTradeBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    account_id: uuid.UUID = Field(foreign_key="account.id", nullable=False)
    account: "Account" = Relationship(back_populates="daily_trades")
    
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone('Asia/Seoul')),
        sa_column=Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone('Asia/Seoul')),
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("CURRENT_TIMESTAMP"),
            onupdate=lambda: datetime.now(timezone('Asia/Seoul'))
        )
    )

    class Config:
        table_name = "daily_trades"

    __table_args__ = (
        UniqueConstraint('account_id', 'order_date', 'order_no', name='uix_account_order'),
        Index('ix_daily_trades_account_date', 'account_id', 'order_date'),
        Index('ix_daily_trades_stock', 'account_id', 'stock_code'),
    )

# Database model
class Account(AccountBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    owner: User | None = Relationship(back_populates="accounts")
    owner_name: str | None = None
    kis_access_token: str | None = Field(default=None, max_length=1024)
    access_token_expired: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone('Asia/Seoul')), 
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("CURRENT_TIMESTAMP")
        )
    )
    daily_trades: list["DailyTrade"] = Relationship(back_populates="account", cascade_delete=True)
    minutely_balances: list["MinutelyBalance"] = Relationship(back_populates="account", cascade_delete=True)

    def __init__(self, **data):
        super().__init__(**data)
        if self.owner:
            self.owner_name = self.owner.full_name if self.owner.full_name else self.owner.email

# Properties to return via API
class AccountPublic(AccountBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    owner_name: str | None = None
    kis_access_token: str | None = Field(default=None, max_length=1024)
    access_token_expired: datetime | None = Field(default=None)

    class Config:
        json_schema_extra = {
            "example": {
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
                "discord_webhook_url": "https://discord.com/api/webhooks/xxx/xxx",
                "kis_access_token": "eyJhbGciOiJIxxxxxxxxxxxxx",
                "access_token_expired": "2024-03-19T15:30:00+09:00"
            }
        }

class AccountsPublic(SQLModel):
    data: list[AccountPublic]
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
                        "discord_webhook_url": "https://discord.com/api/webhooks/xxx/xxx",
                        "kis_access_token": "eyJhbGciOiJIxxxxxxxxxxxxx",
                        "access_token_expired": "2024-03-19T15:30:00+09:00"
                    }
                ],
                "count": 1
            }
        }

class DailyTradeResponse(SQLModel):
    message: str
    updated_count: int
    start_date: str
    end_date: str
    error_count: int
    errors: list[str]

    class Config:
        json_schema_extra = {
            "example": {
                "message": "일별 거래내역이 성공적으로 업데이트되었습니다.",
                "updated_count": 5,
                "start_date": "20240301",
                "end_date": "20240319",
                "error_count": 0,
                "errors": []
            }
        }

class BalanceResponse(SQLModel):
    rt_cd: str | None = None
    msg1: str | None = None
    msg_cd: str | None = None
    output1: list[dict] | None = Field(default=None, description="보유종목 상세내역")
    output2: list[dict] | None = Field(default=None, description="계좌잔고 종합")

    class Config:
        json_schema_extra = {
            "example": {
                "rt_cd": "0",
                "msg1": "정상처리",
                "msg_cd": "MCA00000",
                "output1": [
                    {
                        "pdno": "005930",
                        "prdt_name": "삼성전자",
                        "hldg_qty": 10,
                        "pchs_avg_pric": 70000,
                        "prpr": 73000,
                        "evlu_pfls_amt": 30000,
                        "evlu_pfls_rt": 4.28
                    }
                ],
                "output2": [
                    {
                        "dnca_tot_amt": 1000000,
                        "tot_evlu_amt": 5000000,
                        "pchs_amt_smtl": 4800000,
                        "evlu_amt_smtl": 5000000,
                        "evlu_pfls_smtl": 200000,
                        "tot_evlu_pfls_rt": 4.17
                    }
                ]
            }
        }

# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


class MinutelyBalance(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    account_id: uuid.UUID = Field(foreign_key="account.id", nullable=False)
    account: "Account" = Relationship(back_populates="minutely_balances")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone('Asia/Seoul')),
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("CURRENT_TIMESTAMP")
        )
    )
    
    # 계좌 요약 정보
    total_balance: float = Field(description="예수금총금액")
    available_balance: float = Field(description="D+2 예수금")
    total_assets: float = Field(description="총평가금액")
    purchase_amount: float = Field(description="매입금액합계금액")
    eval_amount: float = Field(description="평가금액합계금액")
    profit_loss: float = Field(description="평가손익합계금액")
    profit_loss_rate: float = Field(description="수익률")
    asset_change_amount: float = Field(description="자산증감금액")
    asset_change_rate: float = Field(description="자산증감수익율")

    # 보유종목 정보 (JSON 형태로 저장)
    holdings: list[dict] | None = Field(
        default=None,
        description="보유종목 상세 정보",
        sa_column=Column(JSON)
    )

    class Config:
        table_name = "minutely_balances"

    __table_args__ = (
        Index('ix_minutely_balances_account_timestamp', 'account_id', 'timestamp'),
    )

