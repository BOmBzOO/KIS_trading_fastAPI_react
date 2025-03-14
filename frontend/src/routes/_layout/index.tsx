import { Box, Container, Text, VStack, Spinner } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { useQuery } from "@tanstack/react-query"
import { useState } from "react"

import useAuth from "@/hooks/useAuth"
import { AccountsService, type AccountPublic } from "@/client"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
})

function Dashboard() {
  const { user: currentUser } = useAuth()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedAccount, setSelectedAccount] = useState<AccountPublic | null>(null)
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
      const response = await fetch(`/api/v1/accounts/${account.id}/balance`);
      if (!response.ok) {
        throw new Error('잔고 조회 실패');
      }
      const data = await response.json();
      setBalanceInfo(data);
    } catch (error) {
      console.error('잔고 조회 중 오류 발생:', error);
      alert('잔고 조회 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAccountClick = async (account: AccountPublic) => {
    setSelectedAccount(account)
    setIsModalOpen(true)
    await fetchBalance(account)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setSelectedAccount(null)
    setBalanceInfo(null)
  }

  return (
    <>
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
                      <tr key={account.id}>
                        <td 
                          style={{ 
                            padding: "8px", 
                            borderBottom: "1px solid #e2e8f0",
                            cursor: "pointer",
                            color: "#3182ce"
                          }}
                          onClick={() => handleAccountClick(account)}
                        >
                          {account.acnt_name}
                        </td>
                        <td style={{ padding: "8px", borderBottom: "1px solid #e2e8f0" }}>{account.cano}</td>
                        <td style={{ padding: "8px", borderBottom: "1px solid #e2e8f0" }}>{account.acnt_prdt_cd}</td>
                        <td style={{ padding: "8px", borderBottom: "1px solid #e2e8f0" }}>{account.acnt_type}</td>
                        <td style={{ padding: "8px", borderBottom: "1px solid #e2e8f0" }}>{account.hts_id}</td>
                        <td style={{ padding: "8px", borderBottom: "1px solid #e2e8f0" }}>{account.owner_name}</td>
                        <td style={{ padding: "8px", borderBottom: "1px solid #e2e8f0" }}>{account.is_active ? "활성" : "비활성"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </Box>
            )}
          </Box>
        </Box>
      </Container>

      {isModalOpen && selectedAccount && (
        <div style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: "rgba(0, 0, 0, 0.5)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 1000,
        }}>
          <div style={{
            backgroundColor: "white",
            padding: "24px",
            borderRadius: "8px",
            maxWidth: "500px",
            width: "90%",
            maxHeight: "90vh",
            overflowY: "auto",
          }}>
            <div style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "16px",
            }}>
              <h2 style={{ margin: 0, fontSize: "1.5rem" }}>계좌 상세 정보</h2>
              <button
                onClick={handleCloseModal}
                style={{
                  background: "none",
                  border: "none",
                  fontSize: "1.5rem",
                  cursor: "pointer",
                  padding: "0",
                }}
              >
                ×
              </button>
            </div>
            <VStack align="stretch" gap={4}>
              <Box>
                <Text fontWeight="bold">계좌명</Text>
                <Text>{selectedAccount.acnt_name}</Text>
              </Box>
              <Box>
                <Text fontWeight="bold">계좌번호</Text>
                <Text>{selectedAccount.cano}</Text>
              </Box>
              <Box>
                <Text fontWeight="bold">상품코드</Text>
                <Text>{selectedAccount.acnt_prdt_cd}</Text>
              </Box>
              <Box>
                <Text fontWeight="bold">계좌유형</Text>
                <Text>{selectedAccount.acnt_type}</Text>
              </Box>
              <Box>
                <Text fontWeight="bold">HTS ID</Text>
                <Text>{selectedAccount.hts_id}</Text>
              </Box>
              <Box>
                <Text fontWeight="bold">상태</Text>
                <Text>{selectedAccount.is_active ? "활성" : "비활성"}</Text>
              </Box>
              <Box>
                <Text fontWeight="bold">생성일</Text>
                <Text>{new Date(selectedAccount.created_at).toLocaleDateString()}</Text>
              </Box>
              <Box>
                <Text fontWeight="bold">수정일</Text>
                <Text>{new Date(selectedAccount.updated_at).toLocaleDateString()}</Text>
              </Box>

              {/* 잔고 정보 표시 */}
              <Box borderTop="1px solid #e2e8f0" pt={4}>
                <Text fontWeight="bold" fontSize="lg" mb={2}>계좌 잔고 정보</Text>
                {isLoading ? (
                  <Spinner />
                ) : balanceInfo ? (
                  <VStack align="stretch" gap={2}>
                    <Box>
                      <Text fontWeight="bold">예수금</Text>
                      <Text>{balanceInfo.output1?.[0]?.dnca_tot_amt?.toLocaleString() || '0'}원</Text>
                    </Box>
                    <Box>
                      <Text fontWeight="bold">D+2 예수금</Text>
                      <Text>{balanceInfo.output1?.[0]?.d2_dps_amt?.toLocaleString() || '0'}원</Text>
                    </Box>
                    <Box>
                      <Text fontWeight="bold">평가금액</Text>
                      <Text>{balanceInfo.output1?.[0]?.tot_evlu_amt?.toLocaleString() || '0'}원</Text>
                    </Box>
                    <Box>
                      <Text fontWeight="bold">매입금액</Text>
                      <Text>{balanceInfo.output1?.[0]?.pchs_amt?.toLocaleString() || '0'}원</Text>
                    </Box>
                    <Box>
                      <Text fontWeight="bold">평가손익</Text>
                      <Text>{balanceInfo.output1?.[0]?.evlu_pfls_amt?.toLocaleString() || '0'}원</Text>
                    </Box>
                  </VStack>
                ) : (
                  <Text>잔고 정보를 불러올 수 없습니다.</Text>
                )}
              </Box>
            </VStack>
          </div>
        </div>
      )}
    </>
  )
}
