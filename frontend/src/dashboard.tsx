import { Box, Heading, HStack, VStack, Text, Spinner } from '@chakra-ui/react'
import { useState, useEffect } from 'react'
import { useFirebaseAuth } from './context/FirebaseProvider'
import ScoreModal from './ScoreModal'
import PaycheckDonut from './components/PaycheckDonut'
import PillNav from './components/PillNav'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import ClarityCashy from './assets/Clarity-Cashy.png'

type PaycheckSummary = {
  last_paycheck_amount: number;
  last_paycheck_date: string;
  spent_since_paycheck: number;
}

function dashboard() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedScore, setSelectedScore] = useState(0)
  const [selectedReasons, setSelectedReasons] = useState('')
  const [selectedDescription, setSelectedDescription] = useState('')

  // Loading states
  const [loadingSummary, setLoadingSummary] = useState(true)
  const [loadingScores, setLoadingScores] = useState(true)
  const [loadingTransactions, setLoadingTransactions] = useState(true)

  // Get data for the pie chart from backend (last paycheck amount spent)
  const uid = useFirebaseAuth().uid ?? ''
  const [summary, setSummary] = useState<PaycheckSummary | null>(null);
  const [meanScores, setMeanScores] = useState<number[]>([]);
  const [transactions, setTransactions] = useState<any[]>([]);

  useEffect(() => {
    let isMounted = true
    
    // Fetch paycheck summary data
    const fetchPieChartData = async () => {
      setLoadingSummary(true)
      try {
        const response = await fetch(`/api/plaid/paycheck-spending/${uid}`)
        if (!response.ok) throw new Error('Failed to fetch pie chart data')
        const data = await response.json()
        if (isMounted) {
          setSummary(data)
          setLoadingSummary(false)
        }
      } catch (error) {
        console.error(error)
        if (isMounted) setLoadingSummary(false)
      }
    }

    // Fetch weekly mean scores data
    const fetchMeanScores = async () => {
      setLoadingScores(true)
      try {
        const response = await fetch(`/api/plaid/mean-spending-scores-month/${uid}`)
        if (!response.ok) throw new Error('Failed to fetch weekly mean scores')
        const data = await response.json()
        if (isMounted) {
          setMeanScores(data.mean_scores)
          setLoadingScores(false)
        }
      } catch (error) {
        console.error(error)
        if (isMounted) setLoadingScores(false)
      }
    }

    // Get transaction history for table
    const fetchTransactionHistory = async () => {
      setLoadingTransactions(true)
      try {
        const response = await fetch(`/api/plaid/transactions/${uid}`)
        if (!response.ok) throw new Error('Failed to fetch transaction history')
        const data = await response.json()
        if (isMounted) {
          setTransactions(data)
          setLoadingTransactions(false)
        }
      } catch (error) {
        console.error(error)
        if (isMounted) setLoadingTransactions(false)
      }
    }

    if (uid) {
      fetchPieChartData()
      fetchMeanScores()
      fetchTransactionHistory()
    }

    return () => {
      isMounted = false
    }
  }, [uid])

  // Paycheck summary data preparation
  const paycheckAmount = summary?.last_paycheck_amount ?? 0;
  const spent = summary?.spent_since_paycheck ?? 0;

  // Line graph data preparation
  const lineGraphData = meanScores.map((score, index) => ({
    week: `Week ${index + 1}`,
    score: score,
  }))

  // Calculate Y-axis domain dynamically based on actual data
  const maxScore = meanScores.length > 0 ? Math.max(...meanScores) : 100;
  const yAxisMax = Math.ceil(maxScore / 10) * 10 + 10;

  const handleTransactionClick = (_transaction_id: string) => {
    // Fetch transaction details based on transaction_id
    setSelectedScore(87)
    setSelectedDescription('Sample description for the score.')
    setSelectedReasons('Sample reasons for the score.')
    setIsModalOpen(true)
  }

  return (
    <Box minH="100vh" w="100vw" bg="gray.950" overflow="hidden">
      {/* Pill Navigation - Centered */}
      <Box 
        bg="gray.900" 
        borderBottom="1px solid" 
        borderColor="gray.800"
        display="flex"
        justifyContent="center"
        py={4}
      >
        <PillNav
          logo={ClarityCashy}
          logoAlt='ClarityCashy'
          items={[
            { label: 'Dashboard', href: '/dashboard' },
            { label: 'Purchase Analyzer', href: '/analyze' },
            { label: 'Sign Out', href: '/' },
          ]} 
          activeHref='/dashboard'
          className='custom-nav'
          baseColor='#111827'
          pillColor='#2563eb'
          hoveredPillTextColor='#f3f4f6'
          pillTextColor='#ffffff'
        />
      </Box>

      {/* Charts Section - Responsive Grid */}
      <Box 
        display="grid" 
        gridTemplateColumns={{ base: '1fr', lg: '1fr 1fr' }}
        gap={0}
        borderBottom="1px solid" 
        borderColor="gray.800"
      >
        {/* Pie Chart */}
        <Box
          bg="gray.900"
          borderRight={{ base: 'none', lg: '1px solid' }}
          borderColor="gray.800"
          display="flex"
          alignItems="center"
          justifyContent="center"
          minH="500px"
          p={8}
        >
          {loadingSummary ? (
            <VStack gap={4}>
              <Spinner size="xl" color="blue.500" borderWidth="4px" />
              <Text color="gray.400" fontSize="lg">Loading paycheck data...</Text>
            </VStack>
          ) : (
            <PaycheckDonut 
              donutData={summary ? {
                last_paycheck_date: summary.last_paycheck_date,
                amount: paycheckAmount,
                spent: spent,
                width: 400,
                height: 400
              } : undefined} 
            />
          )}
        </Box>

        {/* Line Graph */}
        <Box
          bg="gray.900"
          display="flex"
          alignItems="center"
          justifyContent="center"
          minH="500px"
          p={8}
        >
          {loadingScores ? (
            <VStack gap={4}>
              <Spinner size="xl" color="blue.500" borderWidth="4px" />
              <Text color="gray.400" fontSize="lg">Loading score trends...</Text>
            </VStack>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={lineGraphData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis 
                  dataKey="week" 
                  stroke="#9ca3af"
                  style={{ fontSize: '14px' }}
                />
                <YAxis 
                  domain={[0, yAxisMax]} 
                  stroke="#9ca3af"
                  style={{ fontSize: '14px' }}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1f2937', 
                    border: '1px solid #374151',
                    borderRadius: '6px',
                    color: '#f3f4f6'
                  }}
                />
                <Legend 
                  wrapperStyle={{ color: '#f3f4f6' }}
                />
                <Line 
                  type="monotone" 
                  dataKey="score" 
                  name="Weekly Average Score"
                  stroke="#14b8a6" 
                  strokeWidth={3}
                  dot={{ fill: '#14b8a6', r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </Box>
      </Box>

      {/* Recent Transactions Table */}
      <VStack align="stretch" p={0} gap={0}>
        <Box bg="blue.600" w="full" py={4} px={8}>
          <Heading
            size="lg"
            color="white"
            fontWeight="bold"
          >
            Recent Transactions
          </Heading>
        </Box>

        {loadingTransactions ? (
          <Box bg="gray.900" minH="400px" display="flex" alignItems="center" justifyContent="center">
            <VStack gap={4}>
              <Spinner size="xl" color="blue.500" borderWidth="4px" />
              <Text color="gray.400" fontSize="lg">Loading transactions...</Text>
            </VStack>
          </Box>
        ) : (
          <Box bg="gray.950" p={6}>
            {/* Table Header */}
            <HStack
              gap={0}
              bg="gray.800"
              borderRadius="md"
              borderWidth="1px"
              borderColor="gray.700"
              mb={2}
              p={4}
            >
              <Box flex={1}>
                <Text fontSize="sm" fontWeight="bold" color="gray.300">DATE</Text>
              </Box>
              <Box flex={2}>
                <Text fontSize="sm" fontWeight="bold" color="gray.300">MERCHANT</Text>
              </Box>
              <Box flex={2}>
                <Text fontSize="sm" fontWeight="bold" color="gray.300">CATEGORY</Text>
              </Box>
              <Box flex={1} textAlign="right">
                <Text fontSize="sm" fontWeight="bold" color="gray.300">AMOUNT</Text>
              </Box>
              <Box flex={1} textAlign="right">
                <Text fontSize="sm" fontWeight="bold" color="gray.300">SCORE</Text>
              </Box>
            </HStack>

            {/* Animated Transaction Rows */}
            <VStack gap={2} align="stretch">
              {transactions.map((transaction, index) => (
                <HStack
                  key={transaction.transaction_id}
                  gap={0}
                  bg="gray.900"
                  borderRadius="md"
                  borderWidth="1px"
                  borderColor="gray.800"
                  p={4}
                  cursor="pointer"
                  transition="all 0.2s"
                  _hover={{ 
                    bg: "gray.800", 
                    borderColor: "blue.500",
                    transform: "translateX(4px)"
                  }}
                  onClick={() => handleTransactionClick(transaction.transaction_id)}
                  style={{
                    animation: `slideIn 0.3s ease-out ${index * 0.05}s both`
                  }}
                >
                  <Box flex={1}>
                    <Text fontSize="md" color="gray.100">{transaction.date}</Text>
                  </Box>
                  <Box flex={2}>
                    <Text fontSize="md" fontWeight="semibold" color="gray.100">
                      {transaction.merchant}
                    </Text>
                  </Box>
                  <Box flex={2}>
                    <Text fontSize="sm" color="gray.400">
                      {Array.isArray(transaction.category) 
                        ? transaction.category.join(', ') 
                        : transaction.category}
                    </Text>
                  </Box>
                  <Box flex={1} textAlign="right">
                    <Text fontSize="md" fontWeight="bold" color="gray.100">
                      ${Math.abs(transaction.amount).toFixed(2)}
                    </Text>
                  </Box>
                  <Box flex={1} textAlign="right">
                    <Text 
                      fontSize="md" 
                      fontWeight="bold"
                      color={
                        transaction.score >= 70 ? "green.400" : 
                        transaction.score >= 40 ? "yellow.400" : 
                        "red.400"
                      }
                    >
                      {transaction.score ?? 'N/A'}
                    </Text>
                  </Box>
                </HStack>
              ))}
            </VStack>
          </Box>
        )}
      </VStack>

      <ScoreModal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
        score={selectedScore} 
        reasons={selectedReasons} 
        description={selectedDescription} 
      />

      {/* Add CSS animation */}
      <style>{`
        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateX(-20px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
      `}</style>
    </Box>
  )
}

export default dashboard