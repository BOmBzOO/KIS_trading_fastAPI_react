from datetime import datetime, timedelta
import requests
from fastapi import HTTPException
from app.models.account import Account
from app.constants import (
    LS_API_BASE_URL,
    LS_API_ENDPOINTS,
    LS_API_TR_ID,
    LS_API_PARAMS
)
from typing import Any

def get_access_token_LS(app_key: str, app_secret: str, acnt_type: str) -> tuple[str, datetime]:
    """
    LS API를 통해 access token을 받아옵니다.
    Returns:
        tuple[str, datetime]: (access_token, expires_at)
    """
    base_url = LS_API_BASE_URL[acnt_type]
    try:
        headers = {
            "content-type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "client_credentials",
            "appkey": app_key,
            "appsecretkey": app_secret,
            "scope": "oob"
        }
        
        response = requests.post(
            f"{base_url}{LS_API_ENDPOINTS['token']}",
            headers=headers,
            data=data
        )
        response.raise_for_status()
        data = response.json()

        # print(data)
        access_token = data.get("access_token", "")
        expires_in = data.get("expires_in", 86400)
        expires_at = datetime.now() + timedelta(seconds=expires_in)
        
        return access_token, expires_at
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"LS API 토큰 발급 실패: {str(e)}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=f"LS API 토큰 만료 시간 파싱 실패: {str(e)}"
        )

async def inquire_balance_from_LS(account: Account) -> Any:
    """LS API를 통한 잔고 조회"""
    base_url = LS_API_BASE_URL[account.acnt_type]
    
    try:
        # 요청 헤더 설정
        headers = {
            "content-type": "application/json; charset=utf-8",
            "authorization": f"Bearer {account.access_token}",
            "tr_cd":  LS_API_TR_ID["balance"],  # 주식잔고2 TR
            "tr_cont": "N",
            "tr_cont_key": "",
            "mac_address": account.mac_address if hasattr(account, 'mac_address') else ""
        }

        # 요청 바디 설정
        request_body = {
            "t0424InBlock": {
                "prcgb": "1",    # 단가구분
                "chegb": "1",    # 체결구분
                "dangb": "1",    # 단일가구분
                "charge": "1",   # 제비용포함여부
                "cts_expcode": ""  # CTS_종목번호
            }
        }

        response = requests.post(
            f"{base_url}{LS_API_ENDPOINTS['balance']}",
            headers=headers,
            json=request_body
        )
        response.raise_for_status()
        data = response.json()

        # 응답 코드 확인
        if data.get("rsp_cd") != "00000":
            raise HTTPException(
                status_code=400,
                detail=f"LS API 오류: {data.get('rsp_msg', '알 수 없는 오류')}"
            )

        # 응답 데이터 변환
        balance_response = {
            "rt_cd": data.get("rsp_cd"),
            "msg1": data.get("rsp_msg"),
            "output1": [],  # 보유종목 상세내역
            "output2": []   # 계좌잔고 종합
        }

        # output1 (보유종목 상세) 변환
        for holding in data.get("t0424OutBlock1", []):
            balance_response["output1"].append({
                "pdno": holding.get("expcode"),          # 종목번호
                "prdt_name": holding.get("hname"),       # 종목명
                "hldg_qty": holding.get("janqty"),       # 잔고수량
                "pchs_avg_pric": holding.get("pamt"),    # 평균단가
                "prpr": holding.get("price"),            # 현재가
                "evlu_pfls_amt": holding.get("dtsunik"), # 평가손익
                "evlu_pfls_rt": holding.get("sunikrt"),  # 수익률
                "market_gb": holding.get("marketgb"),    # 시장구분
                "jong_gb": holding.get("jonggb"),        # 종목구분
                "jan_rt": holding.get("janrt"),          # 보유비중
                "app_amt": holding.get("appamt"),        # 평가금액
                "fee": holding.get("fee"),               # 수수료
                "tax": holding.get("tax"),               # 제세금
                "sin_inter": holding.get("sininter"),    # 신용이자
                "mdpos_qt": holding.get("mdposqt"),      # 매도가능수량
                "sin_amt": holding.get("sinamt"),        # 대출금액
                "last_dt": holding.get("lastdt"),        # 만기일자
                "loan_dt": holding.get("loandt"),        # 대출일자
                "msat": holding.get("msat"),             # 당일매수금액
                "mpms": holding.get("mpms"),             # 당일매수단가
                "mdat": holding.get("mdat"),             # 당일매도금액
                "mpmd": holding.get("mpmd"),             # 당일매도단가
                "jsat": holding.get("jsat"),             # 전일매수금액
                "jpms": holding.get("jpms"),             # 전일매수단가
                "jdat": holding.get("jdat"),             # 전일매도금액
                "jpmd": holding.get("jpmd")              # 전일매도단가
            })

        # output2 (계좌잔고 종합) 변환
        out_block = data.get("t0424OutBlock", {})
        balance_response["output2"].append({
            "dnca_tot_amt": out_block.get("sunamt"),      # 추정순자산
            "tot_evlu_amt": out_block.get("tappamt"),     # 평가금액
            "pchs_amt_smtl": out_block.get("mamt"),       # 매입금액
            "evlu_amt_smtl": out_block.get("tappamt"),    # 평가금액
            "evlu_pfls_smtl": out_block.get("tdtsunik"),  # 평가손익
            "tot_evlu_pfls_rt": round(
                (out_block.get("tdtsunik", 0) / out_block.get("mamt", 1)) * 100, 2
            ) if out_block.get("mamt") else 0,  # 총수익률
            "sunamt1": out_block.get("sunamt1"),          # 추정D2예수금
            "dtsunik": out_block.get("dtsunik")           # 실현손익
        })

        return balance_response

    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"LS API 잔고 조회 실패: {str(e)}"
        )

