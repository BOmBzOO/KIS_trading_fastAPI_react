import uuid
from typing import Any, Dict, List
import requests
from datetime import datetime, timedelta
import asyncio
import os
import logging
from dotenv import load_dotenv

from fastapi import APIRouter, HTTPException, BackgroundTasks
from sqlmodel import func, select, Session
from sqlalchemy.orm import joinedload
from pydantic import BaseModel

from app.api.deps import CurrentUser, SessionDep
from app.models import Account, AccountCreate, AccountPublic, AccountsPublic, AccountUpdate, Message, DailyTrade, DailyTradeBase, MinutelyBalance
from app.core.config import settings
from app.core.db import engine, get_session

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('background_tasks.log')
    ]
)
logger = logging.getLogger(__name__)

# .env 파일 로드
load_dotenv()

# 백그라운드 작업 설정
TOKEN_CHECK_INTERVAL = 60  # 60초(1분) 간격으로 토큰 체크
BALANCE_CHECK_INTERVAL = 60  # 60초(1분) 간격으로 잔고 조회
MAX_RETRIES = 3  # 최대 재시도 횟수

router = APIRouter(prefix="/accounts", tags=["accounts"])

# 전역 변수로 백그라운드 태스크 실행 여부를 추적
background_task_running = False

def should_refresh_token(expires_at: datetime) -> bool:
    """토큰 만료 10분 전인지 확인"""
    if not expires_at:
        return True
    return datetime.now() + timedelta(minutes=10) >= expires_at

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
            logger.info(f"Token refreshed for account {account.id}")
        except Exception as e:
            logger.error(f"Error refreshing token for account {account.id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"토큰 갱신 실패: {str(e)}"
            )

async def periodic_token_check():
    """주기적으로 모든 활성화된 계정의 토큰을 검증하고 갱신"""
    global background_task_running
    while background_task_running:
        try:
            session = next(get_session())
            statement = select(Account).where(Account.is_active == True)
            accounts = session.exec(statement).all()
            
            refresh_count = 0
            for account in accounts:
                try:
                    if should_refresh_token(account.access_token_expired):
                        access_token, expires_at = get_kis_access_token(
                            app_key=account.app_key,
                            app_secret=account.app_secret,
                            acnt_type=account.acnt_type
                        )
                        account.kis_access_token = access_token
                        account.access_token_expired = expires_at
                        refresh_count += 1
                except Exception as e:
                    logger.error(f"Token refresh failed for {account.acnt_name}")
            
            if refresh_count > 0:
                logger.info(f"Refreshed {refresh_count} tokens")
            session.commit()
        except Exception as e:
            logger.error(f"Token check error: {str(e)}")
        
        await asyncio.sleep(TOKEN_CHECK_INTERVAL)

