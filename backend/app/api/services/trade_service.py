from datetime import datetime
from sqlmodel import select
from app.models import DailyTrade, Account

def process_trade_data(response_data: dict, account_id: str) -> list[DailyTrade]:
    """거래 데이터를 처리하여 DailyTrade 객체 리스트로 변환"""
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
            account_id=account_id,
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