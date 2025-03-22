from typing import Optional, List
import uuid
from datetime import datetime, date, time
from pytz import timezone
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import TIMESTAMP, Column, Index, UniqueConstraint, text, JSON
from decimal import Decimal

class Kis_Balance_Base(SQLModel):
    """KIS 증권 계좌 잔고 정보 기본 모델"""
    account_id: uuid.UUID = Field(foreign_key="account.id", description="계좌 ID")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone('Asia/Seoul')), 
                                sa_column=Column(TIMESTAMP(timezone=True), 
                                                 server_default=text("CURRENT_TIMESTAMP")), 
                                                 description="잔고 조회 시간")
    total_balance: Decimal = Field(max_digits=20, decimal_places=2, description="총 잔고")
    total_profit: Decimal = Field(max_digits=20, decimal_places=2, description="총 수익")
    total_profit_rate: Decimal = Field(max_digits=10, decimal_places=2, description="총 수익률")
    total_buy_amount: Decimal = Field(max_digits=20, decimal_places=2, description="총 매수금액")
    total_sell_amount: Decimal = Field(max_digits=20, decimal_places=2, description="총 매도금액")
    total_buy_fee: Decimal = Field(max_digits=20, decimal_places=2, description="총 매수수수료")
    total_sell_fee: Decimal = Field(max_digits=20, decimal_places=2, description="총 매도수수료")
    total_buy_tax: Decimal = Field(max_digits=20, decimal_places=2, description="총 매수세금")
    total_sell_tax: Decimal = Field(max_digits=20, decimal_places=2, description="총 매도세금")
    holdings: Optional[List[dict]] = Field(default=None, description="보유종목 상세 정보 (JSON 형태)", sa_column=Column(JSON))

class Kis_Balance(Kis_Balance_Base, table=True):
    """KIS 증권 계좌 잔고 정보 테이블"""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="잔고 정보 ID")
    account: "Account" = Relationship(back_populates="kis_balances")

    class Config:
        table_name = "kis_balances"
        description = "KIS 증권 계좌 잔고 정보 테이블"

    __table_args__ = (
        Index('ix_kis_balances_account_timestamp', 'account_id', 'timestamp'),
    )

class Kis_Trade_Base(SQLModel):
    """KIS 증권 거래내역 기본 모델"""
    account_id: uuid.UUID = Field(foreign_key="account.id", description="계좌 ID")
    trade_date: date = Field(description="거래일자")
    trade_time: time = Field(description="거래시간")
    stock_code: str = Field(max_length=12, description="종목코드")
    stock_name: str = Field(max_length=100, description="종목명")
    trade_type: str = Field(max_length=20, description="거래유형 (매수/매도)")
    quantity: int = Field(description="거래수량")
    price: Decimal = Field(max_digits=13, decimal_places=2, description="거래단가")
    amount: Decimal = Field(max_digits=20, decimal_places=2, description="거래금액")
    fee: Decimal = Field(max_digits=20, decimal_places=2, description="수수료")
    tax: Decimal = Field(max_digits=20, decimal_places=2, description="세금")
    profit_amount: Optional[Decimal] = Field(max_digits=20, decimal_places=2, description="손익금액")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone('Asia/Seoul')), 
                                 sa_column=Column(TIMESTAMP(timezone=True), 
                                                  server_default=text("CURRENT_TIMESTAMP")), 
                                                  description="생성일시")

class Kis_Trade(Kis_Trade_Base, table=True):
    """KIS 증권 거래내역 테이블"""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="거래내역 ID")
    account: "Account" = Relationship(back_populates="kis_trades")

    class Config:
        table_name = "kis_trades"
        description = "KIS 증권 거래내역 테이블"

    __table_args__ = (
        Index('ix_kis_trades_account_date', 'account_id', 'trade_date'),
        Index('ix_kis_trades_stock', 'account_id', 'stock_code'),
    )