async def periodic_balance_check():
    """주기적으로 모든 활성화된 계정의 잔고를 조회하고 저장"""
    global background_task_running
    retry_counts = {}  # 계정별 재시도 횟수 추적
    
    while background_task_running:
        try:
            current_time = datetime.now()
            # # 장 운영 시간(9:00 ~ 15:30)에만 실행
            # if current_time.hour < 9 or (current_time.hour == 15 and current_time.minute >= 30) or current_time.hour > 15:
            #     logger.info(f"Outside trading hours ({current_time.strftime('%H:%M')}), skipping balance check")
            #     await asyncio.sleep(BALANCE_CHECK_INTERVAL)
            #     continue
            
            logger.info(f"Starting periodic balance check at {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
            session = next(get_session())
            statement = select(Account).where(Account.is_active == True)
            accounts = session.exec(statement).all()
            
            success_count = 0
            error_count = 0
            
            # 각 계정의 잔고를 조회하고 저장
            for account in accounts:
                try:
                    # 잔고 조회
                    balance_data = await fetch_account_balance(account)
                    
                    if balance_data.get("rt_cd") == "0":
                        output1 = balance_data.get("output1", [])
                        output2 = balance_data.get("output2", [{}])[0]
                        
                        # 수익률 계산
                        purchase_amount = float(output2.get("pchs_amt_smtl_amt", 0))
                        eval_profit_loss = float(output2.get("evlu_pfls_smtl_amt", 0))
                        profit_loss_rate = (eval_profit_loss / purchase_amount * 100) if purchase_amount > 0 else 0
                        
                        # MinutelyBalance 객체 생성
                        minutely_balance = MinutelyBalance(
                            account_id=account.id,
                            total_balance=float(output2.get("dnca_tot_amt", 0)),
                            available_balance=float(output2.get("prvs_rcdl_excc_amt", 0)),
                            total_assets=float(output2.get("tot_evlu_amt", 0)),
                            purchase_amount=purchase_amount,
                            eval_amount=float(output2.get("evlu_amt_smtl_amt", 0)),
                            profit_loss=eval_profit_loss,
                            profit_loss_rate=profit_loss_rate,
                            asset_change_amount=float(output2.get("asst_icdc_amt", 0)),
                            asset_change_rate=float(output2.get("asst_icdc_rt", 0)),
                            holdings=[{
                                "stock_code": item.get("pdno"),
                                "stock_name": item.get("prdt_name"),
                                "quantity": int(item.get("hldg_qty", 0)),
                                "purchase_price": float(item.get("pchs_avg_pric", 0)),
                                "current_price": float(item.get("prpr", 0)),
                                "eval_amount": float(item.get("evlu_amt", 0)),
                                "profit_loss": float(item.get("evlu_pfls_amt", 0)),
                                "profit_loss_rate": float(item.get("evlu_pfls_rt", 0))
                            } for item in output1] if output1 else None
                        )
                        
                        session.add(minutely_balance)
                        logger.info(f"Account {account.acnt_name}: Assets {minutely_balance.total_assets:,.0f}원 ({minutely_balance.profit_loss_rate:+.1f}%)")
                        success_count += 1
                        retry_counts[account.id] = 0  # 성공 시 재시도 횟수 초기화
                        
                except Exception as e:
                    error_count += 1
                    retry_counts[account.id] = retry_counts.get(account.id, 0) + 1
                    
                    if retry_counts[account.id] <= MAX_RETRIES:
                        logger.error(f"Balance check failed for {account.acnt_name} (Try {retry_counts[account.id]}/{MAX_RETRIES})")
                        if retry_counts[account.id] < MAX_RETRIES:
                            await asyncio.sleep(5)  # 5초 대기 후 다음 시도
                            continue
                    else:
                        logger.error(f"Max retries reached for {account.acnt_name}")
                    continue
            
            try:
                session.commit()
                if success_count > 0 or error_count > 0:
                    logger.info(f"Balance check completed: {success_count} success, {error_count} errors")
            except Exception as e:
                logger.error("Failed to save balance data")
                session.rollback()
            
        except Exception as e:
            logger.error(f"Balance check error: {str(e)}")
        
        await asyncio.sleep(BALANCE_CHECK_INTERVAL)

@router.on_event("startup")
async def start_background_tasks():
    """애플리케이션 시작 시 백그라운드 태스크 시작"""
    global background_task_running
    background_task_running = True
    logger.info("Starting background tasks...")
    asyncio.create_task(periodic_token_check())
    asyncio.create_task(periodic_balance_check())
    logger.info("Background tasks started successfully")

@router.on_event("shutdown")
async def stop_background_tasks():
    """애플리케이션 종료 시 백그라운드 태스크 중지"""
    global background_task_running
    background_task_running = False
    logger.info("Background tasks stopped")

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
        
        # Parse expires_in to calculate expiration datetime
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
        statement = (
            select(Account)
            .options(joinedload(Account.owner))  # User 정보를 함께 로드
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
            .options(joinedload(Account.owner))  # User 정보를 함께 로드
            .where(Account.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        accounts = session.exec(statement).all()

    # 각 계정의 토큰 상태를 확인하고 필요한 경우 갱신
    for account in accounts:
        if account.is_active:  # 활성화된 계정만 토큰 갱신
            refresh_token_if_needed(account)
    
    session.commit()
    return AccountsPublic(data=accounts, count=count)

@router.get("/{account_id}", response_model=AccountPublic)
def read_account(session: SessionDep, current_user: CurrentUser, account_id: uuid.UUID) -> Any:
    """
    Get account by ID.
    """
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (account.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # 토큰 상태 확인 및 갱신
    if account.is_active:
        refresh_token_if_needed(account)
        session.commit()
    
    return account

@router.post("/", response_model=AccountPublic)
def create_account(
    *, session: SessionDep, current_user: CurrentUser, account_in: AccountCreate
) -> Any:
    """
    Create new account and get KIS API access token.
    """
    # KIS API에서 access token 받아오기
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
    """
    Update an account.
    """
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Item not found")
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
        # 자격 증명이 업데이트되지 않았지만 토큰이 만료되어가는 경우 갱신
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
    """
    Delete an account.
    """
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (account.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    session.delete(account)
    session.commit()
    return Message(message="Account deleted successfully")

class BalanceOutput1(BaseModel):
    """잔고 조회 출력 데이터 모델 - 보유종목 정보"""
    pdno: str | None = None  # 상품번호
    prdt_name: str | None = None  # 상품명
    trad_dvsn_name: str | None = None  # 매매구분명
    bfdy_buy_qty: int | None = None  # 전일매수수량
    bfdy_sll_qty: int | None = None  # 전일매도수량
    thdt_buyqty: int | None = None  # 금일매수수량
    thdt_sll_qty: int | None = None  # 금일매도수량
    hldg_qty: int | None = None  # 보유수량
    ord_psbl_qty: int | None = None  # 주문가능수량
    pchs_avg_pric: float | None = None  # 매입평균가격
    pchs_amt: int | None = None  # 매입금액
    prpr: int | None = None  # 현재가
    evlu_amt: int | None = None  # 평가금액
    evlu_pfls_amt: int | None = None  # 평가손익금액
    evlu_pfls_rt: float | None = None  # 평가손익율
    evlu_erng_rt: float | None = None  # 평가수익율
    loan_dt: str | None = None  # 대출일자
    loan_amt: int | None = None  # 대출금액
    stln_slng_chgs: int | None = None  # 대주매각대금
    expd_dt: str | None = None  # 만기일자
    fltt_rt: float | None = None  # 등락율
    bfdy_cprs_icdc: float | None = None  # 전일대비증감
    item_mgna_rt_name: str | None = None  # 종목증거금율명
    grta_rt_name: str | None = None  # 보증금율명
    sbst_pric: int | None = None  # 대용가격
    stck_loan_unpr: float | None = None  # 주식대출단가

class BalanceOutput2(BaseModel):
    """잔고 조회 출력 데이터 모델 - 계좌 요약 정보"""
    dnca_tot_amt: int | None = None  # 예수금총금액
    nxdy_excc_amt: int | None = None  # 익일정산금액
    prvs_rcdl_excc_amt: int | None = None  # 가수도정산금액
    cma_evlu_amt: int | None = None  # CMA평가금액
    bfdy_buy_amt: int | None = None  # 전일매수금액
    thdt_buy_amt: int | None = None  # 금일매수금액
    nxdy_auto_rdpt_amt: int | None = None  # 익일자동상환금액
    bfdy_sll_amt: int | None = None  # 전일매도금액
    thdt_sll_amt: int | None = None  # 금일매도금액
    d2_auto_rdpt_amt: int | None = None  # D+2자동상환금액
    bfdy_tlex_amt: int | None = None  # 전일거래세금액
    thdt_tlex_amt: int | None = None  # 금일거래세금액
    tot_loan_amt: int | None = None  # 대출총금액
    scts_evlu_amt: int | None = None  # 유가평가금액
    tot_evlu_amt: int | None = None  # 총평가금액
    nass_amt: int | None = None  # 순자산금액
    fncg_gld_auto_rdpt_yn: str | None = None  # 융자금자동상환여부
    pchs_amt_smtl_amt: int | None = None  # 매입금액합계금액
    evlu_amt_smtl_amt: int | None = None  # 평가금액합계금액
    evlu_pfls_smtl_amt: int | None = None  # 평가손익합계금액
    tot_stln_slng_chgs: int | None = None  # 총대주매각대금
    bfdy_tot_asst_evlu_amt: int | None = None  # 전일총자산평가금액
    asst_icdc_amt: int | None = None  # 자산증감금액
    asst_icdc_erng_rt: float | None = None  # 자산증감수익율

class BalanceResponse(BaseModel):
    """잔고 조회 응답 모델"""
    output1: list[BalanceOutput1]
    output2: list[BalanceOutput2]
    rt_cd: str
    msg_cd: str
    msg1: str
    ctx_area_fk100: str | None = None
    ctx_area_nk100: str | None = None

@router.get("/{account_id}/balance", response_model=BalanceResponse)
def get_account_balance(
    session: SessionDep,
    current_user: CurrentUser,
    account_id: uuid.UUID
) -> Any:
    """
    Get account balance from KIS API.
    """
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if not current_user.is_superuser and (account.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # 토큰 상태 확인 및 갱신
    if account.is_active:
        refresh_token_if_needed(account)
        session.commit()
    
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
                "tr_cont": "",
                "content-type": "application/json"
            }
        )
        # print(response.json())
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"KIS API 잔고 조회 실패: {str(e)}"
        )

@router.post("/{account_id}/token_refresh", response_model=AccountPublic)
def refresh_account_token(
    session: SessionDep,
    current_user: CurrentUser,
    account_id: uuid.UUID
) -> Any:
    """
    Manually refresh KIS API access token for a specific account.
    """
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

class DailyTradeResponse(BaseModel):
    """일별 주문체결 조회 응답 모델"""
    message: str
    updated_count: int
    start_date: str
    end_date: str
    error_count: int = 0
    errors: List[str] = []

def process_trade_data(response_data: dict) -> list[DailyTrade]:
    trades = []
    output1 = response_data.get("output1", [])
    output2 = response_data.get("output2", {})

    # output2의 합산 정보를 저장
    summary_data = {
        "total_order_qty_sum": int(output2.get("tot_ord_qty", 0)),
        "total_trade_qty_sum": int(output2.get("tot_ccld_qty", 0)),
        "total_trade_amt_sum": float(output2.get("tot_ccld_amt", 0)),
        "estimated_tax_amt": float(output2.get("prsm_tlex_smtl", 0)),
        "avg_trade_price": float(output2.get("pchs_avg_pric", 0))
    }

    # output1의 개별 거래 데이터 처리
    for trade in output1:
        daily_trade = DailyTrade(
            order_date=trade["ord_dt"],
            stock_code=trade["pdno"],
            stock_name=trade["prdt_name"],
            order_no=trade["odno"],
            order_time=trade["ord_tmd"],
            order_type=trade["sll_buy_dvsn_cd"],
            order_price=float(trade["ord_unpr"]),
            order_qty=int(trade["ord_qty"]),
            trade_price=float(trade.get("avg_prvs", 0)),
            trade_qty=int(trade.get("tot_ccld_qty", 0)),
            trade_amount=float(trade.get("tot_ccld_amt", 0)),
            total_trade_qty=int(trade.get("tot_ccld_qty", 0)),
            remaining_qty=int(trade.get("rmn_qty", 0)),
            cancel_qty=int(trade.get("cncl_cfrm_qty", 0)),
            
            # output1의 추가 필드들
            original_order_no=trade.get("orgn_odno"),
            order_type_name=trade.get("ord_dvsn_name"),
            order_type_detail_name=trade.get("sll_buy_dvsn_cd_name"),
            cancel_yn=trade.get("cncl_yn"),
            loan_date=trade.get("loan_dt"),
            order_branch_no=trade.get("ord_gno_brno"),
            order_media_code=trade.get("ord_dvsn_cd"),
            reject_qty=int(trade.get("rjct_qty", 0)),
            trade_condition_name=trade.get("ccld_cndt_name"),
            inqr_ip_addr=trade.get("inqr_ip_addr"),
            order_method_code=trade.get("cpbc_ordp_ord_rcit_dvsn_cd"),
            order_info_code=trade.get("cpbc_ordp_infm_mthd_dvsn_cd"),
            info_update_time=trade.get("infm_tmd"),
            phone_number=trade.get("ctac_tlno"),
            product_type_code=trade.get("prdt_type_cd"),
            exchange_code=trade.get("excg_dvsn_cd"),
            order_material_code=trade.get("cpbc_ordp_mtrl_dvsn_cd"),
            order_org_no=trade.get("ord_orgno"),
            reserve_order_end_date=trade.get("rsvn_ord_end_dt"),
            exchange_id_code=trade.get("excg_id_dvsn_cd"),
            stop_condition_price=float(trade.get("stpm_cndt_pric", 0)),
            stop_effect_time=trade.get("stpm_efct_occr_dtmd"),

            # output2의 합산 정보 추가
            **summary_data
        )
        trades.append(daily_trade)

    return trades

@router.post("/{account_id}/update-daily-trades", response_model=DailyTradeResponse)
async def update_daily_trades(
    account_id: uuid.UUID,
    start_date: str | None = None,  # YYYY-MM-DD
    end_date: str | None = None,    # YYYY-MM-DD
    background_tasks: BackgroundTasks = None,
    session: SessionDep = None,
    current_user: CurrentUser = None,
) -> Any:
    """특정 계좌의 일별 주문체결 내역을 조회하여 DB에 업데이트"""
    errors = []
    updated_count = 0

    try:
        # 1. 날짜 범위 설정
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        print(f"조회 기간: {start_date} ~ {end_date}")  # 디버깅용

        # 2. 계좌 정보 조회 및 권한 확인
        account = session.get(Account, account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        if not current_user.is_superuser and (account.owner_id != current_user.id):
            raise HTTPException(status_code=400, detail="Not enough permissions")

        # 3. 토큰 상태 확인 및 갱신
        if account.is_active:
            refresh_token_if_needed(account)
            session.commit()

        # 4. KIS API 호출
        trade_data = await fetch_daily_trades(account, start_date, end_date)
        print(f"API 응답 전체: {trade_data}")  # 디버깅용
        
        if not trade_data.get("output1"):
            print(f"API 응답에 거래 내역이 없음: {trade_data}")  # 디버깅용
            return DailyTradeResponse(
                message="조회된 거래 내역이 없습니다.",
                updated_count=0,
                start_date=start_date,
                end_date=end_date,
                error_count=0,
                errors=[]
            )

        # 5. DB 업데이트
        from sqlmodel import select
        
        try:
            for trade in process_trade_data(trade_data):
                try:
                    # 거래 데이터 변환
                    trade_dict = trade.model_dump()
                    trade_dict["account_id"] = account_id

                    print(f"처리할 거래 데이터: {trade_dict}")  # 디버깅용

                    # 기존 거래 확인
                    statement = select(DailyTrade).where(
                        DailyTrade.account_id == account_id,
                        DailyTrade.order_date == trade_dict["order_date"],
                        DailyTrade.order_no == trade_dict["order_no"]
                    )
                    existing_trade = session.exec(statement).first()

                    if existing_trade:
                        # 기존 거래 업데이트
                        for key, value in trade_dict.items():
                            setattr(existing_trade, key, value)
                        print(f"기존 거래 업데이트: {trade_dict['order_no']}")  # 디버깅용
                    else:
                        # 새 거래 추가
                        new_trade = DailyTrade(**trade_dict)
                        session.add(new_trade)
                        print(f"새 거래 추가: {trade_dict['order_no']}")  # 디버깅용

                    updated_count += 1

                except Exception as e:
                    error_msg = f"거래 데이터 처리 실패 (주문번호: {trade.get('ordno')}): {str(e)}"
                    print(f"에러: {error_msg}")  # 디버깅용
                    errors.append(error_msg)
                    continue

            # 모든 거래 처리가 완료되면 커밋
            session.commit()
            print(f"전체 거래 저장 성공: {updated_count}건")  # 디버깅용

        except Exception as e:
            # 오류 발생 시 롤백
            session.rollback()
            error_msg = f"데이터베이스 저장 실패: {str(e)}"
            print(f"에러: {error_msg}")  # 디버깅용
            raise HTTPException(status_code=500, detail=error_msg)

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
        error_msg = f"데이터 업데이트 실패: {str(e)}"
        print(f"예외 발생: {error_msg}")  # 디버깅용
        raise HTTPException(
            status_code=500,
            detail=error_msg
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
    """특정 계좌의 일별 주문체결 내역을 조회"""
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

async def fetch_daily_trades(
    account: Account,
    start_date: str,
    end_date: str
) -> dict:
    """KIS API를 통해 일별 주문체결 내역을 조회"""
    base_url = "https://openapi.koreainvestment.com:9443" if account.acnt_type == "live" else "https://openapivts.koreainvestment.com:29443"
    
    params = {
        "CANO": account.cano,  # 종합계좌번호
        "ACNT_PRDT_CD": account.acnt_prdt_cd,  # 계좌상품코드
        "INQR_STRT_DT": start_date.replace("-", ""),  # 조회시작일자
        "INQR_END_DT": end_date.replace("-", ""),  # 조회종료일자
        "SLL_BUY_DVSN_CD": "00",  # 매도매수구분코드 - 00:전체, 01:매도, 02:매수
        "INQR_DVSN": "00",  # 조회구분 - 00:전체, 01:체결, 02:미체결
        "PDNO": "",  # 상품번호(종목코드), 공백:전체
        "CCLD_DVSN": "00",  # 체결구분 - 00:전체, 01:체결, 02:미체결
        "ORD_GNO_BRNO": "",  # 주문채번지점번호
        "ODNO": "",  # 주문번호
        "INQR_DVSN_3": "00",  # 조회구분3 - 00:전체, 01:현금, 02:신용, 03:선물대용
        "INQR_DVSN_1": "",  # 조회구분1
        "INQR_DVSN_2": "",  # 조회구분2
        "CTX_AREA_FK100": "",  # 연속조회검색조건100
        "CTX_AREA_NK100": ""   # 연속조회키100
    }
    
    headers = {
        "authorization": f"Bearer {account.kis_access_token}",
        "appkey": account.app_key,
        "appsecret": account.app_secret,
        "tr_id": "TTTC8001R" if account.acnt_type == "live" else "VTTC8001R",
        "content-type": "application/json"
    }
    
    try:
        print(f"API Request - URL: {base_url}/uapi/domestic-stock/v1/trading/inquire-daily-ccld")  # 디버깅용
        print(f"API Request - Params: {params}")  # 디버깅용
        print(f"API Request - Headers: {headers}")  # 디버깅용
        
        response = requests.get(
            f"{base_url}/uapi/domestic-stock/v1/trading/inquire-daily-ccld",
            params=params,
            headers=headers
        )
        response.raise_for_status()
        data = response.json()
        
        print(f"API Response - Status Code: {response.status_code}")  # 디버깅용
        print(f"API Response - Headers: {response.headers}")  # 디버깅용
        print(f"API Response - Data: {data}")  # 디버깅용
        
        # API 응답 검증
        if data.get("rt_cd") != "0":
            raise HTTPException(
                status_code=400,
                detail=f"KIS API 오류: {data.get('msg1', '알 수 없는 오류')}"
            )
            
        return data
        
    except requests.RequestException as e:
        print(f"API Request Error: {str(e)}")  # 디버깅용
        raise HTTPException(
            status_code=500,
            detail=f"KIS API 호출 실패: {str(e)}"
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

@router.get("/{account_id}/minutely-balances", response_model=List[MinutelyBalance])
async def get_minutely_balances(
    account_id: uuid.UUID,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    session: SessionDep = None,
    current_user: CurrentUser = None,
) -> Any:
    """특정 계좌의 분당 잔고 데이터를 조회"""
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
