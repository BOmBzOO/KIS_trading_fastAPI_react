import uuid
from datetime import datetime

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import TIMESTAMP, Column, Index, UniqueConstraint, text


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

# Properties to receive on account creation
class AccountCreate(AccountBase):
    pass

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
    access_token_expired: datetime | None = None

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
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP(timezone=False), server_default=text("CURRENT_TIMESTAMP"))
    )
    updated_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP(timezone=False),
            server_default=text("CURRENT_TIMESTAMP"),
            onupdate=datetime.utcnow
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
    access_token_expired: datetime | None = Field(default=None, sa_column=Column(TIMESTAMP(timezone=False)))
    daily_trades: list["DailyTrade"] = Relationship(back_populates="account", cascade_delete=True)

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

class AccountsPublic(SQLModel):
    data: list[AccountPublic]
    count: int
#######################################################################

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
