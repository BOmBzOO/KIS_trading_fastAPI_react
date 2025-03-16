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
import { BalanceInfo } from "./BalanceInfo"

interface AccountTableProps {
  accounts: AccountPublic[] | undefined
  isLoading: boolean
  selectedAccountId: string | null
  onAccountClick: (account: AccountPublic) => void
  balanceInfo: any
  balanceLoading: boolean
}

export function AccountTable({ 
  accounts, 
  isLoading, 
  selectedAccountId, 
  onAccountClick, 
  balanceInfo, 
  balanceLoading 
}: AccountTableProps) {
  if (isLoading) {
    return <Spinner />
  }

  if (!accounts?.length) {
    return <Text color="var(--chakra-colors-chakra-text-color)">등록된 계좌가 없습니다.</Text>
  }

  return (
    <Box mb={8}>
      <Text fontSize="xl" fontWeight="bold" mb={4}>계좌 관리</Text>
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
                        <BalanceInfo balanceInfo={balanceInfo} />
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
    </Box>
  )
} 