import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from pytz import timezone
from zoneinfo import ZoneInfo
from fastapi import HTTPException

from sqlmodel import select, Session

from app.constants import (
    TOKEN_REFRESH_THRESHOLD_MINUTES,
    TOKEN_CHECK_INTERVAL_SECONDS,
    BALANCE_CHECK_INTERVAL_SECONDS,
    LOG_FORMAT,
    LOG_DATE_FORMAT,
    TOKEN_CHECK_INTERVAL,
    BALANCE_CHECK_INTERVAL,
    KST,
    UTC,
    MARKET_START_TIME,
    MARKET_END_TIME
)
from app.core.db import engine
from app.models.account import Account
from app.models.kis import Kis_Minutely_Balance
from app.models.ls import Ls_Minutely_Balance, Ls_Trade
from app.api.services.kis_api import get_access_token_KIS, inquire_balance_from_KIS, inquire_daily_ccld_from_KIS
from app.api.services.ls_api import get_access_token_LS, inquire_balance_from_LS, inquire_daily_ccld_from_LS
from app.api.services.kis_trade_service import process_trade_data_KIS, update_account_daily_trades_KIS
from app.api.services.ls_trade_service import process_trade_data_LS, update_account_daily_trades_LS

# 로깅 설정
logging.basicConfig(
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT,
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 백그라운드 태스크 상태 관리
background_tasks = set()
last_balance_check = {}  # 계정별 마지막 잔고 체크 시간 저장
last_token_check = {}    # 계정별 마지막 토큰 체크 시간 저장
last_token_task_time = datetime.now(KST)  # 마지막 토큰 체크 작업 시간
last_balance_task_time = datetime.now(KST)  # 마지막 잔고 체크 작업 시간

def should_refresh_token(expires_at: Optional[datetime]) -> bool:
    """토큰 갱신이 필요한지 확인"""
    if not expires_at:
        return True
    
    threshold = timedelta(minutes=TOKEN_REFRESH_THRESHOLD_MINUTES)
    now = datetime.now(KST)
    return now + threshold >= expires_at

def should_check_token(account_id: str) -> bool:
    """토큰 체크가 필요한지 확인"""
    now = datetime.now(KST)
    last_check = last_token_check.get(account_id)
    
    if not last_check:
        return True
    
    # 마지막 체크로부터 60초 이상 지났는지 확인
    return (now - last_check).total_seconds() >= TOKEN_CHECK_INTERVAL_SECONDS

def should_check_balance(account_id: str) -> bool:
    """잔고 체크가 필요한지 확인"""
    now = datetime.now(KST)
    last_check = last_balance_check.get(account_id)
    
    if not last_check:
        return True
    
    # 마지막 체크로부터 60초 이상 지났는지 확인
    return (now - last_check).total_seconds() >= BALANCE_CHECK_INTERVAL_SECONDS

async def check_and_refresh_tokens():
    """모든 활성 계정의 토큰을 주기적으로 체크하고 갱신"""
    global last_token_task_time
    
    while True:
        try:
            current_time = datetime.now(KST)
            time_diff = (current_time - last_token_task_time).total_seconds()
            
            if time_diff < TOKEN_CHECK_INTERVAL:
                await asyncio.sleep(1)
                continue

            with Session(engine) as session:
                # 활성 계정 조회
                statement = select(Account).where(Account.is_active == True)
                accounts = session.exec(statement).all()
                
                refresh_count = 0
                check_count = 0
                failed_accounts = []
                
                for account in accounts:
                    if not should_check_token(account.id):
                        continue
                        
                    try:
                        if should_refresh_token(account.access_token_expired):
                            if account.broker.upper() == "KIS":
                                access_token, expires_at = get_access_token_KIS(
                                    app_key=account.app_key,
                                    app_secret=account.app_secret,
                                    acnt_type=account.acnt_type
                                )
                            elif account.broker.upper() == "LS":
                                access_token, expires_at = get_access_token_LS(
                                    app_key=account.app_key,
                                    app_secret=account.app_secret,
                                    acnt_type=account.acnt_type
                                )
                            else:
                                logger.warning(f"지원하지 않는 브로커: {account.broker}")
                                continue
                                
                            account.access_token = access_token
                            account.access_token_expired = expires_at
                            session.add(account)
                            refresh_count += 1
                        
                        last_token_check[account.id] = current_time
                        check_count += 1
                        
                    except Exception as e:
                        failed_accounts.append((account.acnt_name, str(e)))
                        continue
                
                if refresh_count > 0:
                    session.commit()
                    logger.info(f"토큰 갱신 완료 - 총 {refresh_count}개 계좌")
                
                if check_count > 0:
                    logger.info(f"토큰 체크 완료 - 총 {check_count}개 계좌")
                
                # 실패한 계좌만 로깅
                if failed_accounts:
                    for acnt_name, error in failed_accounts:
                        logger.error(f"토큰 갱신 실패 - 계정: {acnt_name}, 에러: {error}")
                
                last_token_task_time = current_time
                
        except Exception as e:
            logger.error(f"토큰 체크 중 오류 발생: {str(e)}")
        
        await asyncio.sleep(1)

async def check_and_save_balances():
    """모든 활성 계정의 잔고를 주기적으로 체크하고 저장"""
    global last_balance_task_time
    
    while True:
        try:
            current_time = datetime.now(KST)
            time_diff = (current_time - last_balance_task_time).total_seconds()
            
            if time_diff < BALANCE_CHECK_INTERVAL:
                await asyncio.sleep(1)
                continue

            with Session(engine) as session:
                # 활성 계정 조회
                statement = select(Account).where(Account.is_active == True)
                accounts = session.exec(statement).all()
                
                success_count = 0
                failed_accounts = []
                
                for account in accounts:
                    if not should_check_balance(account.id):
                        continue
                        
                    try:
                        # 토큰 갱신이 필요한 경우 갱신
                        if should_refresh_token(account.access_token_expired):
                            if account.broker.upper() == "KIS":
                                access_token, expires_at = get_access_token_KIS(
                                    app_key=account.app_key,
                                    app_secret=account.app_secret,
                                    acnt_type=account.acnt_type
                                )
                            elif account.broker.upper() == "LS":
                                access_token, expires_at = get_access_token_LS(
                                    app_key=account.app_key,
                                    app_secret=account.app_secret,
                                    acnt_type=account.acnt_type
                                )
                            account.access_token = access_token
                            account.access_token_expired = expires_at
                            session.add(account)
                            session.commit()
                        
                        # 잔고 조회 및 저장
                        if account.broker.upper() == "KIS":
                            balance_data = await inquire_balance_from_KIS(account)
                            await process_and_save_kis_balance(account, balance_data, session)
                        elif account.broker.upper() == "LS":
                            balance_data = await inquire_balance_from_LS(account)
                            await process_and_save_ls_balance(account, balance_data, session)
                        
                        success_count += 1
                        last_balance_check[account.id] = current_time
                            
                    except Exception as e:
                        failed_accounts.append((account.acnt_name, str(e)))
                        continue
                
                if success_count > 0:
                    logger.info(f"잔고 저장 완료 - 총 {success_count}개 계좌")
                
                # 실패한 계좌만 로깅
                if failed_accounts:
                    for acnt_name, error in failed_accounts:
                        logger.error(f"잔고 체크 실패 - 계정: {acnt_name}, 에러: {error}")
                
                last_balance_task_time = current_time
                
        except Exception as e:
            logger.error(f"잔고 체크 중 오류 발생: {str(e)}")
        
        await asyncio.sleep(1)

async def update_daily_trades():
    """한국 시간 오전 3시에 모든 계정의 일별 거래 내역을 업데이트"""
    while True:
        try:
            now = datetime.now(KST)
            
            # 다음 실행 시간 계산 (다음 날 오전 3시)
            next_run = now.replace(hour=3, minute=0, second=0, microsecond=0)
            if now.hour >= 3:
                next_run += timedelta(days=1)
            
            # 다음 실행까지 대기
            wait_seconds = (next_run - now).total_seconds()
            await asyncio.sleep(wait_seconds)
            
            # 활성 계정 조회
            with Session(engine) as session:
                statement = select(Account).where(Account.is_active == True)
                accounts = session.exec(statement).all()
                
                total_success_count = 0
                all_failed_accounts = []
                
                for account in accounts:
                    try:
                        # 7일치 데이터 업데이트
                        end_date = datetime.now(KST).strftime("%Y-%m-%d")
                        start_date = (datetime.now(KST) - timedelta(days=7)).strftime("%Y-%m-%d")
                        
                        if account.broker.upper() == "KIS":
                            success_count, failed_accounts = await update_account_daily_trades_KIS(
                                account_id=account.id,
                                start_date=start_date,
                                end_date=end_date,
                                session=session
                            )
                        elif account.broker.upper() == "LS":
                            success_count, failed_accounts = await update_account_daily_trades_LS(
                                account_id=account.id,
                                start_date=start_date,
                                end_date=end_date,
                                session=session
                            )
                        
                        total_success_count += success_count
                        all_failed_accounts.extend(failed_accounts)
                        
                    except Exception as e:
                        all_failed_accounts.append((account.acnt_name, str(e)))
                        continue
                
                if total_success_count > 0:
                    logger.info(f"일별 거래 내역 업데이트 완료 - 총 {total_success_count}개 거래")
                
                if all_failed_accounts:
                    for acnt_name, error in all_failed_accounts:
                        logger.error(f"일별 거래 내역 업데이트 실패 - 계정: {acnt_name}, 에러: {error}")
                
        except Exception as e:
            logger.error(f"일별 거래 내역 업데이트 중 오류 발생: {str(e)}")
        
        await asyncio.sleep(60)  # 1분 대기 후 다음 체크

async def check_and_save_minutely_data():
    """모든 활성 계정의 분별 데이터를 수집하고 저장"""
    while True:
        try:
            current_time = datetime.now(KST)
            
            # 장 시간 중에만 실행
            if (current_time.time() >= MARKET_START_TIME and 
                current_time.time() <= MARKET_END_TIME and
                current_time.weekday() < 5):  # 평일만
                
                with Session(engine) as session:
                    statement = select(Account).where(Account.is_active == True)
                    accounts = session.exec(statement).all()
                    
                    for account in accounts:
                        try:
                            if account.broker.upper() == "KIS":
                                balance_data = await inquire_balance_from_KIS(account)
                                await process_and_save_kis_balance(account, balance_data, session)
                            elif account.broker.upper() == "LS":
                                balance_data = await inquire_balance_from_LS(account)
                                await process_and_save_ls_balance(account, balance_data, session)
                            
                            session.commit()
                            
                        except Exception as e:
                            logger.error(f"분별 데이터 수집 실패 - 계정: {account.acnt_name}, 에러: {str(e)}")
                            continue
            
            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error(f"분별 데이터 수집 중 오류 발생: {str(e)}")
            await asyncio.sleep(60)

def start_background_tasks():
    """백그라운드 태스크 시작"""
    logger.info("백그라운드 작업 시작")
    loop = asyncio.get_event_loop()
    
    # 토큰 체크 태스크 시작
    token_task = loop.create_task(check_and_refresh_tokens())
    background_tasks.add(token_task)
    token_task.add_done_callback(background_tasks.discard)
    
    # 잔고 체크 태스크 시작
    balance_task = loop.create_task(check_and_save_balances())
    background_tasks.add(balance_task)
    balance_task.add_done_callback(background_tasks.discard)
    
    # 일별 거래 내역 업데이트 태스크 시작
    daily_trades_task = loop.create_task(update_daily_trades())
    background_tasks.add(daily_trades_task)
    daily_trades_task.add_done_callback(background_tasks.discard)
    
    # 분별 데이터 수집 태스크 추가
    minutely_task = loop.create_task(check_and_save_minutely_data())
    background_tasks.add(minutely_task)
    minutely_task.add_done_callback(background_tasks.discard)

def stop_background_tasks():
    """백그라운드 태스크 중지"""
    logger.info("백그라운드 작업 중지")
    for task in background_tasks:
        task.cancel()

def refresh_token_if_needed(account: Account) -> None:
    """계정의 토큰이 만료되어가는 경우 갱신"""
    if should_refresh_token(account.access_token_expired):  # access_token_expired 사용
        try:
            access_token, expires_at = get_access_token_KIS(
                app_key=account.app_key,
                app_secret=account.app_secret,
                acnt_type=account.acnt_type
            )
            
            # timezone 처리
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=ZoneInfo("Asia/Seoul"))
            
            account.access_token = access_token  # kis_access_token -> access_token
            account.access_token_expired = expires_at
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"토큰 갱신 실패: {str(e)}"
            ) 

