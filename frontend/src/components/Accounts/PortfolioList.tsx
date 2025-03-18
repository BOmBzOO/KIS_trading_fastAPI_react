import { Box, Heading, Flex } from '@chakra-ui/react'
import { useColorModeValue } from '@/components/ui/color-mode'
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
  const headingColor = useColorModeValue('gray.700', 'gray.100')

  return (
    <Box mb={6}>
      <Heading 
        size="md" 
        mb={4} 
        color={headingColor}
        fontWeight="bold"
        letterSpacing="tight"
      >
        포트폴리오 목록
      </Heading>
      <Box 
        position="relative"
        py={3}
        px={0}
      >
        <Flex 
          gap={4} 
          overflowX="auto" 
          pb={4}
          px={2}
          position="relative"
          css={{
            scrollbarWidth: 'thin',
            scrollbarColor: 'var(--chakra-colors-gray-300) var(--chakra-colors-gray-100)',
            '&::-webkit-scrollbar': {
              height: '8px',
            },
            '&::-webkit-scrollbar-track': {
              background: 'var(--chakra-colors-gray-100)',
              borderRadius: '4px',
            },
            '&::-webkit-scrollbar-thumb': {
              background: 'var(--chakra-colors-gray-300)',
              borderRadius: '4px',
              '&:hover': {
                background: 'var(--chakra-colors-gray-400)',
              },
            },
            _dark: {
              scrollbarColor: 'var(--chakra-colors-gray-600) var(--chakra-colors-gray-700)',
              '&::-webkit-scrollbar-track': {
                background: 'var(--chakra-colors-gray-700)',
              },
              '&::-webkit-scrollbar-thumb': {
                background: 'var(--chakra-colors-gray-600)',
                '&:hover': {
                  background: 'var(--chakra-colors-gray-500)',
                },
              },
            },
          }}
        >
          {portfolioData.map((portfolio, index) => (
            <Box key={index} position="relative" py={2}>
              <PortfolioCard
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
            </Box>
          ))}
        </Flex>
      </Box>
    </Box>
  )
} 