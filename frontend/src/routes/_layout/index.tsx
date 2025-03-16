import React, { useEffect } from "react"
import { 
  Box, 
  Container, 
  Text, 
  Heading, 
  SimpleGrid, 
  Flex, 
  Icon,
  HStack,
  Badge,
  Spinner
} from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { FaWallet, FaChartLine, FaTrophy } from "react-icons/fa"
import { useQuery } from "@tanstack/react-query"

import { AccountsService } from "@/client"
import useAuth from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
})

interface SummaryCardProps {
  title: string
  value: string
  subtitle?: string
  icon?: React.ElementType
}

const SummaryCard = ({ title, value, subtitle, icon }: SummaryCardProps) => (
  <Box 
    py={4}
    px={6}
    borderRadius="xl" 
    border="2px solid var(--chakra-colors-gray-200)"
    backgroundColor="var(--chakra-colors-chakra-bg)"
    _dark={{
      borderColor: "var(--chakra-colors-gray-600)"
    }}
    transition="all 0.2s"
    _hover={{
      transform: "translateY(-2px)",
      boxShadow: "lg"
    }}
  >
    <Flex alignItems="center" mb={3}>
      {icon && <Icon as={icon} boxSize={5} color="blue.500" mr={2} />}
      <Text fontSize="sm" color="gray.500" fontWeight="medium" _dark={{ color: "gray.400" }}>{title}</Text>
    </Flex>
    <Text fontSize="2xl" fontWeight="bold" mb={1} _dark={{ color: "white" }}>{value}</Text>
    {subtitle && <Text fontSize="sm" color="gray.500" _dark={{ color: "gray.400" }}>{subtitle}</Text>}
  </Box>
)

interface PortfolioCardProps {
  name: string
  tags: string[]
  returnRate: string
  status?: string
  isSelected?: boolean
  onClick?: () => void
}

const PortfolioCard = ({ name, tags, returnRate, status, isSelected, onClick }: PortfolioCardProps) => (
  <Box 
    py={4}
    px={6}
    borderRadius="xl" 
    border="2px solid var(--chakra-colors-gray-200)"
    backgroundColor={isSelected ? "var(--chakra-colors-blue-50)" : "var(--chakra-colors-chakra-bg)"}
    cursor="pointer"
    onClick={onClick}
    transition="all 0.2s"
    _dark={{
      borderColor: "var(--chakra-colors-gray-600)",
      backgroundColor: isSelected ? "var(--chakra-colors-blue-900)" : "var(--chakra-colors-chakra-bg)"
    }}
    _hover={{
      transform: "translateY(-2px)",
      boxShadow: "lg",
      borderColor: "var(--chakra-colors-blue-500)"
    }}
  >
    <Text fontSize="lg" fontWeight="bold" mb={3} _dark={{ color: "white" }}>{name}</Text>
    <HStack gap={2} mb={4} flexWrap="wrap">
      {tags.map((tag, index) => (
        <Badge key={index} variant="subtle" colorScheme="gray" fontSize="xs">
          {tag}
        </Badge>
      ))}
    </HStack>
    <Flex justify="space-between" align="center">
      {status && <Text fontSize="sm" color="gray.500" _dark={{ color: "gray.400" }}>{status}</Text>}
      <Text fontSize="2xl" fontWeight="bold" color="red.500">{returnRate}</Text>
    </Flex>
  </Box>
)

interface StockHoldingProps {
  name: string
  code: string
  returnRate: string
  trend: "up" | "down"
}

const StockHolding = ({ name, code, returnRate, trend }: StockHoldingProps) => (
  <Flex 
    justify="space-between" 
    align="center" 
    py={2}
    px={6}
    borderBottom="1px solid var(--chakra-colors-gray-200)"
    _dark={{
      borderColor: "var(--chakra-colors-gray-600)"
    }}
  >
    <Flex align="center" gap={2} flex={1} minWidth={0}>
      <Text 
        fontWeight="medium"
        color="var(--chakra-colors-gray-700)"
        _dark={{
          color: "var(--chakra-colors-gray-100)"
        }}
        maxWidth="140px"
        overflow="hidden"
        textOverflow="ellipsis"
        whiteSpace="nowrap"
      >
        - {name}
      </Text>
      <Text fontSize="xs" color="gray.500" _dark={{ color: "gray.400" }} flexShrink={0}>{code}</Text>
    </Flex>
    <Text 
      fontWeight="medium" 
      color={trend === "up" ? "red.500" : "blue.500"}
      flexShrink={0}
    >
      {returnRate}
    </Text>
  </Flex>
)