async def inquire_daily_ccld_from_LS(account: Account, start_date: str, end_date: str) -> dict:
    """LS API를 통해 일별 주문체결 내역을 조회"""
    base_url = LS_API_BASE_URL[account.acnt_type]
    
    try:
        # 요청 헤더 설정
        headers = {
            "content-type": "application/json; charset=utf-8",
            "authorization": f"Bearer {account.access_token}",
            "tr_cd": LS_API_TR_ID["daily_trades"],
            "tr_cont": "N",
            "tr_cont_key": "",
            "mac_address": account.mac_address if hasattr(account, 'mac_address') else ""
        }

        # 요청 바디 설정
        request_body = {
            "CDPCQ04700InBlock1": {
                "QryTp": "0",           # 전체 조회
                "QrySrtDt": start_date.replace("-", ""),  # 조회시작일
                "QryEndDt": end_date.replace("-", ""),    # 조회종료일
                "SrtNo": "0",           # 시작번호
                "PdptnCode": "01",      # 상품유형코드 (주식)
                "IsuLgclssCode": "01",  # 종목대분류코드 (주식)
                "IsuNo": ""             # 종목번호 (전체)
            }
        }

        response = requests.post(
            f"{base_url}{LS_API_ENDPOINTS['daily_trades']}",
            headers=headers,
            json=request_body
        )
        response.raise_for_status()
        data = response.json()

        # 응답 코드 확인
        if data.get("rsp_cd") != "00000":
            raise HTTPException(
                status_code=400,
                detail=f"LS API 오류: {data.get('rsp_msg', '알 수 없는 오류')}"
            )

        # 응답 데이터 변환
        trade_response = {
            "rt_cd": data.get("rsp_cd"),
            "msg1": data.get("rsp_msg"),
            "output1": [],  # 거래내역
            "output2": []   # 계좌정보
        }

        # output1 (거래내역) 변환
        for trade in data.get("CDPCQ04700OutBlock3", []):
            trade_response["output1"].append({
                "ord_dt": trade.get("TrdDt"),           # 거래일자
                "pdno": trade.get("IsuNo"),             # 종목코드
                "prdt_name": trade.get("IsuNm"),        # 종목명
                "odno": trade.get("TrdNo"),             # 거래번호
                "ord_tmd": trade.get("TrxTime"),        # 거래시간
                "sll_buy_dvsn_cd": "01" if trade.get("TrdQty", 0) > 0 else "02",  # 매수/매도 구분
                "ord_unpr": trade.get("TrdUprc"),       # 거래단가
                "ord_qty": trade.get("TrdQty"),         # 거래수량
                "tot_ccld_qty": trade.get("TrdQty"),    # 체결수량
                "tot_ccld_amt": trade.get("TrdAmt"),    # 체결금액
                "rmn_qty": trade.get("BalUnit"),        # 잔고수량
                "cncl_cfrm_qty": "0",                   # 취소확인수량
                "orgn_odno": trade.get("OrgTrdNo"),     # 원거래번호
                "ord_dvsn_name": trade.get("TpCodeNm"), # 주문구분명
                "sll_buy_dvsn_cd_name": "매수" if trade.get("TrdQty", 0) > 0 else "매도",  # 매수/매도 구분명
                "cncl_yn": "N",                         # 취소여부
                "loan_dt": trade.get("LoanDt"),         # 대출일자
                "ord_gno_brno": trade.get("TrxBrnNo"),  # 주문지점번호
                "ord_dvsn_cd": "00",                    # 주문구분코드
                "rjct_qty": "0",                        # 거절수량
                "ccld_cndt_name": trade.get("TrdmdaNm"), # 체결조건명
                "inqr_ip_addr": "",                     # 조회IP주소
                "cpbc_ordp_ord_rcit_dvsn_cd": "",      # 주문접수구분코드
                "cpbc_ordp_infm_mthd_dvsn_cd": "",     # 주문정보전달방법구분코드
                "infm_tmd": trade.get("TrxTime"),       # 정보전달시간
                "ctac_tlno": "",                        # 연락처
                "prdt_type_cd": trade.get("PdptnCode"), # 상품유형코드
                "excg_dvsn_cd": "",                     # 거래소구분코드
                "cpbc_ordp_mtrl_dvsn_cd": "",          # 주문매체구분코드
                "ord_orgno": "",                        # 주문기관번호
                "rsvn_ord_end_dt": "",                  # 예약주문종료일자
                "excg_id_dvsn_cd": "",                  # 거래소ID구분코드
                "stpm_cndt_pric": "",                   # 정지조건가격
                "stpm_efct_occr_dtmd": "",             # 정지효력발생일시
                "cmsn_amt": trade.get("CmsnAmt"),      # 수수료
                "tax_sum_amt": trade.get("TaxSumAmt"),  # 세금합계금액
                "evr_tax": trade.get("EvrTax"),        # 제세금
                "ictax": trade.get("Ictax"),           # 소득세
                "ihtax": trade.get("Ihtax"),           # 주민세
                "trtax": trade.get("Trtax"),           # 거래세
                "exec_tax": trade.get("ExecTax"),      # 체결세금
                "mny_dvd_amt": trade.get("MnyDvdAmt"), # 배당금액
                "rcvbl_ocr_amt": trade.get("RcvblOcrAmt"), # 미수발생금액
                "trx_brn_nm": trade.get("TrxBrnNm"),   # 처리지점명
                "base_prc": trade.get("BasePrc"),      # 기준가
                "dps_crbal_amt": trade.get("DpsCrbalAmt"), # 예수금금잔금액
                "mnyout_able_amt": trade.get("MnyoutAbleAmt"), # 출금가능금액
                "bns_base_prc": trade.get("BnsBasePrc"), # 매매기준가
                "taxchr_base_prc": trade.get("TaxchrBasePrc"), # 과세기준가
                "trd_unit": trade.get("TrdUnit"),      # 거래좌수
                "eval_amt": trade.get("EvalAmt"),      # 평가금액
                "bnspl_amt": trade.get("BnsplAmt"),    # 매매손익금액
                "opp_acnt_nm": trade.get("OppAcntNm"), # 상대계좌명
                "opp_acnt_no": trade.get("OppAcntNo"), # 상대계좌번호
                "loan_rfund_amt": trade.get("LoanRfundAmt"), # 대출상환금액
                "loan_intrst_amt": trade.get("LoanIntrstAmt"), # 대출이자금액
                "askpsn_nm": trade.get("AskpsnNm"),    # 의뢰인명
                "ord_dt": trade.get("OrdDt"),          # 주문일자
                "rdct_cmsn": trade.get("RdctCmsn")     # 감면수수료
            })

        # output2 (계좌정보) 변환
        out_block = data.get("CDPCQ04700OutBlock2", {})
        trade_response["output2"].append({
            "acnt_nm": out_block.get("AcntNm", ""),    # 계좌명
            "rec_cnt": out_block.get("RecCnt", 0)      # 레코드갯수
        })

        # output4 (손익합계) 변환
        out_block4 = data.get("CDPCQ04700OutBlock4", {})
        trade_response["output4"] = [{
            "pnl_sum_amt": out_block4.get("PnlSumAmt", 0),  # 손익합계금액
            "ctrct_asm": out_block4.get("CtrctAsm", 0),    # 약정누계
            "cmsn_amt_sum_amt": out_block4.get("CmsnAmtSumAmt", 0)  # 수수료합계금액
        }]

        # output5 (매매합계) 변환
        out_block5 = data.get("CDPCQ04700OutBlock5", {})
        trade_response["output5"] = [{
            "mnyin_amt": out_block5.get("MnyinAmt", 0),    # 입금금액
            "secin_amt": out_block5.get("SecinAmt", 0),    # 입고금액
            "mnyout_amt": out_block5.get("MnyoutAmt", 0),  # 출금금액
            "secout_amt": out_block5.get("SecoutAmt", 0),  # 출고금액
            "diff_amt": out_block5.get("DiffAmt", 0),      # 차이금액
            "diff_amt0": out_block5.get("DiffAmt0", 0),    # 차이금액0
            "sell_qty": out_block5.get("SellQty", 0),      # 매도수량
            "sell_amt": out_block5.get("SellAmt", 0),      # 매도금액
            "sell_cmsn": out_block5.get("SellCmsn", 0),    # 매도수수료
            "evr_tax": out_block5.get("EvrTax", 0),        # 제세금
            "fcurr_sell_adjst_amt": out_block5.get("FcurrSellAdjstAmt", 0),  # 외화매도정산금액
            "buy_qty": out_block5.get("BuyQty", 0),        # 매수수량
            "buy_amt": out_block5.get("BuyAmt", 0),        # 매수금액
            "buy_cmsn": out_block5.get("BuyCmsn", 0),      # 매수수수료
            "exec_tax": out_block5.get("ExecTax", 0),      # 체결세금
            "fcurr_buy_adjst_amt": out_block5.get("FcurrBuyAdjstAmt", 0)     # 외화매수정산금액
        }]

        return trade_response

    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"LS API 거래내역 조회 실패: {str(e)}"
        )

