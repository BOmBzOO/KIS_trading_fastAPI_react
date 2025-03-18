import { Flex, Image, useBreakpointValue, IconButton } from "@chakra-ui/react"
import { Link } from "@tanstack/react-router"
import { useTheme } from "next-themes"

import Logo from "/assets/images/fastapi-logo.svg"
import UserMenu from "./UserMenu"

function Navbar() {
  const display = useBreakpointValue({ base: "none", md: "flex" })
  const { theme, setTheme } = useTheme()

  const toggleTheme = () => {
    setTheme(theme === "light" ? "dark" : "light")
  }

  return (
    <Flex
      display={display}
      justify="space-between"
      position="sticky"
      color="white"
      align="center"
      bg="bg.muted"
      w="100%"
      top={0}
      p={4}
    >
      <Link to="/">
        <Image src={Logo} alt="Logo" maxW="3xs" p={2} />
      </Link>
      <Flex gap={2} alignItems="center">
        <IconButton
          aria-label={theme === "light" ? "다크 모드로 변경" : "라이트 모드로 변경"}
          onClick={toggleTheme}
          variant="ghost"
          colorScheme="whiteAlpha"
          size="sm"
          fontSize="lg"
          _hover={{ bg: "whiteAlpha.200" }}
        >
          {theme === "light" ? "🌙" : "☀️"}
        </IconButton>
        <UserMenu />
      </Flex>
    </Flex>
  )
}

export default Navbar
