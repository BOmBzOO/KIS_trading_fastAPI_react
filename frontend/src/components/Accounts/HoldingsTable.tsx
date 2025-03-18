import { Box, useBreakpointValue } from "@chakra-ui/react"

interface HoldingsTableProps {
  holdings: any[]
}

export function HoldingsTable({ holdings }: HoldingsTableProps) {
  const isMobile = useBreakpointValue({ base: true, md: false });

  if (!holdings?.length) {
    return null
  }

  const truncateName = (name: string) => {
    return name.length > 9 ? name.substring(0, 9) + '...' : name;
  };

  return (
    <Box>
      <Box overflowX="auto" borderRadius="lg" border="1px solid var(--chakra-colors-chakra-border-color)">
        <table style={{ 
          width: "100%", 
          borderCollapse: "collapse",
          color: "var(--chakra-colors-chakra-text-color)"
        }}>
          <thead>
            <tr style={{ backgroundColor: "var(--chakra-colors-chakra-subtle-bg)" }}>
              <th style={{ 
                padding: "12px 16px", 
                textAlign: "left", 
                borderBottom: "1px solid var(--chakra-colors-chakra-border-color)",
                color: "var(--chakra-colors-chakra-text-color)",
                fontWeight: "bold"
              }}>종목명</th>
              {!isMobile && (
                <>
                  <th style={{ 
                    padding: "12px 16px", 
                    textAlign: "right", 
                    borderBottom: "1px solid var(--chakra-colors-chakra-border-color)",
                    color: "var(--chakra-colors-chakra-text-color)",
                    fontWeight: "bold"
                  }}>평가금액</th>
                  <th style={{ 
                    padding: "12px 16px", 
                    textAlign: "right", 
                    borderBottom: "1px solid var(--chakra-colors-chakra-border-color)",
                    color: "var(--chakra-colors-chakra-text-color)",
                    fontWeight: "bold"
                  }}>평가손익</th>
                </>
              )}
              <th style={{ 
                padding: "12px 16px", 
                textAlign: "right", 
                borderBottom: "1px solid var(--chakra-colors-chakra-border-color)",
                color: "var(--chakra-colors-chakra-text-color)",
                fontWeight: "bold"
              }}>보유수량</th>
              <th style={{ 
                padding: "12px 16px", 
                textAlign: "right", 
                borderBottom: "1px solid var(--chakra-colors-chakra-border-color)",
                color: "var(--chakra-colors-chakra-text-color)",
                fontWeight: "bold"
              }}>수익률</th>
            </tr>
          </thead>
          <tbody>
            {holdings.map((item, index) => (
              <tr key={index} style={{ 
                backgroundColor: index % 2 === 0 ? "var(--chakra-colors-chakra-subtle-bg)" : "transparent"
              }}>
                <td style={{ 
                  padding: "12px 16px", 
                  borderBottom: "1px solid var(--chakra-colors-chakra-border-color)",
                  color: "var(--chakra-colors-chakra-text-color)",
                  fontWeight: "500"
                }}>{isMobile ? truncateName(item.prdt_name) : item.prdt_name}</td>
                {!isMobile && (
                  <>
                    <td style={{ 
                      padding: "12px 16px", 
                      textAlign: "right", 
                      borderBottom: "1px solid var(--chakra-colors-chakra-border-color)",
                      color: "var(--chakra-colors-chakra-text-color)"
                    }}>{item.evlu_amt?.toLocaleString()}</td>
                    <td style={{ 
                      padding: "12px 16px", 
                      textAlign: "right", 
                      borderBottom: "1px solid var(--chakra-colors-chakra-border-color)",
                      color: "var(--chakra-colors-chakra-text-color)"
                    }}>{item.evlu_pfls_amt?.toLocaleString()}</td>
                  </>
                )}
                <td style={{ 
                  padding: "12px 16px", 
                  textAlign: "right", 
                  borderBottom: "1px solid var(--chakra-colors-chakra-border-color)",
                  color: "var(--chakra-colors-chakra-text-color)"
                }}>{item.hldg_qty?.toLocaleString()}</td>
                <td style={{ 
                  padding: "12px 16px", 
                  textAlign: "right", 
                  borderBottom: "1px solid var(--chakra-colors-chakra-border-color)",
                  color: "var(--chakra-colors-chakra-text-color)"
                }}>{item.evlu_pfls_rt ? Number(item.evlu_pfls_rt).toFixed(2) : '0.00'}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Box>
    </Box>
  )
} 