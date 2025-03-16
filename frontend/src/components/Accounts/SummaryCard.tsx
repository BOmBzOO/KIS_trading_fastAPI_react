import React from "react"
import { Box, Text, Flex, Icon } from "@chakra-ui/react"

interface SummaryCardProps {
  title: string
  value: string
  subtitle?: string
  icon?: React.ElementType
}

export const SummaryCard = ({ title, value, subtitle, icon }: SummaryCardProps) => (
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