import React from "react"
import { Container, Spinner, Flex, Button, Text, VStack, StackProps } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { FaWallet, FaChartLine, FaTrophy, FaSync } from "react-icons/fa"
import { useQuery } from "@tanstack/react-query"

import { AccountsService } from "@/client"
import useAuth from "@/hooks/useAuth"
import { DashboardHeader } from "@/components/Dashboard/DashboardHeader"
import { PortfolioList } from "@/components/Accounts/PortfolioList"
import { AccountDetail } from "@/components/Accounts/AccountDetail"
import { PortfolioItem } from "@/types/portfolio"

// 임시 데이터 정의
const MOCK_BALANCE_DATA = {
  output1: [
    {
      prdt_name: "삼성전자",
      pdno: "005930",
      evlu_pfls_rt: 15.23,
      hldg_qty: 100,
      pchs_avg_pric: 60000,
      prpr: 69000,
      evlu_pfls_amt: 900000,
      pchs_amt: 6000000,
      evlu_amt: 6900000,
    },
    {
      prdt_name: "NAVER",
      pdno: "035420",
      evlu_pfls_rt: -5.32,
      hldg_qty: 50,
      pchs_avg_pric: 200000,
      prpr: 189360,
      evlu_pfls_amt: -532000,
      pchs_amt: 10000000,
      evlu_amt: 9468000,
    },
  ],
  output2: [{
    tot_evlu_amt: 16368000,
    pchs_amt_smtl_amt: 16000000,
    evlu_pfls_smtl_amt: 368000,
    asst_icdc_erng_rt: 2.3,
    asst_icdc_erng_rt_1: 0.5,
  }],
}

const MOCK_PORTFOLIO_DATA: PortfolioItem[] = [
  {
    name: "주식계좌1",
    tags: ["활성", "실전매매"],
    returnRate: "2.3%",
    accountId: "mock1",
    accessTokenExpired: true,
    tokenExpiryTime: "2024-03-20 15:00:00",
    holdings: [
      {
        name: "삼성전자",
        code: "005930",
        returnRate: "15.23%",
        trend: "up" as const
      },
      {
        name: "NAVER",
        code: "035420",
        returnRate: "-5.32%",
        trend: "down" as const
      }
    ]
  }
]

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
})

