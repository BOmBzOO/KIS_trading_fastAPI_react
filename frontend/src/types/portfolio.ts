export interface PortfolioItem {
  name: string
  tags: string[]
  returnRate: string
  status?: string
  accountId: string
  accessTokenExpired: boolean
  tokenExpiryTime?: string
  totalAssets?: string
  availableCash?: string
  depositBalance?: string
  d2DepositBalance?: string
  evaluationAmount?: string
  purchaseAmount?: string
  evaluationProfitLoss?: string
  profitLossRate?: string
  holdings?: {
    name: string
    code: string
    returnRate: string
    trend: "up" | "down"
  }[]
} 