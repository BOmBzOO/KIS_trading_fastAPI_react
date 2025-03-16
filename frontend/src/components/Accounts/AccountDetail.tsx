import React from 'react'
import { Box, Flex, SimpleGrid, Text, Spinner } from '@chakra-ui/react'
import { PerformanceChart } from '@/components/PerformanceChart'
import { BalanceInfo } from './BalanceInfo'
import { HoldingsTable } from './HoldingsTable'
import { PortfolioItem } from '@/types/portfolio'

interface AccountDetailProps {
  portfolio: PortfolioItem
  balanceInfo: any
  isLoading: boolean
}

export function AccountDetail({ portfolio, balanceInfo, isLoading }: AccountDetailProps) {
  if (isLoading) {
    return (
      <Box p={4} display="flex" justifyContent="center">
        <Spinner />
      </Box>
    )
  }

  if (!balanceInfo) {
    return null
  }

  return (
    <Flex direction="column" gap={6}>
      {/* 상단: 잔고와 차트 */}
      <SimpleGrid columns={{ base: 1, xl: 2 }} gap={6}>
        {/* 잔고 정보 */}
        <BalanceInfo balanceInfo={balanceInfo} />

        {/* 차트 */}
        <Box 
          p={6}
          borderRadius="xl"
          border="2px solid var(--chakra-colors-gray-200)"
          backgroundColor="var(--chakra-colors-chakra-bg)"
          _dark={{
            borderColor: "var(--chakra-colors-gray-600)"
          }}
          height="400px"
        >
          <PerformanceChart accountId={portfolio.name} />
        </Box>
      </SimpleGrid>

      {/* 하단: 보유종목 */}
      <Box 
        borderRadius="xl" 
        border="2px solid var(--chakra-colors-gray-200)"
        overflow="hidden"
        _dark={{
          borderColor: "var(--chakra-colors-gray-600)"
        }}
      >
        <Text px={6} py={3} fontSize="lg" fontWeight="bold" borderBottom="1px solid var(--chakra-colors-gray-200)" _dark={{ borderColor: "var(--chakra-colors-gray-600)" }}>
          보유종목
        </Text>
        {portfolio.holdings && portfolio.holdings.length > 0 ? (
          <HoldingsTable holdings={balanceInfo.output1 || []} />
        ) : (
          <Text p={6} textAlign="center" fontSize="sm" color="gray.500">
            보유 중인 종목이 없습니다.
          </Text>
        )}
      </Box>
    </Flex>
  )
} 