function Dashboard() {
  const { user } = useAuth()
  const [summaryData, setSummaryData] = React.useState([
    { title: "자산", value: "0원", subtitle: "", icon: FaWallet },
    { title: "수익률(1개월)", value: "0%", subtitle: "", icon: FaChartLine },
    { title: "수익률(금일)", value: "0%", subtitle: "", icon: FaTrophy },
  ])

  const [portfolioData, setPortfolioData] = React.useState<PortfolioItem[]>([])
  const [selectedPortfolio, setSelectedPortfolio] = React.useState<string | null>(null)
  const [balanceInfo, setBalanceInfo] = React.useState<any>(null)
  const [isLoading, setIsLoading] = React.useState(false)
  const [tokenExpired, setTokenExpired] = React.useState(false)
  const [tokenExpiryTime, setTokenExpiryTime] = React.useState<string | null>(null)

  const { data: accounts, isLoading: accountsLoading, refetch: refetchAccounts } = useQuery({
    queryKey: ["accounts"],
    queryFn: () => AccountsService.readAccounts(),
  })

  const fetchBalance = async (account: any) => {
    setIsLoading(true)
    try {
      const data = await AccountsService.getBalance(account.id)
      setBalanceInfo(data)
      setTokenExpired(false)
      setTokenExpiryTime(null)
    } catch (error) {
      console.error('잔고 조회중 오류 발생:', error)
      if (error instanceof Error && 
          (error.message.includes('token') || error.message.includes('Internal Server Error'))) {
        setTokenExpired(true)
        setTokenExpiryTime(MOCK_PORTFOLIO_DATA[0].tokenExpiryTime ?? "알 수 없음")
        setBalanceInfo(MOCK_BALANCE_DATA)
      } else if (error instanceof Error) {
        alert(`잔고 조회중 오류가 발생했습니다: ${error.message}`)
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handlePortfolioClick = async (portfolio: PortfolioItem) => {
    setSelectedPortfolio(portfolio.name)
    const account = accounts?.data?.find(acc => acc.acnt_name === portfolio.name)
    if (account) {
      await fetchBalance(account)
    }
  }

  const refreshToken = async (accountId: string) => {
    try {
      const updatedAccount = await AccountsService.refreshToken(accountId)
      await refetchAccounts()
      setTokenExpired(false)
      setTokenExpiryTime(null)
      
      if (selectedPortfolio === updatedAccount.acnt_name) {
        await fetchBalance(updatedAccount)
      }
    } catch (error) {
      console.error('토큰 갱신 중 오류 발생:', error)
      if (error instanceof Error) {
        alert(`토큰 갱신 중 오류가 발생했습니다: ${error.message}`)
      }
    }
  }

  React.useEffect(() => {
    const fetchInitialData = async () => {
      if (!accounts?.data) {
        setPortfolioData(MOCK_PORTFOLIO_DATA)
        setSummaryData([
          { 
            title: "총합", 
            value: `${MOCK_BALANCE_DATA.output2[0].tot_evlu_amt.toLocaleString()}원`, 
            subtitle: "임시 데이터", 
            icon: FaWallet 
          },
          { 
            title: "수익률(1개월)", 
            value: `${MOCK_BALANCE_DATA.output2[0].asst_icdc_erng_rt}%`, 
            subtitle: "임시 데이터", 
            icon: FaChartLine 
          },
          { 
            title: "수익률(금일)", 
            value: `${MOCK_BALANCE_DATA.output2[0].asst_icdc_erng_rt_1}%`, 
            subtitle: "임시 데이터", 
            icon: FaTrophy 
          },
        ])
        if (MOCK_PORTFOLIO_DATA.length > 0) {
          setSelectedPortfolio(MOCK_PORTFOLIO_DATA[0].name)
          setBalanceInfo(MOCK_BALANCE_DATA)
          setTokenExpired(true)
          setTokenExpiryTime(MOCK_PORTFOLIO_DATA[0].tokenExpiryTime ?? "알 수 없음")
        }
        return
      }

      const balancePromises = accounts.data.map(async (account) => {
        try {
          const data = await AccountsService.getBalance(account.id)
          return { account, data, error: null }
        } catch (error) {
          console.error(`Error fetching balance for account ${account.id}:`, error)
          if (error instanceof Error && 
              (error.message.includes('token') || error.message.includes('Internal Server Error'))) {
            return { 
              account, 
              data: MOCK_BALANCE_DATA, 
              error: 'token_expired',
              tokenExpiryTime: MOCK_PORTFOLIO_DATA[0].tokenExpiryTime ?? "알 수 없음"
            }
          }
          return null
        }
      })

      const results = await Promise.all(balancePromises)
      
      let totalAssets = 0
      let totalMonthlyReturn = 0
      let totalDailyReturn = 0
      let validAccountCount = 0

      const newPortfolioData: PortfolioItem[] = []

      results.forEach(result => {
        if (!result) return

        const { account, data: balance, error, tokenExpiryTime } = result
        const accountAssets = Number(balance.output2?.[0]?.tot_evlu_amt || 0)
        const monthlyReturn = Number(balance.output2?.[0]?.asst_icdc_erng_rt || 0)
        const dailyReturn = Number(balance.output2?.[0]?.asst_icdc_erng_rt_1 || 0)
        const pchsAmt = Number(balance.output2?.[0]?.pchs_amt_smtl_amt || 0)
        const evluPflsAmt = Number(balance.output2?.[0]?.evlu_pfls_smtl_amt || 0)

        totalAssets += accountAssets
        totalMonthlyReturn += monthlyReturn
        totalDailyReturn += dailyReturn
        validAccountCount++

        const returnRate = pchsAmt === 0 ? '0.00' : ((evluPflsAmt / pchsAmt) * 100).toFixed(2)

        newPortfolioData.push({
          name: account.acnt_name,
          tags: [
            account.is_active ? "활성" : "비활성",
            account.acnt_type === "paper" ? "가상매매" : "실전매매",
          ],
          returnRate: `${returnRate}%`,
          status: balance.output1?.length ? undefined : "",
          accountId: account.id,
          accessTokenExpired: error === 'token_expired',
          tokenExpiryTime: tokenExpiryTime,
          holdings: balance.output1?.map((item: any) => ({
            name: item.prdt_name,
            code: item.pdno,
            returnRate: `${Number(item.evlu_pfls_rt).toFixed(2)}%`,
            trend: Number(item.evlu_pfls_rt) >= 0 ? "up" : "down"
          }))
        })
      })

      setSummaryData([
        { 
          title: "총합", 
          value: `${totalAssets.toLocaleString()}원`, 
          subtitle: "", 
          icon: FaWallet 
        },
        { 
          title: "수익률(1개월)", 
          value: `${(totalMonthlyReturn / validAccountCount).toFixed(2)}%`, 
          subtitle: "", 
          icon: FaChartLine 
        },
        { 
          title: "수익률(금일)", 
          value: `${(totalDailyReturn / validAccountCount).toFixed(2)}%`, 
          subtitle: "", 
          icon: FaTrophy 
        },
      ])

      setPortfolioData(newPortfolioData)

      if (newPortfolioData.length > 0) {
        handlePortfolioClick(newPortfolioData[0])
      }
    }

    fetchInitialData()
  }, [accounts])

  if (accountsLoading) {
    return (
      <Container maxW="full" p={6}>
        <Flex justify="center" align="center" minH="60vh">
          <Spinner size="xl" />
        </Flex>
      </Container>
    )
  }

  return (
    <Container maxW="full" p={{ base: 4, md: 6 }}>
      <DashboardHeader 
        userName={user?.full_name || ''} 
        summaryData={summaryData} 
      />

      <PortfolioList 
        portfolioData={portfolioData}
        selectedPortfolio={selectedPortfolio}
        onPortfolioClick={handlePortfolioClick}
        onRefreshToken={refreshToken}
      />

      {portfolioData.map((item, index) => (
        selectedPortfolio === item.name && (
          <Flex key={index} direction="column" gap={4}>
            {tokenExpired && (
              <Flex 
                bg="yellow.100" 
                p={4} 
                borderRadius="md" 
                justifyContent="space-between" 
                alignItems="center"
              >
                <Flex direction="column" gap={1}>
                  <Text color="yellow.800" fontWeight="bold">
                    데이터를 불러올 수 없습니다
                  </Text>
                  <Text color="yellow.600" fontSize="sm">
                    KIS 액세스 토큰이 만료되었거나 서버 오류가 발생했습니다
                  </Text>
                  <Text color="yellow.600" fontSize="sm">
                    만료 시간: {tokenExpiryTime}
                  </Text>
                </Flex>
                <Button
                  colorScheme="yellow"
                  onClick={() => refreshToken(item.accountId)}
                  display="flex"
                  alignItems="center"
                  gap="2"
                >
                  <FaSync />
                  토큰 갱신
                </Button>
              </Flex>
            )}
            <AccountDetail 
              portfolio={item}
              balanceInfo={balanceInfo}
              isLoading={isLoading}
            />
          </Flex>
        )
      ))}
    </Container>
  )
}