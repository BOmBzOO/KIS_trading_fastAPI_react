import React, { useState } from 'react';
import {
  Box,
  Button,
  Flex,
  Spinner,
  ButtonGroup,
  useBreakpointValue
} from '@chakra-ui/react';
import { useQuery } from '@tanstack/react-query';
import { AccountsService } from '@/client/sdk.gen';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface PerformanceChartProps {
  accountId: string;
}

type Period = 'minutely' | 'daily' | 'weekly' | 'monthly' | 'yearly';

export const PerformanceChart: React.FC<PerformanceChartProps> = ({ accountId }) => {
  const [isLoading] = useState(false);
  const [selectedPeriod, setSelectedPeriod] = useState<Period>('minutely');
  const isMobile = useBreakpointValue({ base: true, md: false });
  
  const { data: balanceHistory } = useQuery({
    queryKey: ['balanceHistory', accountId, selectedPeriod],
    queryFn: async () => {
      const now = new Date();
      let startTime = new Date(now);
      
      // 기간별 시작 시간 설정
      switch (selectedPeriod) {
        case 'minutely':
          startTime.setDate(now.getDate() - 1);
          startTime.setHours(8, 0, 0, 0);
          if (now.getHours() < 8) {
            startTime.setDate(startTime.getDate() - 1);
          }
          break;
        case 'daily':
          startTime.setDate(now.getDate() - 7);
          startTime.setHours(8, 0, 0, 0);
          break;
        case 'weekly':
          startTime.setDate(now.getDate() - 30);
          startTime.setHours(8, 0, 0, 0);
          break;
        case 'monthly':
          startTime.setMonth(now.getMonth() - 6);
          startTime.setHours(8, 0, 0, 0);
          break;
        case 'yearly':
          startTime.setFullYear(now.getFullYear() - 1);
          startTime.setHours(8, 0, 0, 0);
          break;
      }

      const response = await AccountsService.inquireBalanceFromDb({ 
        account_id: accountId,
        start_time: startTime.toISOString(),
        end_time: now.toISOString()
      });
      return response;
    },
    refetchInterval: 60 * 1000
  });

  const getPeriodLabel = (period: Period) => {
    switch (period) {
      case 'minutely':
        return '당일';
      case 'daily':
        return '일별';
      case 'weekly':
        return '주별';
      case 'monthly':
        return '월별';
      case 'yearly':
        return '년별';
      default:
        return '';
    }
  };

  const chartData = React.useMemo(() => {
    if (!balanceHistory) return { labels: [], datasets: [] };

    let sortedData = [...balanceHistory].sort((a, b) => 
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );

    if (sortedData.length === 0 || selectedPeriod !== 'minutely') {
      const now = new Date();
      const dummyData = [];
      const baseAmount = 1000000;

      for (let i = (selectedPeriod === 'yearly' ? 11 : (selectedPeriod === 'monthly' ? 5 : (selectedPeriod === 'weekly' ? 29 : 6))); i >= 0; i--) {
        const date = new Date(now);
        if (selectedPeriod === 'yearly' || selectedPeriod === 'monthly') {
          date.setMonth(date.getMonth() - i);
        } else {
          date.setDate(date.getDate() - i);
        }

        const randomChange = (Math.random() - 0.5) * 0.1;
        const amount = baseAmount * (1 + randomChange * (i + 1));

        dummyData.push({ 
          id: `dummy-${i}`,
          account_id: accountId,
          timestamp: date.toISOString(),
          total_assets: amount,
          available_cash: amount * 0.3,
          deposit_balance: amount * 0.7,
          stock_value: 0,
          total_profit_loss: amount - baseAmount,
          daily_profit_loss: amount - baseAmount,
          daily_profit_loss_rate: randomChange * 100,
          total_profit_loss_rate: ((amount - baseAmount) / baseAmount) * 100,
          d2_deposit_balance: amount * 0.7,
          evaluation_amount: 0,
          purchase_amount: 0,
          evaluation_profit_loss: amount - baseAmount,
          profit_loss_rate: ((amount - baseAmount) / baseAmount) * 100,
          created_at: date.toISOString(),
          updated_at: date.toISOString()
        });
      }
      sortedData = dummyData;
    }

    const initialTotalAssets = sortedData[0]?.total_assets || 0;
    const times: string[] = [];
    const values: number[] = [];

    sortedData.forEach((item) => {
      const currentTotalAssets = item.total_assets || 0;
      const dailyReturnRate = initialTotalAssets === 0 
        ? 0 
        : ((currentTotalAssets - initialTotalAssets) / initialTotalAssets) * 100;

      const date = new Date(item.timestamp);
      let timeFormat: Intl.DateTimeFormatOptions;
      
      switch (selectedPeriod) {
        case 'minutely':
          timeFormat = { hour: '2-digit', minute: '2-digit', hour12: false };
          times.push(date.toLocaleTimeString('ko-KR', timeFormat));
          break;
        case 'daily':
        case 'weekly':
          timeFormat = { month: '2-digit', day: '2-digit' };
          times.push(date.toLocaleDateString('ko-KR', timeFormat));
          break;
        case 'monthly':
        case 'yearly':
          timeFormat = { month: '2-digit' };
          times.push(date.toLocaleDateString('ko-KR', timeFormat));
          break;
        default:
          timeFormat = { hour: '2-digit', minute: '2-digit', hour12: false };
          times.push(date.toLocaleTimeString('ko-KR', timeFormat));
      }

      values.push(Number(dailyReturnRate.toFixed(2)));
    });

    return {
      labels: times,
      datasets: [
        {
          label: `${getPeriodLabel(selectedPeriod)} 누적수익률`,
          data: values,
          borderColor: '#4299E1',
          backgroundColor: 'rgba(66, 153, 225, 0.1)',
          fill: true,
          tension: 0.4,
          pointRadius: 0,
          pointHoverRadius: 5,
          pointHoverBackgroundColor: '#4299E1',
          borderWidth: 2,
        },
      ],
    };
  }, [balanceHistory, selectedPeriod, accountId]);

  const options: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        callbacks: {
          label: (context: any) => {
            if (typeof context.parsed?.y === 'number') {
              const value = context.parsed.y;
              return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
            }
            return '';
          },
        },
        backgroundColor: 'white',
        titleColor: '#718096',
        bodyColor: (context: any) => {
          if (typeof context.parsed?.y === 'number') {
            return context.parsed.y >= 0 ? '#E53E3E' : '#3182CE';
          }
          return '#718096';
        },
        borderColor: '#E2E8F0',
        borderWidth: 1,
        padding: 12,
        bodyFont: {
          size: 14,
          weight: 'bold',
        },
      },
    },
    scales: {
      x: {
        grid: {
          display: false
        },
        ticks: {
          color: '#718096',
          font: {
            size: 12,
          },
          maxRotation: 45,
          minRotation: 45,
        },
      },
      y: {
        grid: {
          display: false
        },
        ticks: {
          color: '#718096',
          font: {
            size: 12,
          },
          callback: (value: string | number) => `${Number(value).toFixed(2)}%`,
        },
      },
    },
    interaction: {
      mode: 'nearest',
      axis: 'x',
      intersect: false,
    },
  };

  return (
    <Box h="400px" w="100%" p={1} overflow="hidden">
      <Flex mb={4} direction={isMobile ? "column" : "row"} gap={2} justify="flex-end" align="center">
        <ButtonGroup size="sm" attached variant="outline">
          {['minutely', 'daily', 'weekly', 'monthly', 'yearly'].map((period) => (
            <Button
              key={period}
              onClick={() => setSelectedPeriod(period as Period)}
              colorScheme={selectedPeriod === period ? 'blue' : 'gray'}
              variant={selectedPeriod === period ? 'solid' : 'outline'}
              px={isMobile ? 2 : 4}
              fontSize={isMobile ? "xs" : "sm"}
            >
              {getPeriodLabel(period as Period)}
            </Button>
          ))}
        </ButtonGroup>
      </Flex>
      
      {isLoading ? (
        <Flex justify="center" align="center" h="300px">
          <Spinner />
        </Flex>
      ) : (
        <Box h="300px" overflow="hidden">
          <Line data={chartData} options={{
            ...options,
            scales: {
              x: {
                grid: { display: false },
                ticks: {
                  color: '#718096',
                  font: { size: isMobile ? 10 : 12 },
                  maxRotation: selectedPeriod === 'monthly' || selectedPeriod === 'yearly' ? 0 : (isMobile ? 30 : 45),
                  minRotation: selectedPeriod === 'monthly' || selectedPeriod === 'yearly' ? 0 : (isMobile ? 30 : 45),
                },
              },
              y: {
                grid: { display: false },
                ticks: {
                  color: '#718096',
                  font: { size: isMobile ? 10 : 12 },
                  callback: (value: string | number) => `${Number(value).toFixed(2)}%`,
                },
              },
            },
          }} />
        </Box>
      )}
    </Box>
  );
}; 