class Kis_Daily_Trade_Base(SQLModel):
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
    trade_time: Optional[str] = Field(default=None, max_length=6, description="체결시각")
    total_trade_qty: int = Field(default=0, description="총체결수량")
    remaining_qty: int = Field(default=0, description="주문잔량")
    cancel_qty: int = Field(default=0, description="취소수량")
    
    # output1의 추가 필드들
    original_order_no: Optional[str] = Field(default=None, max_length=10, description="원주문번호")
    order_type_name: Optional[str] = Field(default=None, max_length=20, description="주문구분명")
    order_type_detail_name: Optional[str] = Field(default=None, max_length=20, description="매매구분명")
    cancel_yn: Optional[str] = Field(default=None, max_length=1, description="취소여부")
    loan_date: Optional[str] = Field(default=None, max_length=8, description="대출일자")
    order_branch_no: Optional[str] = Field(default=None, max_length=5, description="주문점번호")
    order_media_code: Optional[str] = Field(default=None, max_length=2, description="주문매체구분코드")
    reject_qty: int = Field(default=0, description="거부수량")
    trade_condition_name: Optional[str] = Field(default=None, max_length=20, description="체결조건명")
    inqr_ip_addr: Optional[str] = Field(default=None, max_length=20, description="조회 IP주소")
    order_method_code: Optional[str] = Field(default=None, max_length=2, description="주문처리구분코드")
    order_info_code: Optional[str] = Field(default=None, max_length=2, description="주문정보분류코드")
    info_update_time: Optional[str] = Field(default=None, max_length=6, description="정보변경시각")
    phone_number: Optional[str] = Field(default=None, max_length=20, description="연락전화번호")
    product_type_code: Optional[str] = Field(default=None, max_length=3, description="상품유형코드")
    exchange_code: Optional[str] = Field(default=None, max_length=2, description="거래소코드")
    order_material_code: Optional[str] = Field(default=None, max_length=2, description="주문매체유형코드")
    order_org_no: Optional[str] = Field(default=None, max_length=5, description="주문조직번호")
    reserve_order_end_date: Optional[str] = Field(default=None, max_length=8, description="예약주문종료일자")
    exchange_id_code: Optional[str] = Field(default=None, max_length=3, description="거래소ID구분코드")
    stop_condition_price: float = Field(default=0, description="스탑조건가격")
    stop_effect_time: Optional[str] = Field(default=None, max_length=14, description="스탑발동시각")

    # output2 필드들 (일별 합산 정보)
    total_order_qty_sum: Optional[int] = Field(default=None, description="총주문수량")
    total_trade_qty_sum: Optional[int] = Field(default=None, description="총체결수량")
    total_trade_amt_sum: Optional[float] = Field(default=None, description="총체결금액")
    estimated_tax_amt: Optional[float] = Field(default=None, description="추정제비용합")
    avg_trade_price: Optional[float] = Field(default=None, description="매수평균가격")

class Kis_Daily_Trade(Kis_Daily_Trade_Base, table=True):
    """KIS 증권 일별 거래내역 테이블"""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    account_id: uuid.UUID = Field(foreign_key="account.id", nullable=False)
    account: Optional["Account"] = Relationship(back_populates="kis_daily_trades")
    
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
        table_name = "kis_daily_trades"
        description = "KIS 증권 일별 거래내역 테이블"

    __table_args__ = (
        UniqueConstraint('account_id', 'order_date', 'order_no', name='uix_kis_daily_trade_account_order'),
        Index('ix_daily_trades_account_date', 'account_id', 'order_date'),
        Index('ix_daily_trades_stock', 'account_id', 'stock_code'),
    )

class Kis_Minutely_Balance(SQLModel, table=True):
    """KIS 증권 분별 잔고 정보 테이블"""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    account_id: uuid.UUID = Field(foreign_key="account.id", nullable=False)
    account: Optional["Account"] = Relationship(back_populates="kis_minutely_balances")
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
    holdings: Optional[List[dict]] = Field(
        default=None,
        description="보유종목 상세 정보",
        sa_column=Column(JSON)
    )

    class Config:
        table_name = "kis_minutely_balances"
        description = "KIS 증권 분별 잔고 정보 테이블"

    __table_args__ = (
        Index('ix_kis_minutely_balances_account_timestamp', 'account_id', 'timestamp'),
    )

class Kis_Daily_Trade_Response(SQLModel):
    """KIS 증권 일별 거래내역 응답 모델"""
    message: str
    updated_count: int
    start_date: str
    end_date: str
    error_count: int
    errors: List[str]

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

class Kis_Balance_Response(SQLModel):
    """KIS 증권 잔고 조회 응답 모델"""
    rt_cd: Optional[str] = None
    msg1: Optional[str] = None
    msg_cd: Optional[str] = None
    output1: Optional[List[dict]] = Field(default=None, description="보유종목 상세내역")
    output2: Optional[List[dict]] = Field(default=None, description="계좌잔고 종합")

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