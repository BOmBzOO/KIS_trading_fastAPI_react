import { Box, Text, Spinner } from "@chakra-ui/react"

interface BalanceInfoProps {
  balanceInfo: any
  isLoading: boolean
}

export function BalanceInfo({ balanceInfo, isLoading }: BalanceInfoProps) {
  if (isLoading) {
    return <Spinner />
  }

  if (!balanceInfo) {
    return <Text color="var(--chakra-colors-chakra-text-color)">잔고 정보를 불러올 수 없습니다.</Text>
  }

  return (
    <Box>
      <Text fontWeight="bold" fontSize="xl" mb={6} color="var(--chakra-colors-chakra-text-color)">계좌 잔고 정보</Text>
      <Box 
        display="grid" 
        gridTemplateColumns={{ base: "1fr", md: "repeat(2, 1fr)", lg: "repeat(3, 1fr)" }} 
        gap={6} 
        mb={8}
      >
        <Box 
          p={4} 
          borderRadius="lg" 
          border="1px solid var(--chakra-colors-chakra-border-color)"
          backgroundColor="var(--chakra-colors-chakra-bg)"
        >
          <Text fontWeight="bold" mb={2} color="var(--chakra-colors-chakra-text-color)">예수금</Text>
          <Text fontSize="xl" color="var(--chakra-colors-chakra-text-color)">{balanceInfo.output2?.[0]?.dnca_tot_amt?.toLocaleString() || '0'}원</Text>
        </Box>
        <Box 
          p={4} 
          borderRadius="lg" 
          border="1px solid var(--chakra-colors-chakra-border-color)"
          backgroundColor="var(--chakra-colors-chakra-bg)"
        >
          <Text fontWeight="bold" mb={2} color="var(--chakra-colors-chakra-text-color)">D+2 예수금</Text>
          <Text fontSize="xl" color="var(--chakra-colors-chakra-text-color)">{balanceInfo.output2?.[0]?.prvs_rcdl_excc_amt?.toLocaleString() || '0'}원</Text>
        </Box>
        <Box 
          p={4} 
          borderRadius="lg" 
          border="1px solid var(--chakra-colors-chakra-border-color)"
          backgroundColor="var(--chakra-colors-chakra-bg)"
        >
          <Text fontWeight="bold" mb={2} color="var(--chakra-colors-chakra-text-color)">총평가금액</Text>
          <Text fontSize="xl" color="var(--chakra-colors-chakra-text-color)">{balanceInfo.output2?.[0]?.tot_evlu_amt?.toLocaleString() || '0'}원</Text>
        </Box>
        <Box 
          p={4} 
          borderRadius="lg" 
          border="1px solid var(--chakra-colors-chakra-border-color)"
          backgroundColor="var(--chakra-colors-chakra-bg)"
        >
          <Text fontWeight="bold" mb={2} color="var(--chakra-colors-chakra-text-color)">매입금액</Text>
          <Text fontSize="xl" color="var(--chakra-colors-chakra-text-color)">{balanceInfo.output2?.[0]?.pchs_amt_smtl_amt?.toLocaleString() || '0'}원</Text>
        </Box>
        <Box 
          p={4} 
          borderRadius="lg" 
          border="1px solid var(--chakra-colors-chakra-border-color)"
          backgroundColor="var(--chakra-colors-chakra-bg)"
        >
          <Text fontWeight="bold" mb={2} color="var(--chakra-colors-chakra-text-color)">평가손익</Text>
          <Text fontSize="xl" color="var(--chakra-colors-chakra-text-color)">{balanceInfo.output2?.[0]?.evlu_pfls_smtl_amt?.toLocaleString() || '0'}원</Text>
        </Box>
        <Box 
          p={4} 
          borderRadius="lg" 
          border="1px solid var(--chakra-colors-chakra-border-color)"
          backgroundColor="var(--chakra-colors-chakra-bg)"
        >
          <Text fontWeight="bold" mb={2} color="var(--chakra-colors-chakra-text-color)">총수익률</Text>
          <Text fontSize="xl" color="var(--chakra-colors-chakra-text-color)">
            {(() => {
              const pchsAmt = balanceInfo.output2?.[0]?.pchs_amt_smtl_amt || 0;
              const evluPflsAmt = balanceInfo.output2?.[0]?.evlu_pfls_smtl_amt || 0;
              if (pchsAmt === 0) return '0.00';
              return ((evluPflsAmt / pchsAmt) * 100).toFixed(2);
            })()}%
          </Text>
        </Box>
      </Box>
    </Box>
  )
} 