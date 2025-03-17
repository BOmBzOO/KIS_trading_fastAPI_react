import React, { useState, useCallback, useEffect } from 'react';
import {
  Box,
  Button,
  Text,
  Flex,
  Spinner
} from '@chakra-ui/react';
import { FaSync } from 'react-icons/fa';
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

export const PerformanceChart: React.FC<PerformanceChartProps> = ({ accountId }) => {
  const [isLoading, setIsLoading] = useState(false);
  
  const { data: balanceHistory, refetch } = useQuery({
    queryKey: ['balanceHistory', accountId],
    queryFn: async () => {
      const now = new Date();
      const kstOffset = 9 * 60;
      const today = new Date(now.getTime() + kstOffset * 60000);
      today.setHours(0, 0, 0, 0);
      const utcToday = new Date(today.getTime() - kstOffset * 60000);

      const response = await AccountsService.inquireBalanceFromDb({ 
        account_id: accountId,
        start_time: utcToday.toISOString(),
        end_time: new Date().toISOString()
      });
      return response;
    },
    refetchInterval: 60 * 1000
  });

  const refreshData = useCallback(async () => {
    setIsLoading(true);
    try {
      await refetch();
    } catch (error: unknown) {
      console.error('데이터 새로고침 중 오류 발생:', error);
    } finally {
      setIsLoading(false);
    }
  }, [refetch]);

  const chartData = React.useMemo(() => {
    if (!balanceHistory) return { labels: [], datasets: [] };

    const sortedData = [...balanceHistory].sort((a, b) => 
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );

    if (sortedData.length === 0) return { labels: [], datasets: [] };

    const initialEvaluationAmount = sortedData[0].evaluation_amount || 0;
    const kstOffset = 9 * 60;

    const times: string[] = [];
    const values: number[] = [];

    sortedData.forEach((item) => {
      const currentEvaluationAmount = item.evaluation_amount || 0;
      const dailyReturnRate = initialEvaluationAmount === 0 
        ? 0 
        : ((currentEvaluationAmount - initialEvaluationAmount) / initialEvaluationAmount) * 100;

      const utcDate = new Date(item.timestamp);
      const kstDate = new Date(utcDate.getTime() + kstOffset * 60000);
      
      times.push(kstDate.toLocaleTimeString('ko-KR', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      }));
      values.push(Number(dailyReturnRate.toFixed(2)));
    });

    return {
      labels: times,
      datasets: [
        {
          label: '당일 수익률',
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
  }, [balanceHistory]);

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
          label: (context) => {
            const value = context.parsed.y;
            return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
          },
        },
        backgroundColor: 'white',
        titleColor: '#718096',
        bodyColor: value => value.parsed.y >= 0 ? '#E53E3E' : '#3182CE',
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
          color: '#E2E8F0',
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
          color: '#E2E8F0',
        },
        ticks: {
          color: '#718096',
          font: {
            size: 12,
          },
          callback: value => `${value}%`,
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
    <Box h="400px" w="100%" p={1}>
      <Flex mb={4} justify="space-between" align="center">
        <Button
          onClick={refreshData}
          size="sm"
          loading={isLoading}
          colorScheme="gray"
          variant="ghost"
        >
          <Flex align="center" gap={2}>
            <FaSync />
            <Text>새로고침</Text>
          </Flex>
        </Button>
      </Flex>
      
      {isLoading ? (
        <Flex justify="center" align="center" h="300px">
          <Spinner />
        </Flex>
      ) : (
        <Box h="300px">
          <Line data={chartData} options={options} />
        </Box>
      )}
    </Box>
  );
}; 