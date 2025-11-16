import { Box, Heading, HStack, Button, VStack, Text } from '@chakra-ui/react'
import { useState } from 'react'
import ScoreModal from './ScoreModal'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

function dashboard() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedScore, setSelectedScore] = useState(0)
  const [selectedReasons, setSelectedReasons] = useState('')

  // Example data - backend will provide this
  const pieChartData = [
    { label: '15%', percentage: 15 },
    { label: '24%', percentage: 24 },
    { label: '12%', percentage: 12 },
    { label: '8%', percentage: 8 },
    { label: '18%', percentage: 18 },
    { label: '10%', percentage: 10 },
    { label: '8%', percentage: 8 },
    { label: '5%', percentage: 5 }
  ]

  const lineGraphData = [
    { month: 0, spending: 500, budget: 600 },
    { month: 1, spending: 750, budget: 600 },
    { month: 2, spending: 600, budget: 600 },
    { month: 3, spending: 550, budget: 600 },
    { month: 4, spending: 700, budget: 600 },
    { month: 5, spending: 250, budget: 600 },
    { month: 6, spending: 800, budget: 600 },
    { month: 7, spending: 600, budget: 600 },
    { month: 8, spending: 700, budget: 600 },
    { month: 9, spending: 650, budget: 600 }
  ]

  const transactions = [
    { id: 1, company: 'Company', date: 'Date', item: 'Item', amount: 'Amount', etc: 'etc' },
    { id: 2, company: 'Company', date: 'Date', item: 'Item', amount: 'Amount', etc: 'etc' },
    { id: 3, company: 'Company', date: 'Date', item: 'Item', amount: 'Amount', etc: 'etc' }
  ]

  const handleTransactionClick = (transactionId: number) => {
    // Backend will fetch actual data based on transactionId
    // For now using example data
    setSelectedScore(87)
    setSelectedReasons('Sample reasons for the score.')
    setIsModalOpen(true)
  }

  return (
    <Box minH="100vh" w="100vw" bg="white">
      {/* Top Navigation Bar */}
      <HStack
        bg="white"
        px={8}
        py={4}
        justifyContent="space-between"
        borderBottom="2px solid"
        borderColor="blue.600"
      >
        <Button
          size="lg"
          bg="blue.600"
          color="white"
          _hover={{ bg: "blue.700" }}
        >
          Purchase Analyzer
        </Button>
        <Button
          size="lg"
          bg="blue.600"
          color="white"
          _hover={{ bg: "blue.700" }}
        >
          Sign Out
        </Button>
      </HStack>

      {/* Charts Section */}
      <HStack gap={0} h="500px" borderBottom="2px solid" borderColor="gray.300">
        {/* Pie Chart */}
        <Box
          flex={1}
          p={8}
          borderRight="2px solid"
          borderColor="gray.300"
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          <Box position="relative" w="350px" h="350px">
            {/* Pie Chart Circle with segments */}
            <svg width="350" height="350" viewBox="0 0 350 350">
              <circle cx="175" cy="175" r="175" fill="#1e3a8a" />
              {/* White lines to create segments */}
              {pieChartData.map((_, index) => {
                const angle = (index / pieChartData.length) * 360
                const x2 = 175 + Math.cos((angle - 90) * Math.PI / 180) * 175
                const y2 = 175 + Math.sin((angle - 90) * Math.PI / 180) * 175
                return (
                  <line
                    key={index}
                    x1="175"
                    y1="175"
                    x2={x2}
                    y2={y2}
                    stroke="white"
                    strokeWidth="2"
                  />
                )
              })}
            </svg>

            {/* Percentage Labels - positioned around circle */}
            {pieChartData.map((item, index) => {
              const angle = (index / pieChartData.length) * 360
              const radius = 200
              const x = Math.cos((angle - 90) * Math.PI / 180) * radius
              const y = Math.sin((angle - 90) * Math.PI / 180) * radius

              return (
                <Text
                  key={index}
                  position="absolute"
                  left="50%"
                  top="50%"
                  transform={`translate(calc(-50% + ${x}px), calc(-50% + ${y}px))`}
                  fontSize="lg"
                  fontWeight="bold"
                  color="black"
                >
                  {item.label}
                </Text>
              )
            })}
          </Box>
        </Box>

        {/* Line Graph */}
        <Box
          flex={1}
          p={8}
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={lineGraphData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis domain={[0, 1000]} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="spending" stroke="#14b8a6" strokeWidth={2} />
              <Line type="monotone" dataKey="budget" stroke="#6366f1" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </Box>
      
      </HStack>
        {/* Recent Transactions Table */}
        <VStack align="stretch" p={0} gap={0}>
          <Box bg="teal.300" w="fit-content" py={3} px={6}>
            <Heading
              size="lg"
              color="black"
              fontWeight="bold"
            >
              Recent Transactions
            </Heading>
          </Box>

          <Box>
            {/* Header Row */}
            <HStack
              gap={0}
              bg="cyan.200"
              borderBottom="1px solid"
              borderColor="gray.400"
            >
              <Box flex={1} p={4} borderRight="1px solid" borderColor="gray.400">
                <Text fontSize="xl" fontWeight="bold" color="black">Company</Text>
              </Box>
              <Box flex={1} p={4} borderRight="1px solid" borderColor="gray.400">
                <Text fontSize="xl" fontWeight="bold" color="black">Date</Text>
              </Box>
              <Box flex={1} p={4} borderRight="1px solid" borderColor="gray.400">
                <Text fontSize="xl" fontWeight="bold" color="black">Item</Text>
              </Box>
              <Box flex={1} p={4} borderRight="1px solid" borderColor="gray.400">
                <Text fontSize="xl" fontWeight="bold" color="black">Amount</Text>
              </Box>
              <Box flex={1} p={4}>
                <Text fontSize="xl" fontWeight="bold" color="black">etc</Text>
              </Box>
            </HStack>

            {/* Transaction Rows */}
            {transactions.map((transaction) => (
              <HStack
                key={transaction.id}
                gap={0}
                borderBottom="1px solid"
                borderColor="gray.400"
                cursor="pointer"
                _hover={{ bg: "gray.100" }}
                onClick={() => handleTransactionClick(transaction.id)}
              >
                <Box flex={1} p={4} borderRight="1px solid" borderColor="gray.400">
                  <Text fontSize="lg" color="black">{transaction.company}</Text>
                </Box>
                <Box flex={1} p={4} borderRight="1px solid" borderColor="gray.400">
                  <Text fontSize="lg" color="black">{transaction.date}</Text>
                </Box>
                <Box flex={1} p={4} borderRight="1px solid" borderColor="gray.400">
                  <Text fontSize="lg" color="black">{transaction.item}</Text>
                </Box>
                <Box flex={1} p={4} borderRight="1px solid" borderColor="gray.400">
                  <Text fontSize="lg" color="black">{transaction.amount}</Text>
                </Box>
                <Box flex={1} p={4}>
                  <Text fontSize="lg" color="black">{transaction.etc}</Text>
                </Box>
                </HStack>
            ))}
          </Box>
        </VStack>
      <ScoreModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} score={selectedScore} reasons={selectedReasons} />
    </Box>
  )
}

export default dashboard