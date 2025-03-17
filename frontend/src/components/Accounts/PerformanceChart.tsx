import React, { useState, useCallback } from 'react';
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
  ButtonGroup
} from '@chakra-ui/react';
import { FaSync } from 'react-icons/fa';

// 가상 데이터 생성 함수
const generateMockData = (days: number) => {
  const data = [];
  let value = 0;
  
  for (let i = 0; i < days; i++) {
    const date = new Date();
    date.setDate(date.getDate() - (days - i - 1));
    
    value += (Math.random() - 0.5) * 2; // -1 ~ 1 사이의 변동
    
    data.push({
      date: formatDate(date, days),
      value: parseFloat(value.toFixed(2))
    });
  }
  
  return data;
};

// 날짜 포맷 함수
const formatDate = (date: Date, totalDays: number) => {
  if (totalDays <= 7) {
    // 일별: "12/31" 형식
    return `${date.getMonth() + 1}/${date.getDate()}`;
  } else if (totalDays <= 31) {
    // 주별: "12월 4주" 형식
    const week = Math.ceil(date.getDate() / 7);
    return `${date.getMonth() + 1}월 ${week}주`;
  } else {
    // 월별: "2023/12" 형식
    return `${date.getFullYear()}/${date.getMonth() + 1}`;
  }
};

type Period = 'daily' | 'weekly' | 'monthly';

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
  const [period, setPeriod] = useState<Period>('daily');
  const [isLoading, setIsLoading] = useState(false);
  const [chartData, setChartData] = useState(() => ({
    daily: generateMockData(7),
    weekly: generateMockData(12),
    monthly: generateMockData(12)
  }));
  
  const gridColor = '#E2E8F0';
  const textColor = '#718096';
  const lineColor = '#4299E1';

  const refreshData = useCallback(async () => {
    setIsLoading(true);
    try {
      // 실제 API 연동 시 accountId를 사용하여 해당 계좌의 데이터를 가져옵니다
      console.log(`Fetching data for account: ${accountId}`);
      const newData = {
        daily: generateMockData(7),
        weekly: generateMockData(12),
        monthly: generateMockData(12)
      };
      setChartData(newData);
    } catch (error) {
      console.error('Failed to refresh data:', error);
    } finally {
      setIsLoading(false);
    }
  }, [accountId]);

  const getData = () => chartData[period];
  
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
        
        <ButtonGroup size="sm" variant="solid" attached>
          <Button
            onClick={() => setPeriod('daily')}
            colorScheme={period === 'daily' ? 'blue' : 'gray'}
          >
            일별
          </Button>
          <Button
            onClick={() => setPeriod('weekly')}
            colorScheme={period === 'weekly' ? 'blue' : 'gray'}
          >
            주별
          </Button>
          <Button
            onClick={() => setPeriod('monthly')}
            colorScheme={period === 'monthly' ? 'blue' : 'gray'}
          >
            월별
          </Button>
        </ButtonGroup>
      </Flex>
      
      <ResponsiveContainer width="100%" height={300}>
        <LineChart 
          data={getData()}
          margin={{ top: 5, right: 5, left: 0, bottom: 5 }}
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
            interval="preserveStartEnd"
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
            dot={{ r: 3, fill: lineColor }}
            activeDot={{ r: 5, fill: lineColor }}
            name="수익률 (%)"
          />
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
}; 