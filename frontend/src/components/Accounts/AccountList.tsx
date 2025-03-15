import React from "react"
import {
  Box,
  Text,
  VStack,
  Spinner,
} from "@chakra-ui/react"

import { type AccountPublic } from "@/client"
import DeleteAccount from "./DeleteAccount"
import EditAccount from "./EditAccount"

interface AccountListProps {
  accounts: AccountPublic[] | undefined
  isLoading: boolean
  selectedAccountId: string | null
  onAccountClick: (account: AccountPublic) => void
  balanceInfo: any
  balanceLoading: boolean
}

export function AccountList({ accounts, isLoading, selectedAccountId, onAccountClick, balanceInfo, balanceLoading }: AccountListProps) {
  if (isLoading) {
    return <Spinner />
  }

  if (!accounts?.length) {
    return <Text color="var(--chakra-colors-chakra-text-color)">등록된 계좌가 없습니다.</Text>
  }

  return (
    <VStack gap={4} align="stretch">
      <Box overflowX="auto" borderRadius="0.5rem" border="1px solid var(--chakra-colors-chakra-border-color)">
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
              <th style={{ 
                padding: "12px 16px", 
                textAlign: "left", 
                borderBottom: "1px solid var(--chakra-colors-chakra-border-color)",
                color: "var(--chakra-colors-chakra-text-color)",
                fontWeight: "bold"
              }}>작업</th>
            </tr>
          </thead>
          <tbody>
            {accounts.map((account) => (
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
                    onClick={() => onAccountClick(account)}
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
                  <td style={{ 
                    padding: "12px 16px", 
                    borderBottom: selectedAccountId === account.id ? "none" : "1px solid var(--chakra-colors-chakra-border-color)",
                    color: "var(--chakra-colors-chakra-text-color)"
                  }}>
                    <VStack gap={2}>
                      <EditAccount account={account} />
                      <DeleteAccount id={account.id} />
                    </VStack>
                  </td>
                </tr>
                {selectedAccountId === account.id && (
                  <tr>
                    <td colSpan={8} style={{ 
                      padding: "24px", 
                      backgroundColor: "var(--chakra-colors-chakra-subtle-bg)",
                      borderBottom: "1px solid var(--chakra-colors-chakra-border-color)"
                    }}>
                      {balanceLoading ? (
                        <Spinner />
                      ) : balanceInfo ? (
                        <Box>
                          <Text fontWeight="bold" fontSize="xl" mb={6} color="var(--chakra-colors-chakra-text-color)">잔고</Text>
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
                              <Text fontWeight="bold" mb={2} color="var(--chakra-colors-chakra-text-color)">평가금액</Text>
                              <Text fontSize="xl" color="var(--chakra-colors-chakra-text-color)">{balanceInfo.output2?.[0]?.tot_evlu_amt?.toLocaleString() || '0'}원</Text>
                            </Box>
                            <Box 
                              p={4} 
                              borderRadius="lg" 
                              border="1px solid var(--chakra-colors-chakra-border-color)"
                              backgroundColor="var(--chakra-colors-chakra-bg)"
                            >
                              <Text fontWeight="bold" mb={2} color="var(--chakra-colors-chakra-text-color)">매입금액</Text>
                              <Text fontSize="xl" color="var(--chakra-colors-chakra-text-color)">{balanceInfo.output2?.[0]?.pchs_amt_smtl_amt?.toLocaleString() || '0'}원</Text>
                            </Box>
                            <Box 
                              p={4} 
                              borderRadius="lg" 
                              border="1px solid var(--chakra-colors-chakra-border-color)"
                              backgroundColor="var(--chakra-colors-chakra-bg)"
                            >
                              <Text fontWeight="bold" mb={2} color="var(--chakra-colors-chakra-text-color)">평가손익</Text>
                              <Text fontSize="xl" color="var(--chakra-colors-chakra-text-color)">{balanceInfo.output2?.[0]?.evlu_pfls_smtl_amt?.toLocaleString() || '0'}원</Text>
                            </Box>
                            <Box 
                              p={4} 
                              borderRadius="lg" 
                              border="1px solid var(--chakra-colors-chakra-border-color)"
                              backgroundColor="var(--chakra-colors-chakra-bg)"
                            >
                              <Text fontWeight="bold" mb={2} color="var(--chakra-colors-chakra-text-color)">수익률</Text>
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
                              <Text fontWeight="bold" fontSize="xl" mb={4} color="var(--chakra-colors-chakra-text-color)">보유종목</Text>
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
    </VStack>
  )
} 