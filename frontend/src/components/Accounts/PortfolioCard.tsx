import { Box, Text, Badge, HStack, Stack, Button, Flex } from '@chakra-ui/react'
import { useColorModeValue } from '@/components/ui/color-mode'
import { FaSync } from 'react-icons/fa'

interface PortfolioCardProps {
  name: string
  tags: string[]
  returnRate: string
  isSelected?: boolean
  accessTokenExpired?: boolean
  tokenExpiryTime?: string
  accountId: string
  onClick?: () => void
  onRefreshToken?: (accountId: string) => void
}

export function PortfolioCard({
  name,
  tags,
  returnRate,
  isSelected = false,
  accessTokenExpired = false,
  tokenExpiryTime,
  accountId,
  onClick,
  onRefreshToken
}: PortfolioCardProps) {
  const cardBg = useColorModeValue(
    isSelected ? 'pastel.blue' : 'white',
    isSelected ? 'blue.800' : 'gray.700'
  )
  const cardBorder = useColorModeValue(
    isSelected ? 'blue.300' : 'pastel.gray',
    isSelected ? 'blue.400' : 'gray.600'
  )
  const cardHoverBorder = useColorModeValue('pastel.blue', 'blue.400')
  const titleColor = useColorModeValue('gray.800', 'gray.100')
  const expiryColor = useColorModeValue('gray.500', 'gray.400')

  return (
    <Box
      p={4}
      borderRadius="xl"
      bg={cardBg}
      border="1px solid"
      borderColor={cardBorder}
      cursor="pointer"
      onClick={onClick}
      position="relative"
      minW="250px"
      zIndex={1}
      _hover={{ 
        borderColor: cardHoverBorder,
        transform: 'translateY(-2px)',
        transition: 'all 0.2s ease-in-out',
        boxShadow: 'lg',
        zIndex: 2
      }}
    >
      <Stack gap={3}>
        <Flex justify="space-between" align="center">
          <Text fontSize="lg" fontWeight="bold" color={titleColor}>
            {name}
          </Text>
          {accessTokenExpired && (
            <Button
              size="sm"
              colorScheme="yellow"
              onClick={(e) => {
                e.stopPropagation()
                onRefreshToken?.(accountId)
              }}
              display="flex"
              alignItems="center"
              gap="1"
              bg="pastel.yellow"
              _hover={{ bg: 'yellow.400' }}
            >
              <FaSync />
              갱신
            </Button>
          )}
        </Flex>

        <HStack wrap="wrap" gap={2}>
          <Badge
            bg={tags.includes("실전매매") ? "pastel.blue" : "pastel.purple"}
            color={tags.includes("실전매매") ? "blue.700" : "purple.700"}
          >
            {tags.includes("실전매매") ? "실전매매" : "가상매매"}
          </Badge>
          <Badge
            bg={tags.includes("활성") ? "pastel.green" : "pastel.gray"}
            color={tags.includes("활성") ? "green.700" : "gray.700"}
          >
            {tags.includes("활성") ? "활성" : "비활성"}
          </Badge>
          {accessTokenExpired && (
            <Badge bg="pastel.red" color="red.700">
              토큰 갱신 필요
            </Badge>
          )}
        </HStack>

        <Box>
          <Text
            fontSize="xl"
            fontWeight="bold"
            color={returnRate.startsWith('-') ? 'red.500' : 'green.500'}
          >
            {returnRate}
          </Text>
          {accessTokenExpired && (
            <Text fontSize="xs" color={expiryColor}>
              만료 시간: {tokenExpiryTime}
            </Text>
          )}
        </Box>
      </Stack>
    </Box>
  )
} 