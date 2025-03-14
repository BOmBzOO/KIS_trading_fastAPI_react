import { useQuery } from "@tanstack/react-query"
import {
  Box,
  Text,
  VStack,
} from "@chakra-ui/react"

import { AccountsService, type AccountPublic } from "@/client"
import DeleteAccount from "./DeleteAccount"
import EditAccount from "./EditAccount"


const AccountList = () => {
  const { data: accounts, isLoading } = useQuery({
    queryKey: ["accounts"],
    queryFn: () => AccountsService.readAccounts(),
    retry: false,
  })

  if (isLoading) {
    return <Text>로딩 중...</Text>
  }

  if (!accounts?.data.length) {
    return <Text>등록된 계좌가 없습니다.</Text>
  }

  return (
    <VStack gap={4} align="stretch">
      <Box overflowX="auto">
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th style={{ padding: "8px", textAlign: "left", borderBottom: "1px solid #e2e8f0" }}>계좌명</th>
              <th style={{ padding: "8px", textAlign: "left", borderBottom: "1px solid #e2e8f0" }}>계좌번호</th>
              <th style={{ padding: "8px", textAlign: "left", borderBottom: "1px solid #e2e8f0" }}>소유주 ID</th>
              <th style={{ padding: "8px", textAlign: "left", borderBottom: "1px solid #e2e8f0" }}>상품코드</th>
              <th style={{ padding: "8px", textAlign: "left", borderBottom: "1px solid #e2e8f0" }}>계좌유형</th>
              <th style={{ padding: "8px", textAlign: "left", borderBottom: "1px solid #e2e8f0" }}>HTS ID</th>
              <th style={{ padding: "8px", textAlign: "left", borderBottom: "1px solid #e2e8f0" }}>상태</th>
              <th style={{ padding: "8px", textAlign: "left", borderBottom: "1px solid #e2e8f0" }}>작업</th>
            </tr>
          </thead>
          <tbody>
            {accounts.data.map((account: AccountPublic) => (
              <tr key={account.id}>
                <td style={{ padding: "8px", borderBottom: "1px solid #e2e8f0" }}>{account.acnt_name}</td>
                <td style={{ padding: "8px", borderBottom: "1px solid #e2e8f0" }}>{account.cano}</td>
                <td style={{ padding: "8px", borderBottom: "1px solid #e2e8f0" }}>{account.owner_id}</td>
                <td style={{ padding: "8px", borderBottom: "1px solid #e2e8f0" }}>{account.acnt_prdt_cd}</td>
                <td style={{ padding: "8px", borderBottom: "1px solid #e2e8f0" }}>{account.acnt_type}</td>
                <td style={{ padding: "8px", borderBottom: "1px solid #e2e8f0" }}>{account.hts_id}</td>
                <td style={{ padding: "8px", borderBottom: "1px solid #e2e8f0" }}>{account.is_active ? "활성" : "비활성"}</td>
                <td style={{ padding: "8px", borderBottom: "1px solid #e2e8f0" }}>
                  <VStack gap={2}>
                    <EditAccount account={account} />
                    <DeleteAccount id={account.id} />
                  </VStack>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Box>
    </VStack>
  )
}

export default AccountList 