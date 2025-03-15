import { Box, Container, Text, Heading } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { useQuery } from "@tanstack/react-query"
import { useState } from "react"

import useAuth from "@/hooks/useAuth"
import { AccountsService, type AccountPublic } from "@/client"
import { AccountList } from "@/components/Accounts/AccountList"
import { BalanceInfo } from "@/components/Accounts/BalanceInfo"
import { HoldingsTable } from "@/components/Accounts/HoldingsTable"
import AddAccount from "@/components/Accounts/AddAccount"

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
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} py={12}>
        계좌 관리
      </Heading>
      <AddAccount />
      <Box pt={12} m={4}>
        <Text fontSize="2xl" fontWeight="bold" mb={2} color="var(--chakra-colors-chakra-text-color)">
          안녕하세요, {currentUser?.full_name || currentUser?.email}님 👋🏼
        </Text>
        <Text mb={8} color="var(--chakra-colors-chakra-text-color)">환영합니다!</Text>

        <Box>
          <Text fontSize="xl" fontWeight="bold" mb={6} color="var(--chakra-colors-chakra-text-color)">내 증권 계좌 정보</Text>
          <AccountList 
            accounts={accounts?.data}
            isLoading={accountsLoading}
            selectedAccountId={selectedAccountId}
            onAccountClick={handleAccountClick}
            balanceInfo={balanceInfo}
            balanceLoading={isLoading}
          />
          {selectedAccountId && (
            <Box mt={4} p={4} backgroundColor="var(--chakra-colors-chakra-subtle-bg)" borderRadius="lg">
              <BalanceInfo balanceInfo={balanceInfo} isLoading={isLoading} />
              <HoldingsTable holdings={balanceInfo?.output1 || []} />
            </Box>
          )}
        </Box>
      </Box>
    </Container>
  )
}
