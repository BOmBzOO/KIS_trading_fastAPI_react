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
  IconButton,
  Spinner
} from '@chakra-ui/react';
import { FiRefreshCw } from 'react-icons/fi';

// 가상 데이터 생성 함수
const generateMockData = (days: number) => {
  const data = [];
  let value = 0;
  
  for (let i = 0; i < days; i++) {
    const date = new Date();
    date.setDate(date.getDate() - (days - i - 1));
    
    value += (Math.random() - 0.5) * 2; // -1 ~ 1 사이의 변동
    
    data.push({
      date: date.toLocaleDateString(),
      value: parseFloat(value.toFixed(2))
    });
  }
  
  return data;
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
      // 실제 API 연동 시 여기서 데이터를 가져옵니다
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
  }, []);

  const getData = () => chartData[period];
  
  return (
    <Box h="400px" w="100%" p={4}>
      <Flex mb={4} justify="space-between" align="center">
        <Box display="flex">
          <Button
            borderRadius="md"
            borderRightRadius={0}
            onClick={() => setPeriod('daily')}
            colorScheme={period === 'daily' ? 'blue' : 'gray'}
            size="sm"
          >
            일별
          </Button>
          <Button
            borderRadius={0}
            borderLeftWidth={0}
            borderRightWidth={0}
            onClick={() => setPeriod('weekly')}
            colorScheme={period === 'weekly' ? 'blue' : 'gray'}
            size="sm"
          >
            주별
          </Button>
          <Button
            borderRadius="md"
            borderLeftRadius={0}
            onClick={() => setPeriod('monthly')}
            colorScheme={period === 'monthly' ? 'blue' : 'gray'}
            size="sm"
          >
            월별
          </Button>
        </Box>
        <Button
          onClick={refreshData}
          size="sm"
          disabled={isLoading}
          variant="ghost"
        >
          {isLoading ? <Spinner size="sm" /> : '새로고침'}
        </Button>
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