import { Box, Heading, Flex } from '@chakra-ui/react'
import { PortfolioCard } from './PortfolioCard'
import { PortfolioItem } from '@/client/types.gen'

interface PortfolioListProps {
  portfolioData: PortfolioItem[]
  selectedPortfolio: string | null
  onPortfolioClick: (portfolio: PortfolioItem) => void
  onRefreshToken: (accountId: string) => void
}

export function PortfolioList({
  portfolioData,
  selectedPortfolio,
  onPortfolioClick,
  onRefreshToken
}: PortfolioListProps) {
  return (
    <Box mb={6}>
      <Heading size="md" mb={4}>포트폴리오 목록</Heading>
      <Flex gap={4} overflowX="auto" pb={2}>
        {portfolioData.map((portfolio, index) => (
          <PortfolioCard
            key={index}
            name={portfolio.name}
            tags={portfolio.tags}
            returnRate={portfolio.returnRate}
            isSelected={selectedPortfolio === portfolio.name}
            accessTokenExpired={portfolio.accessTokenExpired}
            tokenExpiryTime={portfolio.tokenExpiryTime}
            accountId={portfolio.accountId}
            onClick={() => onPortfolioClick(portfolio)}
            onRefreshToken={() => onRefreshToken(portfolio.accountId)}
          />
        ))}
      </Flex>
    </Box>
  )
} 