async def inquire_account_info_from_LS(account: Account) -> dict:
    """LS API를 통해 계좌 정보를 조회"""
    base_url = LS_API_BASE_URL[account.acnt_type]
    
    try:
        # 요청 헤더 설정
        headers = {
            "content-type": "application/json; charset=utf-8",
            "authorization": f"Bearer {account.access_token}",
            "tr_cd": "CDPCQ04700",  # 계좌정보 조회 TR
            "tr_cont": "N",
            "tr_cont_key": "",
            "mac_address": account.mac_address if hasattr(account, 'mac_address') else ""
        }

        # 요청 바디 설정
        request_body = {
            "CDPCQ04700InBlock1": {
                "QryTp": "0",           # 전체 조회
                "QrySrtDt": datetime.now().strftime("%Y%m%d"),  # 오늘 날짜
                "QryEndDt": datetime.now().strftime("%Y%m%d"),  # 오늘 날짜
                "SrtNo": "0",           # 시작번호
                "PdptnCode": "01",      # 상품유형코드 (주식)
                "IsuLgclssCode": "01",  # 종목대분류코드 (주식)
                "IsuNo": ""             # 종목번호 (전체)
            }
        }

        response = requests.post(
            f"{base_url}{LS_API_ENDPOINTS['daily_trades']}",  # 계좌정보 조회는 daily_trades 엔드포인트 사용
            headers=headers,
            json=request_body
        )
        response.raise_for_status()
        data = response.json()

        # 응답 코드 확인
        if data.get("rsp_cd") != "00000":
            raise HTTPException(
                status_code=400,
                detail=f"LS API 오류: {data.get('rsp_msg', '알 수 없는 오류')}"
            )

        # 계좌 정보 추출
        account_info = data.get("CDPCQ04700OutBlock2", {})
        
        return {
            "cano": account_info.get("AcntNo", ""),  # 계좌번호
            "acnt_prdt_cd": account_info.get("AcntPrdtCode", ""),  # 계좌상품코드
            "hts_id": account_info.get("HtsId", "")  # HTS ID
        }

    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"LS API 계좌정보 조회 실패: {str(e)}"
        ) 