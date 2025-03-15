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
      console.log('Balance API Response:', JSON.stringify(data, null, 2));
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
        <Text fontSize="2xl" fontWeight="bold" mb={2} color="var(--chakra-colors-chakra-text-color)">
          안녕하세요, {currentUser?.full_name || currentUser?.email}님 👋🏼
        </Text>
        <Text mb={8} color="var(--chakra-colors-chakra-text-color)">환영합니다!</Text>

        <Box>
          <Text fontSize="xl" fontWeight="bold" mb={6} color="var(--chakra-colors-chakra-text-color)">내 증권 계좌 정보</Text>
          {accountsLoading ? (
            <Spinner />
          ) : !accounts?.data.length ? (
            <Text color="var(--chakra-colors-chakra-text-color)">등록된 계좌가 없습니다.</Text>
          ) : (
            <Box overflowX="auto" borderRadius="lg" border="1px solid var(--chakra-colors-chakra-border-color)">
              <table style={{ 
                width: "100%", 
                borderCollapse: "collapse",
                color: "var(--chakra-colors-chakra-text-color)"
              }}>
                <thead>
                  <tr style={{ backgroundColor: "var(--chakra-colors-chakra-subtle-bg)" }}>
                    <th style={{ 
                      padding: "12px 16px", 
                      textAlign: "left", 
                      borderBottom: "1px solid var(--chakra-colors-chakra-border-color)",
                      color: "var(--chakra-colors-chakra-text-color)",
                      fontWeight: "bold"
                    }}>계좌명</th>
                    <th style={{ 
                      padding: "12px 16px", 
                      textAlign: "left", 
                      borderBottom: "1px solid var(--chakra-colors-chakra-border-color)",
                      color: "var(--chakra-colors-chakra-text-color)",
                      fontWeight: "bold"
                    }}>계좌번호</th>
                    <th style={{ 
                      padding: "12px 16px", 
                      textAlign: "left", 
                      borderBottom: "1px solid var(--chakra-colors-chakra-border-color)",
                      color: "var(--chakra-colors-chakra-text-color)",
                      fontWeight: "bold"
                    }}>상품코드</th>
                    <th style={{ 
                      padding: "12px 16px", 
                      textAlign: "left", 
                      borderBottom: "1px solid var(--chakra-colors-chakra-border-color)",
                      color: "var(--chakra-colors-chakra-text-color)",
                      fontWeight: "bold"
                    }}>계좌유형</th>
                    <th style={{ 
                      padding: "12px 16px", 
                      textAlign: "left", 
                      borderBottom: "1px solid var(--chakra-colors-chakra-border-color)",
                      color: "var(--chakra-colors-chakra-text-color)",
                      fontWeight: "bold"
                    }}>HTS ID</th>
                    <th style={{ 
                      padding: "12px 16px", 
                      textAlign: "left", 
                      borderBottom: "1px solid var(--chakra-colors-chakra-border-color)",
                      color: "var(--chakra-colors-chakra-text-color)",
                      fontWeight: "bold"
                    }}>소유주</th>
                    <th style={{ 
                      padding: "12px 16px", 
                      textAlign: "left", 
                      borderBottom: "1px solid var(--chakra-colors-chakra-border-color)",
                      color: "var(--chakra-colors-chakra-text-color)",
                      fontWeight: "bold"
                    }}>상태</th>
                  </tr>
                </thead>
                <tbody>
                  {accounts.data.map((account) => (
                    <React.Fragment key={account.id}>
                      <tr style={{ 
                        backgroundColor: selectedAccountId === account.id ? "var(--chakra-colors-chakra-subtle-bg)" : "transparent",
                        transition: "background-color 0.2s"
                      }}>
                        <td 
                          style={{ 
                            padding: "12px 16px", 
                            borderBottom: selectedAccountId === account.id ? "none" : "1px solid var(--chakra-colors-chakra-border-color)",
                            cursor: "pointer",
                            color: "var(--chakra-colors-blue-500)",
                            fontWeight: "500"
                          }}
                          onClick={() => handleAccountClick(account)}
                        >
                          {account.acnt_name}
                        </td>
                        <td style={{ 
                          padding: "12px 16px", 
                          borderBottom: selectedAccountId === account.id ? "none" : "1px solid var(--chakra-colors-chakra-border-color)",
                          color: "var(--chakra-colors-chakra-text-color)"
                        }}>{account.cano}</td>
                        <td style={{ 
                          padding: "12px 16px", 
                          borderBottom: selectedAccountId === account.id ? "none" : "1px solid var(--chakra-colors-chakra-border-color)",
                          color: "var(--chakra-colors-chakra-text-color)"
                        }}>{account.acnt_prdt_cd}</td>
                        <td style={{ 
                          padding: "12px 16px", 
                          borderBottom: selectedAccountId === account.id ? "none" : "1px solid var(--chakra-colors-chakra-border-color)",
                          color: "var(--chakra-colors-chakra-text-color)"
                        }}>{account.acnt_type}</td>
                        <td style={{ 
                          padding: "12px 16px", 
                          borderBottom: selectedAccountId === account.id ? "none" : "1px solid var(--chakra-colors-chakra-border-color)",
                          color: "var(--chakra-colors-chakra-text-color)"
                        }}>{account.hts_id}</td>
                        <td style={{ 
                          padding: "12px 16px", 
                          borderBottom: selectedAccountId === account.id ? "none" : "1px solid var(--chakra-colors-chakra-border-color)",
                          color: "var(--chakra-colors-chakra-text-color)"
                        }}>{account.owner_name}</td>
                        <td style={{ 
                          padding: "12px 16px", 
                          borderBottom: selectedAccountId === account.id ? "none" : "1px solid var(--chakra-colors-chakra-border-color)",
                          color: "var(--chakra-colors-chakra-text-color)"
                        }}>{account.is_active ? "활성" : "비활성"}</td>
                      </tr>
                      {selectedAccountId === account.id && (
                        <tr>
                          <td colSpan={7} style={{ 
                            padding: "24px", 
                            backgroundColor: "var(--chakra-colors-chakra-subtle-bg)",
                            borderBottom: "1px solid var(--chakra-colors-chakra-border-color)"
                          }}>
                            {isLoading ? (
                              <Spinner />
                            ) : balanceInfo ? (
                              <Box>
                                <Text fontWeight="bold" fontSize="xl" mb={6} color="var(--chakra-colors-chakra-text-color)">계좌 잔고 정보</Text>
                                <Box 
                                  display="grid" 
                                  gridTemplateColumns={{ base: "1fr", md: "repeat(2, 1fr)", lg: "repeat(3, 1fr)" }} 
                                  gap={6} 
                                  mb={8}
                                >
                                  <Box 
                                    p={4} 
                                    borderRadius="lg" 
                                    border="1px solid var(--chakra-colors-chakra-border-color)"
                                    backgroundColor="var(--chakra-colors-chakra-bg)"
                                  >
                                    <Text fontWeight="bold" mb={2} color="var(--chakra-colors-chakra-text-color)">예수금</Text>
                                    <Text fontSize="xl" color="var(--chakra-colors-chakra-text-color)">{balanceInfo.output2?.[0]?.dnca_tot_amt?.toLocaleString() || '0'}원</Text>
                                  </Box>
                                  <Box 
                                    p={4} 
                                    borderRadius="lg" 
                                    border="1px solid var(--chakra-colors-chakra-border-color)"
                                    backgroundColor="var(--chakra-colors-chakra-bg)"
                                  >
                                    <Text fontWeight="bold" mb={2} color="var(--chakra-colors-chakra-text-color)">D+2 예수금</Text>
                                    <Text fontSize="xl" color="var(--chakra-colors-chakra-text-color)">{balanceInfo.output2?.[0]?.prvs_rcdl_excc_amt?.toLocaleString() || '0'}원</Text>
                                  </Box>
                                  <Box 
                                    p={4} 
                                    borderRadius="lg" 
                                    border="1px solid var(--chakra-colors-chakra-border-color)"
                                    backgroundColor="var(--chakra-colors-chakra-bg)"
                                  >
                                    <Text fontWeight="bold" mb={2} color="var(--chakra-colors-chakra-text-color)">총평가금액</Text>
                                    <Text fontSize="xl" color="var(--chakra-colors-chakra-text-color)">{balanceInfo.output2?.[0]?.tot_evlu_amt?.toLocaleString() || '0'}원</Text>
                                  </Box>
                                  <Box 
                                    p={4} 
                                    borderRadius="lg" 
                                    border="1px solid var(--chakra-colors-chakra-border-color)"
                                    backgroundColor="var(--chakra-colors-chakra-bg)"
                                  >
                                    <Text fontWeight="bold" mb={2} color="var(--chakra-colors-chakra-text-color)">매입금액 합계</Text>
                                    <Text fontSize="xl" color="var(--chakra-colors-chakra-text-color)">{balanceInfo.output2?.[0]?.pchs_amt_smtl_amt?.toLocaleString() || '0'}원</Text>
                                  </Box>
                                  <Box 
                                    p={4} 
                                    borderRadius="lg" 
                                    border="1px solid var(--chakra-colors-chakra-border-color)"
                                    backgroundColor="var(--chakra-colors-chakra-bg)"
                                  >
                                    <Text fontWeight="bold" mb={2} color="var(--chakra-colors-chakra-text-color)">평가손익 합계</Text>
                                    <Text fontSize="xl" color="var(--chakra-colors-chakra-text-color)">{balanceInfo.output2?.[0]?.evlu_pfls_smtl_amt?.toLocaleString() || '0'}원</Text>
                                  </Box>
                                  <Box 
                                    p={4} 
                                    borderRadius="lg" 
                                    border="1px solid var(--chakra-colors-chakra-border-color)"
                                    backgroundColor="var(--chakra-colors-chakra-bg)"
                                  >
                                    <Text fontWeight="bold" mb={2} color="var(--chakra-colors-chakra-text-color)">총수익률</Text>
                                    <Text fontSize="xl" color="var(--chakra-colors-chakra-text-color)">
                                      {(() => {
                                        const pchsAmt = balanceInfo.output2?.[0]?.pchs_amt_smtl_amt || 0;
                                        const evluPflsAmt = balanceInfo.output2?.[0]?.evlu_pfls_smtl_amt || 0;
                                        if (pchsAmt === 0) return '0.00';
                                        return ((evluPflsAmt / pchsAmt) * 100).toFixed(2);
                                      })()}%
                                    </Text>
                                  </Box>
                                </Box>

                                {balanceInfo.output1?.length > 0 && (
                                  <Box>
                                    <Text fontWeight="bold" fontSize="xl" mb={4} color="var(--chakra-colors-chakra-text-color)">보유종목 정보</Text>
                                    <Box overflowX="auto" borderRadius="lg" border="1px solid var(--chakra-colors-chakra-border-color)">
                                      <table style={{ 
                                        width: "100%", 
                                        borderCollapse: "collapse",
                                        color: "var(--chakra-colors-chakra-text-color)"
                                      }}>
                                        <thead>
                                          <tr style={{ backgroundColor: "var(--chakra-colors-chakra-subtle-bg)" }}>
                                            <th style={{ 
                                              padding: "12px 16px", 
                                              textAlign: "left", 
                                              borderBottom: "1px solid var(--chakra-colors-chakra-border-color)",
                                              color: "var(--chakra-colors-chakra-text-color)",
                                              fontWeight: "bold"
                                            }}>종목명</th>
                                            <th style={{ 
                                              padding: "12px 16px", 
                                              textAlign: "right", 
                                              borderBottom: "1px solid var(--chakra-colors-chakra-border-color)",
                                              color: "var(--chakra-colors-chakra-text-color)",
                                              fontWeight: "bold"
                                            }}>보유수량</th>
                                            <th style={{ 
                                              padding: "12px 16px", 
                                              textAlign: "right", 
                                              borderBottom: "1px solid var(--chakra-colors-chakra-border-color)",
                                              color: "var(--chakra-colors-chakra-text-color)",
                                              fontWeight: "bold"
                                            }}>평가금액</th>
                                            <th style={{ 
                                              padding: "12px 16px", 
                                              textAlign: "right", 
                                              borderBottom: "1px solid var(--chakra-colors-chakra-border-color)",
                                              color: "var(--chakra-colors-chakra-text-color)",
                                              fontWeight: "bold"
                                            }}>평가손익</th>
                                            <th style={{ 
                                              padding: "12px 16px", 
                                              textAlign: "right", 
                                              borderBottom: "1px solid var(--chakra-colors-chakra-border-color)",
                                              color: "var(--chakra-colors-chakra-text-color)",
                                              fontWeight: "bold"
                                            }}>수익률</th>
                                          </tr>
                                        </thead>
                                        <tbody>
                                          {balanceInfo.output1.map((item: any, index: number) => (
                                            <tr key={index} style={{ 
                                              backgroundColor: index % 2 === 0 ? "var(--chakra-colors-chakra-subtle-bg)" : "transparent"
                                            }}>
                                              <td style={{ 
                                                padding: "12px 16px", 
                                                borderBottom: "1px solid var(--chakra-colors-chakra-border-color)",
                                                color: "var(--chakra-colors-chakra-text-color)",
                                                fontWeight: "500"
                                              }}>{item.prdt_name}</td>
                                              <td style={{ 
                                                padding: "12px 16px", 
                                                textAlign: "right", 
                                                borderBottom: "1px solid var(--chakra-colors-chakra-border-color)",
                                                color: "var(--chakra-colors-chakra-text-color)"
                                              }}>{item.hldg_qty?.toLocaleString()}</td>
                                              <td style={{ 
                                                padding: "12px 16px", 
                                                textAlign: "right", 
                                                borderBottom: "1px solid var(--chakra-colors-chakra-border-color)",
                                                color: "var(--chakra-colors-chakra-text-color)"
                                              }}>{item.evlu_amt?.toLocaleString()}</td>
                                              <td style={{ 
                                                padding: "12px 16px", 
                                                textAlign: "right", 
                                                borderBottom: "1px solid var(--chakra-colors-chakra-border-color)",
                                                color: "var(--chakra-colors-chakra-text-color)"
                                              }}>{item.evlu_pfls_amt?.toLocaleString()}</td>
                                              <td style={{ 
                                                padding: "12px 16px", 
                                                textAlign: "right", 
                                                borderBottom: "1px solid var(--chakra-colors-chakra-border-color)",
                                                color: "var(--chakra-colors-chakra-text-color)"
                                              }}>{item.evlu_pfls_rt?.toFixed(2)}%</td>
                                            </tr>
                                          ))}
                                        </tbody>
                                      </table>
                                    </Box>
                                  </Box>
                                )}
                              </Box>
                            ) : (
                              <Text color="var(--chakra-colors-chakra-text-color)">잔고 정보를 불러올 수 없습니다.</Text>
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
