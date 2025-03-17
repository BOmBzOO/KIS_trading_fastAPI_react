import React, { useState, useCallback, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
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

interface PerformanceChartProps {
  accountId: string;
}

// 커스텀 툴팁 컴포넌트
const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const value = payload[0].value as number;
    return (
      <Box
        bg="white"
        p={3}
        borderRadius="md"
        boxShadow="lg"
        border="1px solid"
        borderColor="gray.200"
        _dark={{
          bg: "gray.800",
          borderColor: "gray.600"
        }}
      >
        <Text fontSize="sm" color="gray.500" mb={1}>
          {label}
        </Text>
        <Text 
          fontSize="md" 
          fontWeight="bold"
          color={value >= 0 ? "red.500" : "blue.500"}
        >
          {value >= 0 ? '+' : ''}{value.toFixed(2)}%
        </Text>
      </Box>
    );
  }
  return null;
};

export const PerformanceChart: React.FC<PerformanceChartProps> = ({ accountId }) => {
  const [isLoading, setIsLoading] = useState(false);
  
  const { data: balanceHistory, refetch } = useQuery({
    queryKey: ['balanceHistory', accountId],
    queryFn: async () => {
      // 한국 시간 기준 오늘 날짜 설정
      const now = new Date();
      const kstOffset = 9 * 60; // 한국 시간 오프셋 (9시간)
      const today = new Date(now.getTime() + kstOffset * 60000);
      today.setHours(0, 0, 0, 0);
      const utcToday = new Date(today.getTime() - kstOffset * 60000); // UTC 기준 오늘 시작 시간

      const response = await AccountsService.inquireBalanceFromDb({ 
        account_id: accountId,
        start_time: utcToday.toISOString(),
        end_time: new Date().toISOString()
      });
      return response;
    },
    refetchInterval: 60 * 1000 // 1분마다 자동 새로고침
  });

  useEffect(() => {
    if (!balanceHistory) {
      console.error('잔고 이력 조회 실패');
    } else {
      console.log('잔고 이력 데이터:', balanceHistory);
    }
  }, [balanceHistory]);

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
    if (!balanceHistory) return [];

    // 시간순으로 정렬
    const sortedData = [...balanceHistory].sort((a, b) => 
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );

    // 한국 시간 기준 오늘 날짜 설정
    const now = new Date();
    const kstOffset = 9 * 60; // 한국 시간 오프셋 (9시간)
    const today = new Date(now.getTime() + kstOffset * 60000);
    today.setHours(0, 0, 0, 0);
    const utcToday = new Date(today.getTime() - kstOffset * 60000); // UTC 기준 오늘 시작 시간

    // 오늘 날짜의 데이터만 필터링 (UTC 기준)
    const todayData = sortedData.filter(item => {
      const itemDate = new Date(item.timestamp);
      return itemDate >= utcToday;
    });

    if (todayData.length === 0) return [];

    // 시작 시점의 평가금액을 기준으로 설정
    const initialEvaluationAmount = todayData[0].evaluation_amount || 0;
    
    return todayData.map((item) => {
      const currentEvaluationAmount = item.evaluation_amount || 0;
      
      // 금일 수익률 계산 (시작 시점 대비 변화율)
      const dailyReturnRate = initialEvaluationAmount === 0 
        ? 0 
        : ((currentEvaluationAmount - initialEvaluationAmount) / initialEvaluationAmount) * 100;

      // UTC 시간을 KST로 변환하여 표시
      const utcDate = new Date(item.timestamp);
      const kstDate = new Date(utcDate.getTime() + kstOffset * 60000);

      return {
        date: kstDate.toLocaleTimeString('ko-KR', {
          hour: '2-digit',
          minute: '2-digit',
          hour12: false
        }),
        value: Number(dailyReturnRate.toFixed(2))
      };
    });
  }, [balanceHistory]);

  const gridColor = '#E2E8F0';
  const textColor = '#718096';
  const lineColor = '#4299E1';

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
        <ResponsiveContainer width="100%" height={300}>
          <LineChart 
            data={chartData}
            margin={{ top: 5, right: 5, left: 0, bottom: 40 }}
          >
            <CartesianGrid 
              strokeDasharray="3 3" 
              stroke={gridColor}
            />
            <XAxis 
              dataKey="date" 
              tick={{ fontSize: 12, fill: textColor }}
              tickLine={{ stroke: gridColor }}
              axisLine={{ stroke: gridColor }}
              angle={-45} // 기울기를 없애고 정렬
              textAnchor="end" // 중앙 정렬
              height={5} // 라벨 높이 조정
            />
            <YAxis
              tick={{ fontSize: 12, fill: textColor }}
              tickLine={{ stroke: gridColor }}
              axisLine={{ stroke: gridColor }}
              tickFormatter={(value) => `${value}%`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Line
              type="monotone"
              dataKey="value"
              stroke={lineColor}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 5, fill: lineColor }}
              name="수익률 (%)"
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </Box>
  );
}; 