import React from "react"
import { Container, Heading, Box, Text } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { useQuery } from "@tanstack/react-query"
import { useState } from "react"

import { AccountList } from "@/components/Accounts/AccountList"
import AddAccount from "@/components/Accounts/AddAccount"
import { AccountsService, type AccountPublic } from "@/client"

export const Route = createFileRoute("/_layout/accounts")({
  component: Accounts,
})

function Accounts() {
  const [selectedAccountId, setSelectedAccountId] = useState<string | null>(null)
  const [balanceInfo, setBalanceInfo] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  
  const { data: accounts, isLoading: accountsLoading } = useQuery({
    queryKey: ["accounts"],
    queryFn: () => AccountsService.readAccounts(),
    retry: false,
  })

  const handleAccountClick = async (account: AccountPublic) => {
    if (selectedAccountId === account.id) {
      setSelectedAccountId(null)
      setBalanceInfo(null)
    } else {
      setSelectedAccountId(account.id)
      await fetchBalance(account)
    }
  }

  const fetchBalance = async (account: AccountPublic) => {
    setIsLoading(true)
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/accounts/${account.id}/balance`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        }
      })
      if (!response.ok) {
        const errorText = await response.text()
        console.error('Response status:', response.status)
        console.error('Response text:', errorText)
        throw new Error(`잔고 조회 실패 (${response.status}): ${errorText}`)
      }
      const data = await response.json()
      setBalanceInfo(data)
    } catch (error) {
      console.error('잔고 조회중 오류 발생:', error)
      if (error instanceof Error) {
        alert(`잔고 조회중 오류가 발생했습니다: ${error.message}`)
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} py={12}>
        계좌 관리
      </Heading>
      <AddAccount />
      <Box pt={12} m={4}>
        <Text fontSize="xl" fontWeight="bold" mb={6} color="var(--chakra-colors-chakra-text-color)">내 증권 계좌 정보</Text>
        <AccountList 
          accounts={accounts?.data}
          isLoading={accountsLoading}
          selectedAccountId={selectedAccountId}
          onAccountClick={handleAccountClick}
          balanceInfo={balanceInfo}
          balanceLoading={isLoading}
        />
      </Box>
    </Container>
  )
}

export const NewAccountRoute = createFileRoute("/_layout/accounts")({
  component: NewAccount,
})

function NewAccount(): React.ReactElement {
  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} py={12}>
        새 계좌 추가
      </Heading>
      <AddAccount />
    </Container>
  )
}
