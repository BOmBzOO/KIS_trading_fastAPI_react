import React from 'react'
import { Box, Flex, Heading, Text, SimpleGrid } from '@chakra-ui/react'
import { SummaryCard } from './SummaryCard'

interface DashboardHeaderProps {
  userName: string
  summaryData: Array<{
    title: string
    value: string
    subtitle: string
    icon?: React.ElementType
  }>
}

export function DashboardHeader({ userName, summaryData }: DashboardHeaderProps) {
  return (
    <Box mb={8}>
      <Flex 
        justify="space-between" 
        align="center" 
        mb={6}
        flexDirection={{ base: "column", md: "row" }}
        gap={{ base: 2, md: 0 }}
      >
        <Heading size="lg">{userName || 'Guest'}님의 자산을 알려드립니다!💰</Heading>
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
  )
} 