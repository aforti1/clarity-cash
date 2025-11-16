/* Display the pie chart showcasing week's spending */

import { Box, Spinner, Text, VStack } from "@chakra-ui/react"
import { PieChart, Pie, Cell, Label, ResponsiveContainer } from "recharts"

const SLICE_COLORS = ['#F56565', '#48BB78']; // red for spent, green for remaining

interface PaycheckDonutProps {
  donutData?: {
    last_paycheck_date: string
    amount: number
    spent: number
    width: number
    height: number
  }
}

function PaycheckDonut({ donutData }: PaycheckDonutProps) {
  
  if (!donutData) return <Spinner size="md"/>;

  const { last_paycheck_date, amount, spent } = donutData;
  const percentSpent = (spent / amount) * 100;
  const remaining = amount - spent;

  const chartData = [
    { name: 'Spent', value: spent },
    { name: 'Remaining', value: remaining }
  ];

  return (
    <Box>
      <VStack gap={2}>
        <Text fontWeight="semibold" fontSize="md" color="gray.100">
          Last paycheck on {last_paycheck_date}
        </Text>
        <Text fontSize="sm" color="gray.400">
          ${spent.toFixed(2)} of ${amount.toFixed(2)} spent (
          {percentSpent.toFixed(0)}%)
        </Text>

        <ResponsiveContainer width={donutData.width} height={donutData.height}>
          <PieChart>
            <Pie
              data={chartData}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              innerRadius={70}
              outerRadius={100}
              paddingAngle={2}
              cornerRadius={6}
            >
              {chartData.map((entry, index) => (
                <Cell
                  key={entry.name}
                  fill={SLICE_COLORS[index]}
                />
              ))}

              {/* Center text (percentage spent) */}
              <Label
                position="center"
                content={() => (
                  <text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle">
                    <tspan x="50%" dy="-0.5em" fontSize="24" fontWeight="bold" fill="#f3f4f6">
                      {percentSpent.toFixed(0)}%
                    </tspan>
                    <tspan x="50%" dy="1.5em" fontSize="12" fill="#9ca3af">
                      of paycheck spent
                    </tspan>
                  </text>
                )}
              />
            </Pie>
          </PieChart>
        </ResponsiveContainer>
      </VStack>
    </Box>
  );
}

export default PaycheckDonut;