interface PortfolioItem {
  name: string
  tags: string[]
  returnRate: string
  status?: string
  totalAssets?: string
  availableCash?: string
  depositBalance?: string
  d2DepositBalance?: string
  evaluationAmount?: string
  purchaseAmount?: string
  evaluationProfitLoss?: string
  profitLossRate?: string
  holdings?: Array<{
    name: string
    code: string
    returnRate: string
    trend: "up" | "down"
  }>
}

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

  const { data: accounts, isLoading: accountsLoading } = useQuery({
    queryKey: ["accounts"],
    queryFn: () => AccountsService.readAccounts(),
  })

  const fetchBalance = async (account: any) => {
    setIsLoading(true)
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/accounts/${account.id}/balance`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'application/json',
          }
        }
      )
      if (!response.ok) {
        const errorText = await response.text()
        console.error('Response status:', response.status)
        console.error('Response text:', errorText)
        throw new Error(`잔고 조회 실패 (${response.status}): ${errorText}`)
      }
      const data = await response.json()
      console.log('Balance data:', data)
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

  const handlePortfolioClick = async (portfolio: any) => {
    if (selectedPortfolio === portfolio.name) {
      setSelectedPortfolio(null)
      setBalanceInfo(null)
    } else {
      setSelectedPortfolio(portfolio.name)
      const account = accounts?.data?.find(acc => acc.acnt_name === portfolio.name)
      if (account) {
        await fetchBalance(account)
      }
    }
  }

  useEffect(() => {
    const fetchInitialData = async () => {
      if (!accounts?.data) return

      const balancePromises = accounts.data.map(async (account) => {
        try {
          const response = await fetch(
            `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/accounts/${account.id}/balance`,
            {
              headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                'Content-Type': 'application/json',
              }
            }
          )
          if (!response.ok) throw new Error('Balance fetch failed')
          return { account, data: await response.json() }
        } catch (error) {
          console.error(`Error fetching balance for account ${account.id}:`, error)
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

        const { account, data: balance } = result
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
            "트레이딩"
          ],
          returnRate: `${returnRate}%`,
          status: balance.output1?.length ? undefined : "",
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
      <Box mb={8}>
        <Flex 
          justify="space-between" 
          align="center" 
          mb={6}
          flexDirection={{ base: "column", md: "row" }}
          gap={{ base: 2, md: 0 }}
        >
          <Heading size="lg">{user?.full_name || 'Guest'}님의 자산을 알려드립니다!💰</Heading>
          <Text color="gray.500" fontSize={{ base: "sm", md: "md" }}>
            최근 업데이트: {new Date().toLocaleString()}
          </Text>
        </Flex>
        
        <SimpleGrid columns={{ base: 1, md: 3 }} gap={{ base: 4, md: 6 }}>
          {summaryData.map((item, index) => (
            <SummaryCard key={index} {...item} />
          ))}
        </SimpleGrid>
      </Box>

      <Box mb={8}>
        <Text fontSize="xl" fontWeight="bold" mb={4}>포트폴리오</Text>
        <SimpleGrid columns={{ base: 1, md: 3 }} gap={{ base: 4, md: 6 }}>
          {portfolioData.map((item, index) => (
            <Box key={index}>
              <PortfolioCard 
                {...item} 
                isSelected={selectedPortfolio === item.name}
                onClick={() => handlePortfolioClick(item)}
              />
              {(!selectedPortfolio || selectedPortfolio === item.name) && (
                <>
                  {selectedPortfolio === item.name && (
                    <>
                      {isLoading ? (
                        <Box mt={2} p={4} display="flex" justifyContent="center">
                          <Spinner />
                        </Box>
                      ) : balanceInfo && (
                        <Box 
                          mt={2}
                          p={4}
                          borderRadius="xl"
                          border="2px solid var(--chakra-colors-gray-200)"
                          backgroundColor="var(--chakra-colors-chakra-bg)"
                          _dark={{
                            borderColor: "var(--chakra-colors-gray-600)"
                          }}
                        >
                          <SimpleGrid columns={1} gap={4}>
                            <Box>
                              <Text fontSize="sm" color="gray.500" mb={1}>예수금</Text>
                              <Text fontWeight="bold">
                                {Number(balanceInfo.output2?.[0]?.dnca_tot_amt || 0).toLocaleString()}원
                              </Text>
                            </Box>
                            <Box>
                              <Text fontSize="sm" color="gray.500" mb={1}>D+2 예수금</Text>
                              <Text fontWeight="bold">
                                {Number(balanceInfo.output2?.[0]?.prvs_rcdl_excc_amt || 0).toLocaleString()}원
                              </Text>
                            </Box>
                            <Box>
                              <Text fontSize="sm" color="gray.500" mb={1}>평가금액</Text>
                              <Text fontWeight="bold">
                                {Number(balanceInfo.output2?.[0]?.tot_evlu_amt || 0).toLocaleString()}원
                              </Text>
                            </Box>
                            <Box>
                              <Text fontSize="sm" color="gray.500" mb={1}>매입금액</Text>
                              <Text fontWeight="bold">
                                {Number(balanceInfo.output2?.[0]?.pchs_amt_smtl_amt || 0).toLocaleString()}원
                              </Text>
                            </Box>
                            <Box>
                              <Text fontSize="sm" color="gray.500" mb={1}>평가손익</Text>
                              <Text 
                                fontWeight="bold" 
                                color={Number(balanceInfo.output2?.[0]?.evlu_pfls_smtl_amt || 0) >= 0 ? "red.500" : "blue.500"}
                              >
                                {Number(balanceInfo.output2?.[0]?.evlu_pfls_smtl_amt || 0).toLocaleString()}원
                              </Text>
                            </Box>
                            <Box>
                              <Text fontSize="sm" color="gray.500" mb={1}>수익률</Text>
                              <Text 
                                fontWeight="bold" 
                                color={Number(balanceInfo.output2?.[0]?.evlu_pfls_smtl_amt || 0) >= 0 ? "red.500" : "blue.500"}
                              >
                                {(() => {
                                  const pchsAmt = balanceInfo.output2?.[0]?.pchs_amt_smtl_amt || 0;
                                  const evluPflsAmt = balanceInfo.output2?.[0]?.evlu_pfls_smtl_amt || 0;
                                  if (pchsAmt === 0) return '0.00';
                                  return ((evluPflsAmt / pchsAmt) * 100).toFixed(2);
                                })()}%
                              </Text>
                            </Box>
                          </SimpleGrid>
                        </Box>
                      )}
                    </>
                  )}
                  <Box 
                    mt={2}
                    borderRadius="xl" 
                    border="2px solid var(--chakra-colors-gray-200)"
                    overflow="hidden"
                    _dark={{
                      borderColor: "var(--chakra-colors-gray-600)"
                    }}
                  >
                    <Text px={6} py={2} fontWeight="bold" borderBottom="1px solid var(--chakra-colors-gray-200)" _dark={{ borderColor: "var(--chakra-colors-gray-600)" }}>
                      보유종목
                    </Text>
                    {item.holdings && item.holdings.length > 0 ? (
                      <>
                        {(selectedPortfolio === item.name ? item.holdings : item.holdings.slice(0, 3)).map((holding, idx) => (
                          <StockHolding key={idx} {...holding} />
                        ))}
                        {!selectedPortfolio && item.holdings.length > 3 && (
                          <Text px={8} py={2} textAlign="left" fontSize="sm" color="gray.500">
                            외 {item.holdings.length - 3}종목 더보기
                          </Text>
                        )}
                      </>
                    ) : (
                      <Text p={4} textAlign="center" fontSize="sm" color="gray.500">
                        보유 중인 종목이 없습니다.
                      </Text>
                    )}
                  </Box>
                </>
              )}
            </Box>
          ))}
        </SimpleGrid>
      </Box>
    </Container>
  )
}