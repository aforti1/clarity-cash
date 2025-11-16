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

function Dashboard() {
  const uid = useFirebaseAuth().uid ?? ''

  const [summary, setSummary] = useState<PaycheckSummary | null>(null)
  const [meanScores, setMeanScores] = useState<number[]>([])
  const [transactions, setTransactions] = useState<any[]>([])

  const [loadingSummary, setLoadingSummary] = useState(true)
  const [loadingScores, setLoadingScores] = useState(true)
  const [loadingTransactions, setLoadingTransactions] = useState(true)

  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedScore, setSelectedScore] = useState(0)
  const [selectedReasons, setSelectedReasons] = useState('')
  const [selectedDescription, setSelectedDescription] = useState('')

  useEffect(() => {
    if (!uid) return;

    let mounted = true;

    // ---- FETCH PAYCHECK SUMMARY ----
    const loadSummary = async () => {
      try {
        const r = await fetch(`/api/plaid/paycheck-spending/${uid}`)
        if (!r.ok) throw new Error("Summary error")
        const d = await r.json()
        if (mounted) setSummary(d)
      } catch (err) {
        console.error(err)
      } finally {
        if (mounted) setLoadingSummary(false)
      }
    }

    // ---- FETCH MEAN SCORES ----
    const loadScores = async () => {
      try {
        const r = await fetch(`/api/plaid/mean-spending-scores-month/${uid}`)
        if (!r.ok) throw new Error("Scores error")
        const d = await r.json()

        if (mounted) setMeanScores(d.mean_scores ?? [])
      } catch (err) {
        console.error(err)
      } finally {
        if (mounted) setLoadingScores(false)
      }
    }

    // ---- FETCH TRANSACTIONS ----
    const loadTransactions = async () => {
      try {
        const r = await fetch(`/api/plaid/transactions/${uid}`)
        if (!r.ok) throw new Error("Transaction fetch error")
        const d = await r.json()

        // IMPORTANT FIX
        const arr = Array.isArray(d.transactions) ? d.transactions : []
        if (mounted) setTransactions(arr)
      } catch (err) {
        console.error(err)
      } finally {
        if (mounted) setLoadingTransactions(false)
      }
    }

    loadSummary()
    loadScores()
    loadTransactions()

    return () => { mounted = false }
  }, [uid])

  // -------- Prepare Chart Data --------
  const paycheckAmount = summary?.last_paycheck_amount ?? 0
  const spent = summary?.spent_since_paycheck ?? 0

  const lineGraphData = meanScores.map((s, i) => ({
    week: `Week ${i + 1}`,
    score: s
  }))

  const yAxisMax = meanScores.length > 0
    ? Math.ceil(Math.max(...meanScores) / 10) * 10 + 10
    : 100

  const handleTransactionClick = (_id: string) => {
    setSelectedScore(87)
    setSelectedReasons("Sample reasons")
    setSelectedDescription("Sample description")
    setIsModalOpen(true)
  }

  return (
    <Box minH="100vh" w="100vw" bg="gray.950" overflow="hidden">

      {/* NAV */}
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
          baseColor='#111827'
          pillColor='#2563eb'
          hoveredPillTextColor='#f3f4f6'
          pillTextColor='#ffffff'
        />
      </Box>

      {/* CHART GRID */}
      <Box
        display="grid"
        gridTemplateColumns={{ base: '1fr', lg: '1fr 1fr' }}
        gap={0}
        borderBottom="1px solid"
        borderColor="gray.800"
      >
        {/* PIE CHART */}
        <Box
          bg="gray.900"
          minH="500px"
          display="flex"
          alignItems="center"
          justifyContent="center"
          borderRight={{ base: 'none', lg: '1px solid' }}
          borderColor="gray.800"
        >
          {loadingSummary ? (
            <VStack>
              <Spinner size="xl" />
              <Text color="gray.400">Loading paycheck data...</Text>
            </VStack>
          ) : (
            <PaycheckDonut
              donutData={{
                last_paycheck_date: summary?.last_paycheck_date ?? "Unknown",
                amount: paycheckAmount,
                spent: spent,
                width: 400,
                height: 400
              }}
            />
          )}
        </Box>

        {/* LINE CHART */}
        <Box
          bg="gray.900"
          minH="500px"
          display="flex"
          alignItems="center"
          justifyContent="center"
          p={8}
        >
          {loadingScores ? (
            <VStack>
              <Spinner size="xl" />
              <Text color="gray.400">Loading score trends...</Text>
            </VStack>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={lineGraphData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="week" stroke="#9ca3af" />
                <YAxis domain={[0, yAxisMax]} stroke="#9ca3af" />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="score" stroke="#14b8a6" strokeWidth={3} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </Box>
      </Box>

      {/* TRANSACTIONS TABLE */}
      <VStack align="stretch">
        <Box bg="blue.600" w="full" py={4} px={8}>
          <Heading size="lg" color="white">Recent Transactions</Heading>
        </Box>

        {loadingTransactions ? (
          <Box bg="gray.900" minH="400px" display="flex" justifyContent="center" alignItems="center">
            <Spinner size="xl" />
          </Box>
        ) : (
          <Box bg="gray.950" p={6}>
            <VStack gap={2} align="stretch">
                {(() => {
                const elements = [];
                for (let index = 0; index < transactions.length; index++) {
                  const tx = transactions[index];
                  elements.push(
                  <HStack
                    key={tx.transaction_id ?? index}
                    bg="gray.900"
                    border="1px solid"
                    borderColor="gray.800"
                    p={4}
                    borderRadius="md"
                    onClick={() => handleTransactionClick(tx.transaction_id)}
                    cursor="pointer"
                  >
                    <Box flex={1}><Text color="gray.100">{tx.date}</Text></Box>
                    <Box flex={2}><Text color="gray.100">{tx.merchant}</Text></Box>
                    <Box flex={2}><Text color="gray.400">{tx.category?.join(", ")}</Text></Box>
                    <Box flex={1} textAlign="right">
                    <Text color="gray.100">${Math.abs(tx.amount).toFixed(2)}</Text>
                    </Box>
                    <Box flex={1} textAlign="right">
                    <Text color="green.300">{tx.score}</Text>
                    </Box>
                  </HStack>
                  );
                }
                return elements;
                })()}
                <HStack
                  key={tx.transaction_id ?? index}
                  bg="gray.900"
                  border="1px solid"
                  borderColor="gray.800"
                  p={4}
                  borderRadius="md"
                  onClick={() => handleTransactionClick(tx.transaction_id)}
                  cursor="pointer"
                >
                  <Box flex={1}><Text color="gray.100">{tx.date}</Text></Box>
                  <Box flex={2}><Text color="gray.100">{tx.merchant}</Text></Box>
                  <Box flex={2}><Text color="gray.400">{tx.category?.join(", ")}</Text></Box>
                  <Box flex={1} textAlign="right">
                    <Text color="gray.100">${Math.abs(tx.amount).toFixed(2)}</Text>
                  </Box>
                  <Box flex={1} textAlign="right">
                    <Text color="green.300">{tx.score}</Text>
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
    </Box>
  )
}

export default Dashboard
