import React from "react"
import { Container, Heading } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"

import AccountList from "@/components/Accounts/AccountList"
import AddAccount from "@/components/Accounts/AddAccount"

export const Route = createFileRoute("/_layout/accounts")({
  component: AccountRoutes,
})

function AccountRoutes(): React.ReactElement {
  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} py={12}>
        계좌 관리
      </Heading>
      <AddAccount />
      <AccountList />
    </Container>
  )
}

export const NewAccountRoute = createFileRoute("/_layout/accounts")({
  component: NewAccount,
})

function NewAccount(): React.ReactElement {
  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} py={12}>
        새 계좌 추가
      </Heading>
      <AddAccount />
    </Container>
  )
}