async def check_balance(account: Account, session: Session) -> None:
    """계좌 잔고 확인 및 저장"""
    try:
        # 토큰 갱신이 필요한지 확인
        if should_refresh_token(account.access_token_expired):  # kis_access_token_expired -> access_token_expired
            access_token, expires_at = get_access_token_KIS(
                app_key=account.app_key,
                app_secret=account.app_secret,
                acnt_type=account.acnt_type
            )
            account.access_token = access_token  # kis_access_token -> access_token
            account.access_token_expired = expires_at
            session.add(account)
            session.commit()

        # 잔고 조회
        balance_response = await inquire_balance_from_KIS(account)
        
        # ... 나머지 코드 ...

    except Exception as e:
        logger.error(f"잔고 체크 실패 - 계정: {account.acnt_name}, 에러: {str(e)}")

async def check_daily_trades(account: Account, session: Session) -> None:
    """일별 거래 내역 확인 및 저장"""
    try:
        # 토큰 갱신이 필요한지 확인
        if should_refresh_token(account.access_token_expired):  # kis_access_token_expired -> access_token_expired
            access_token, expires_at = get_access_token_KIS(
                app_key=account.app_key,
                app_secret=account.app_secret,
                acnt_type=account.acnt_type
            )
            account.access_token = access_token  # kis_access_token -> access_token
            account.access_token_expired = expires_at
            session.add(account)
            session.commit()

        # 거래 내역 조회
        trades_response = await inquire_daily_ccld_from_KIS(account)
        
        # ... 나머지 코드 ...

    except Exception as e:
        logger.error(f"거래 내역 체크 실패 - 계정: {account.acnt_name}, 에러: {str(e)}") 

