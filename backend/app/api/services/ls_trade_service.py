from datetime import datetime
from sqlmodel import select, Session
from app.models.ls import Ls_Trade
from app.models.account import Account
from uuid import UUID
from app.api.services.ls_api import inquire_daily_ccld_from_LS

def process_trade_data_LS(response_data: dict, account_id: str) -> list[Ls_Trade]:
    """LS 거래 데이터를 처리하여 Ls_Trade 객체 리스트로 변환"""
    trades = []
    output1 = response_data.get("output1", [])
    output2 = response_data.get("output2", {})

    # output2의 합산 정보를 저장
    summary_data = {
        "total_order_qty": int(output2.get("tot_ord_qty", 0)),
        "total_trade_qty": int(output2.get("tot_ccld_qty", 0)),
        "total_trade_amt": float(output2.get("tot_ccld_amt", 0)),
        "estimated_tax": float(output2.get("prsm_tlex_smtl", 0)),
        "avg_trade_price": float(output2.get("pchs_avg_pric", 0))
    }

    # output1의 개별 거래 데이터 처리
    for trade in output1:
        daily_trade = Ls_Trade(
            account_id=account_id,
            trade_date=datetime.strptime(trade["ord_dt"], "%Y%m%d").date(),
            trade_time=datetime.strptime(trade["ord_tmd"], "%H%M%S").time(),
            stock_code=trade["pdno"],
            stock_name=trade["prdt_name"],
            trade_type="매수" if trade["sll_buy_dvsn_cd"] == "01" else "매도",
            quantity=int(trade["ord_qty"]),
            price=float(trade["ord_unpr"]),
            amount=float(trade["tot_ccld_amt"]),
            fee=float(trade.get("prsm_tlex_smtl", 0)),
            tax=float(trade.get("prsm_tlex_smtl", 0)),
            profit_amount=float(trade.get("evlu_pfls_smtl", 0)),
            
            # 추가 필드들
            order_no=trade.get("odno"),
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

async def update_account_daily_trades_LS(
    account_id: UUID,
    start_date: str,
    end_date: str,
    session: Session
) -> tuple[int, list[tuple[str, str]]]:
    """특정 계정의 일별 거래 내역을 업데이트"""
    success_count = 0
    failed_accounts = []
    
    try:
        account = session.get(Account, account_id)
        if not account:
            return 0, [("Unknown", f"Account not found: {account_id}")]
            
        # LS API 호출
        trade_data = await inquire_daily_ccld_from_LS(account, start_date, end_date)
        
        if not trade_data.get("output1"):
            return 0, []
            
        # 거래 내역 처리 및 저장
        for trade in process_trade_data_LS(trade_data, str(account_id)):
            try:
                statement = select(Ls_Trade).where(
                    Ls_Trade.account_id == account_id,
                    Ls_Trade.trade_date == trade.trade_date,
                    Ls_Trade.order_no == trade.order_no
                )
                existing_trade = session.exec(statement).first()

                if existing_trade:
                    # 기존 거래 업데이트
                    for key, value in trade.model_dump().items():
                        setattr(existing_trade, key, value)
                else:
                    # 새 거래 추가
                    session.add(trade)

                success_count += 1

            except Exception as e:
                failed_accounts.append((account.acnt_name, f"거래 데이터 처리 실패 (주문번호: {trade.order_no}): {str(e)}"))
                continue

        session.commit()
        return success_count, failed_accounts
        
    except Exception as e:
        return 0, [(account.acnt_name if account else "Unknown", str(e))] 