import React from "react"
import { Container, Heading, Box } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { useQuery } from "@tanstack/react-query"
import { useState } from "react"

import { AccountsService, type AccountPublic } from "@/client"
import { AccountTable } from "@/components/Accounts/AccountTable"
import AddAccount from "@/components/Accounts/AddAccount"

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
      const data = await AccountsService.inquireBalanceFromKis(account.id)
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
      <Box pt={12}>
        <AccountTable 
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
