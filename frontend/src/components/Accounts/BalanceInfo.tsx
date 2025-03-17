import { Box, SimpleGrid, Text } from '@chakra-ui/react'

interface BalanceInfoProps {
  balanceInfo: any
}

export function BalanceInfo({ balanceInfo }: BalanceInfoProps) {
  const output2 = balanceInfo?.output2?.[0] || {}
  
  const calculateReturnRate = (pchsAmt: number, evluPflsAmt: number) => {
    if (pchsAmt === 0) return '0.00'
    const returnRate = (evluPflsAmt / pchsAmt) * 100
    return returnRate.toFixed(2)
  }
  
  const balanceItems = [
    { label: '예수금', value: output2.dnca_tot_amt || 0 },
    { label: 'D+2 예수금', value: output2.prvs_rcdl_excc_amt || 0 },
    { label: '평가금액', value: output2.tot_evlu_amt || 0 },
    { label: '매입금액', value: output2.pchs_amt_smtl_amt || 0 },
    { 
      label: '평가손익', 
      value: output2.evlu_pfls_smtl_amt || 0,
      isProfit: true 
    },
    {
      label: '수익률',
      value: calculateReturnRate(
        output2.pchs_amt_smtl_amt || 0,
        output2.evlu_pfls_smtl_amt || 0
      ),
      isProfit: true,
      isPercentage: true
    }
  ]

  return (
    <Box 
      p={6}
      borderRadius="xl"
      border="2px solid var(--chakra-colors-gray-200)"
      backgroundColor="var(--chakra-colors-chakra-bg)"
      _dark={{
        borderColor: "var(--chakra-colors-gray-600)"
      }}
    >
      <SimpleGrid columns={{ base: 1, sm: 2, xl: 2 }} gap={6}>
        {balanceItems.map((item, index) => (
          <Box key={index}>
            <Text fontSize="sm" color="gray.500" mb={1}>{item.label}</Text>
            <Text 
              fontSize="xl" 
              fontWeight="bold"
              color={item.isProfit && Number(item.value) !== 0 
                ? Number(item.value) >= 0 ? "red.500" : "blue.500"
                : undefined}
            >
              {item.isPercentage 
                ? `${item.value}%`
                : `${Number(item.value).toLocaleString()}원`}
            </Text>
          </Box>
        ))}
      </SimpleGrid>
    </Box>
  )
} 