import { Box, Container, Text, Spinner } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { useQuery } from "@tanstack/react-query"
import { useState } from "react"
import React from "react"

import useAuth from "@/hooks/useAuth"
import { AccountsService, type AccountPublic } from "@/client"

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
})

function Dashboard() {
  const { user: currentUser } = useAuth()
  const [selectedAccountId, setSelectedAccountId] = useState<string | null>(null)
  const [balanceInfo, setBalanceInfo] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  
  const { data: accounts, isLoading: accountsLoading } = useQuery({
    queryKey: ["accounts"],
    queryFn: () => AccountsService.readAccounts(),
    retry: false,
  })

  const fetchBalance = async (account: AccountPublic) => {
    setIsLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/accounts/${account.id}/balance`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        }
      });
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Response status:', response.status);
        console.error('Response text:', errorText);
        throw new Error(`잔고 조회 실패 (${response.status}): ${errorText}`);
      }
      const data = await response.json();
      console.log('Balance data:', data);
      setBalanceInfo(data);
    } catch (error) {
      console.error('잔고 조회 중 오류 발생:', error);
      if (error instanceof Error) {
        alert(`잔고 조회 중 오류가 발생했습니다: ${error.message}`);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleAccountClick = async (account: AccountPublic) => {
    if (selectedAccountId === account.id) {
      setSelectedAccountId(null);
      setBalanceInfo(null);
    } else {
      setSelectedAccountId(account.id);
      await fetchBalance(account);
    }
  }

  return (
    <Container maxW="full">
      <Box pt={12} m={4}>
        <Text fontSize="2xl" truncate maxW="sm">
          안녕하세요, {currentUser?.full_name || currentUser?.email}님 👋🏼
        </Text>
        <Text mb={8}>환영합니다!</Text>

        <Box>
          <Text fontSize="xl" mb={4}>내 증권 계좌 정보</Text>
          {accountsLoading ? (
            <Spinner />
          ) : !accounts?.data.length ? (
            <Text>등록된 계좌가 없습니다.</Text>
          ) : (
            <Box overflowX="auto">
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr>
                    <th style={{ padding: "8px", textAlign: "left", borderBottom: "1px solid #e2e8f0" }}>계좌명</th>
                    <th style={{ padding: "8px", textAlign: "left", borderBottom: "1px solid #e2e8f0" }}>계좌번호</th>
                    <th style={{ padding: "8px", textAlign: "left", borderBottom: "1px solid #e2e8f0" }}>상품코드</th>
                    <th style={{ padding: "8px", textAlign: "left", borderBottom: "1px solid #e2e8f0" }}>계좌유형</th>
                    <th style={{ padding: "8px", textAlign: "left", borderBottom: "1px solid #e2e8f0" }}>HTS ID</th>
                    <th style={{ padding: "8px", textAlign: "left", borderBottom: "1px solid #e2e8f0" }}>소유주</th>
                    <th style={{ padding: "8px", textAlign: "left", borderBottom: "1px solid #e2e8f0" }}>상태</th>
                  </tr>
                </thead>
                <tbody>
                  {accounts.data.map((account) => (
                    <React.Fragment key={account.id}>
                      <tr>
                        <td 
                          style={{ 
                            padding: "8px", 
                            borderBottom: selectedAccountId === account.id ? "none" : "1px solid #e2e8f0",
                            cursor: "pointer",
                            color: "#3182ce"
                          }}
                          onClick={() => handleAccountClick(account)}
                        >
                          {account.acnt_name}
                        </td>
                        <td style={{ padding: "8px", borderBottom: selectedAccountId === account.id ? "none" : "1px solid #e2e8f0" }}>{account.cano}</td>
                        <td style={{ padding: "8px", borderBottom: selectedAccountId === account.id ? "none" : "1px solid #e2e8f0" }}>{account.acnt_prdt_cd}</td>
                        <td style={{ padding: "8px", borderBottom: selectedAccountId === account.id ? "none" : "1px solid #e2e8f0" }}>{account.acnt_type}</td>
                        <td style={{ padding: "8px", borderBottom: selectedAccountId === account.id ? "none" : "1px solid #e2e8f0" }}>{account.hts_id}</td>
                        <td style={{ padding: "8px", borderBottom: selectedAccountId === account.id ? "none" : "1px solid #e2e8f0" }}>{account.owner_name}</td>
                        <td style={{ padding: "8px", borderBottom: selectedAccountId === account.id ? "none" : "1px solid #e2e8f0" }}>{account.is_active ? "활성" : "비활성"}</td>
                      </tr>
                      {selectedAccountId === account.id && (
                        <tr>
                          <td colSpan={7} style={{ padding: "16px", backgroundColor: "#f8f9fa", borderBottom: "1px solid #e2e8f0" }}>
                            {isLoading ? (
                              <Spinner />
                            ) : balanceInfo ? (
                              <Box>
                                <Text fontWeight="bold" fontSize="lg" mb={4}>계좌 잔고 정보</Text>
                                <Box display="grid" gridTemplateColumns="repeat(auto-fit, minmax(200px, 1fr))" gap={4} mb={6}>
                                  <Box>
                                    <Text fontWeight="bold">예수금</Text>
                                    <Text>{balanceInfo.output2?.[0]?.dnca_tot_amt?.toLocaleString() || '0'}원</Text>
                                  </Box>
                                  <Box>
                                    <Text fontWeight="bold">D+2 예수금</Text>
                                    <Text>{balanceInfo.output2?.[0]?.d2_dps_amt?.toLocaleString() || '0'}원</Text>
                                  </Box>
                                  <Box>
                                    <Text fontWeight="bold">총평가금액</Text>
                                    <Text>{balanceInfo.output2?.[0]?.tot_evlu_amt?.toLocaleString() || '0'}원</Text>
                                  </Box>
                                  <Box>
                                    <Text fontWeight="bold">매입금액 합계</Text>
                                    <Text>{balanceInfo.output2?.[0]?.pchs_amt_smtl?.toLocaleString() || '0'}원</Text>
                                  </Box>
                                  <Box>
                                    <Text fontWeight="bold">평가손익 합계</Text>
                                    <Text>{balanceInfo.output2?.[0]?.evlu_pfls_amt_smtl?.toLocaleString() || '0'}원</Text>
                                  </Box>
                                  <Box>
                                    <Text fontWeight="bold">총수익률</Text>
                                    <Text>{balanceInfo.output2?.[0]?.tot_pftrt?.toFixed(2) || '0'}%</Text>
                                  </Box>
                                </Box>

                                {balanceInfo.output1?.length > 0 && (
                                  <Box>
                                    <Text fontWeight="bold" fontSize="lg" mb={2}>보유종목 정보</Text>
                                    <table style={{ width: "100%", borderCollapse: "collapse" }}>
                                      <thead>
                                        <tr>
                                          <th style={{ padding: "8px", textAlign: "left", borderBottom: "1px solid #e2e8f0" }}>종목명</th>
                                          <th style={{ padding: "8px", textAlign: "right", borderBottom: "1px solid #e2e8f0" }}>보유수량</th>
                                          <th style={{ padding: "8px", textAlign: "right", borderBottom: "1px solid #e2e8f0" }}>평가금액</th>
                                          <th style={{ padding: "8px", textAlign: "right", borderBottom: "1px solid #e2e8f0" }}>평가손익</th>
                                          <th style={{ padding: "8px", textAlign: "right", borderBottom: "1px solid #e2e8f0" }}>수익률</th>
                                        </tr>
                                      </thead>
                                      <tbody>
                                        {balanceInfo.output1.map((item: any, index: number) => (
                                          <tr key={index}>
                                            <td style={{ padding: "8px", borderBottom: "1px solid #e2e8f0" }}>{item.prdt_name}</td>
                                            <td style={{ padding: "8px", textAlign: "right", borderBottom: "1px solid #e2e8f0" }}>{item.hldg_qty?.toLocaleString()}</td>
                                            <td style={{ padding: "8px", textAlign: "right", borderBottom: "1px solid #e2e8f0" }}>{item.evlu_amt?.toLocaleString()}</td>
                                            <td style={{ padding: "8px", textAlign: "right", borderBottom: "1px solid #e2e8f0" }}>{item.evlu_pfls_amt?.toLocaleString()}</td>
                                            <td style={{ padding: "8px", textAlign: "right", borderBottom: "1px solid #e2e8f0" }}>{item.evlu_pfls_rt?.toFixed(2)}%</td>
                                          </tr>
                                        ))}
                                      </tbody>
                                    </table>
                                  </Box>
                                )}
                              </Box>
                            ) : (
                              <Text>잔고 정보를 불러올 수 없습니다.</Text>
                            )}
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  ))}
                </tbody>
              </table>
            </Box>
          )}
        </Box>
      </Box>
    </Container>
  )
}
