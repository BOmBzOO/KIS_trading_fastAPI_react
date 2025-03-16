import React from "react"
import { Flex, Text } from "@chakra-ui/react"

interface StockHoldingProps {
  name: string
  code: string
  returnRate: string
  trend: "up" | "down"
}

export const StockHolding = ({ name, code, returnRate, trend }: StockHoldingProps) => (
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