async def process_and_save_ls_balance(account: Account, balance_data: dict, session: Session) -> None:
    """LS 증권 잔고 데이터 처리 및 저장"""
    try:
        if balance_data and isinstance(balance_data, dict):
            output1 = balance_data.get("output1", [])
            output2 = balance_data.get("output2", [{}])[0] if balance_data.get("output2") else {}
            
            if output2:
                # 수익률 계산
                purchase_amount = float(output2.get("pchs_amt_smtl", 0))
                eval_profit_loss = float(output2.get("evlu_pfls_smtl", 0))
                profit_loss_rate = (eval_profit_loss / purchase_amount * 100) if purchase_amount > 0 else 0
                
                # MinutelyBalance 객체 생성 및 저장
                minutely_balance_ls = Ls_Minutely_Balance(
                    account_id=account.id,
                    timestamp=datetime.now().astimezone(timezone('Asia/Seoul')),
                    total_balance=float(output2.get("dnca_tot_amt", 0)),
                    available_balance=float(output2.get("prvs_rcdl_excc_amt", 0)),
                    total_assets=float(output2.get("tot_evlu_amt", 0)),
                    purchase_amount=purchase_amount,
                    eval_amount=float(output2.get("evlu_amt_smtl", 0)),
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
                
                session.add(minutely_balance_ls)
                session.commit()
                
    except Exception as e:
        logger.error(f"LS 잔고 데이터 처리 실패 - 계정: {account.acnt_name}, 에러: {str(e)}")

async def update_account_daily_trades_ls(account_id: str, start_date: str, end_date: str, session: Session) -> tuple[int, list]:
    """LS 증권 일별 거래내역 업데이트"""
    try:
        account = session.get(Account, account_id)
        if not account:
            return 0, [(account_id, "계좌를 찾을 수 없습니다.")]
        
        # 거래내역 조회
        trades_data = await inquire_daily_ccld_from_LS(account, start_date, end_date)
        
        if not trades_data or not isinstance(trades_data, dict):
            return 0, [(account.acnt_name, "잘못된 응답 형식")]
        
        success_count = 0
        failed_trades = []
        
        # 거래내역 처리
        for trade in trades_data.get("output1", []):
            try:
                # 거래유형 확인
                trade_type = "매수" if trade.get("sll_buy_dvsn_cd") == "01" else "매도"
                
                # 거래내역 저장
                ls_trade = Ls_Trade(
                    account_id=account.id,
                    trade_date=datetime.strptime(trade.get("ord_dt", ""), "%Y%m%d").date(),
                    trade_time=datetime.strptime(trade.get("ord_tmd", ""), "%H%M%S").time(),
                    stock_code=trade.get("pdno", ""),
                    stock_name=trade.get("prdt_name", ""),
                    trade_type=trade_type,
                    quantity=int(trade.get("ord_qty", 0)),
                    price=float(trade.get("ord_unpr", 0)),
                    amount=float(trade.get("tot_ccld_amt", 0)),
                    fee=float(trade.get("prsm_tlex_smtl", 0)),
                    tax=float(trade.get("prsm_tlex_smtl", 0)),
                    profit_amount=float(trade.get("evlu_pfls_smtl", 0))
                )
                
                session.add(ls_trade)
                success_count += 1
                
            except Exception as e:
                failed_trades.append((account.acnt_name, f"거래내역 처리 실패: {str(e)}"))
                continue
        
        if success_count > 0:
            session.commit()
        
        return success_count, failed_trades
        
    except Exception as e:
        return 0, [(account_id, f"거래내역 업데이트 실패: {str(e)}")] 

async def process_and_save_kis_balance(account: Account, balance_data: dict, session: Session) -> None:
    """KIS 증권 잔고 데이터 처리 및 저장"""
    try:
        if balance_data and isinstance(balance_data, dict):
            output1 = balance_data.get("output1", [])
            output2 = balance_data.get("output2", [{}])[0] if balance_data.get("output2") else {}
            
            if output2:
                # 수익률 계산
                purchase_amount = float(output2.get("pchs_amt_smtl_amt", 0))
                eval_profit_loss = float(output2.get("evlu_pfls_smtl_amt", 0))
                profit_loss_rate = (eval_profit_loss / purchase_amount * 100) if purchase_amount > 0 else 0
                
                # MinutelyBalance 객체 생성 및 저장
                minutely_balance_kis = Kis_Minutely_Balance(
                    account_id=account.id,
                    timestamp=datetime.now().astimezone(timezone('Asia/Seoul')),
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
                
                session.add(minutely_balance_kis)
                session.commit()
                
    except Exception as e:
        logger.error(f"KIS 잔고 데이터 처리 실패 - 계정: {account.acnt_name}, 에러: {str(e)}") 