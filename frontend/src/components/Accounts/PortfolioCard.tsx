import React from 'react'
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
  onClick?: () => void
  onRefreshToken?: () => void
}

export function PortfolioCard({
  name,
  tags,
  returnRate,
  isSelected = false,
  accessTokenExpired = false,
  tokenExpiryTime,
  onClick,
  onRefreshToken
}: PortfolioCardProps) {
  return (
    <Box
      p={4}
      borderRadius="lg"
      bg={isSelected ? (useColorModeValue('blue.50', 'blue.800')) : useColorModeValue('white', 'gray.700')}
      border="1px solid"
      borderColor={isSelected ? 'blue.300' : useColorModeValue('gray.200', 'gray.600')}
      cursor="pointer"
      onClick={onClick}
      _hover={{ borderColor: useColorModeValue('blue.300', 'blue.400') }}
      position="relative"
      minW="250px"
    >
      <Stack gap={3}>
        <Flex justify="space-between" align="center">
          <Text fontSize="lg" fontWeight="bold" color={useColorModeValue('gray.800', 'gray.100')}>
            {name}
          </Text>
          {accessTokenExpired && (
            <Button
              size="sm"
              colorScheme="yellow"
              onClick={(e) => {
                e.stopPropagation()
                onRefreshToken?.()
              }}
              display="flex"
              alignItems="center"
              gap="2"
            >
              <FaSync />
              갱신
            </Button>
          )}
        </Flex>

        <HStack wrap="wrap" gap={2}>
          <Badge
            colorScheme={tags.includes("활성") ? "green" : "gray"}
          >
            {tags.includes("활성") ? "활성" : "비활성"}
          </Badge>
          <Badge
            colorScheme={tags.includes("실전매매") ? "blue" : "purple"}
          >
            {tags.includes("실전매매") ? "실전매매" : "가상매매"}
          </Badge>
          {accessTokenExpired && (
            <Badge colorScheme="red">
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
            <Text fontSize="xs" color={useColorModeValue('gray.500', 'gray.400')}>
              만료 시간: {tokenExpiryTime}
            </Text>
          )}
        </Box>
      </Stack>
    </Box>
  )
} 