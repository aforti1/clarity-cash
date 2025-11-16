import { Box, Button, Heading, Input, VStack, HStack, Text } from '@chakra-ui/react'
import { useState } from 'react'

function PurchaseAnalyzer() {
  const [cost, setCost] = useState('')
  const [currency, setCurrency] = useState('$')
  const [context, setContext] = useState('')
  const [score, setScore] = useState<number | null>(null)
  const [recommendation, setRecommendation] = useState<string>('')

  return (
    <Box minH="100vh" w="100vw" bg="white">
      {/* Header with blue bar */}
      <Box bg="blue.600" py={2} px={8}>
        <Text color="white" fontSize="lg" fontWeight="semibold">
          Purchase Analyzer
        </Text>
      </Box>

      {/* Main Header */}
      <HStack justifyContent="space-between" px={8} py={6} borderBottom="1px solid" borderColor="gray.200">
        <HStack gap={4}>
          <Button
            variant="ghost"
            size="lg"
            onClick={() => window.history.back()}
          >
            ← Dashboard
          </Button>
        </HStack>
        <Button variant="ghost" size="lg">
          Sign Out
        </Button>
      </HStack>

      {/* Main Content */}
      <HStack gap={8} alignItems="flex-start" w="full" p={8}>
        {/* Left Column */}
        <VStack gap={6} flex={1} alignItems="stretch">
          {/* Cost Input with Currency */}
          <HStack>
            <Text fontSize="3xl" fontWeight="bold" color="black">Cost:</Text>
            <select
              value={currency}
              onChange={(e) => setCurrency(e.target.value)}
              style={{
                fontSize: '24px',
                padding: '8px 12px',
                backgroundColor: '#E5E7EB',
                color: 'black',
                border: 'none',
                borderRadius: '4px'
              }}>
              <option>$</option>
              <option>€</option>
              <option>£</option>
              <option>¥</option>
            </select>
            <Input
              size="lg"
              bg="gray.200"
              border="0"
              _focus={{ boxShadow: "none" }}
              w="200px"
              type="text"
              placeholder="0.00"
              value={cost}
              onInput={(e) => {
                let value = e.currentTarget.value.replace(/[^0-9.]/g, '');
                const parts = value.split('.');
                if (parts.length > 2) {
                  value = parts[0] + '.' + parts.slice(1).join('');
                }
                if (parts[1]?.length > 2) {
                  value = parts[0] + '.' + parts[1].slice(0, 2);
                }
                e.currentTarget.value = value;
                setCost(value);
              }}
            />
          </HStack>

          {/* Context Box */}
          <VStack alignItems="flex-start" gap={2}>
            <Heading size="md" color="black">Context of Purchase</Heading>
            <textarea
              placeholder="Enter context about your purchase..."
              value={context}
              onChange={(e) => setContext(e.target.value)}
              style={{
                width: '100%',
                minHeight: '250px',
                backgroundColor: '#E5E7EB',
                padding: '24px',
                borderRadius: '6px',
                border: 'none',
                fontSize: '16px',
                fontFamily: 'inherit',
                resize: 'vertical',
                color: 'black'
              }}
            />
            <Button
              bg="blue.500"
              color="white"
              size="lg"
              w="full"
              disabled={!cost || !context}
              _hover={{ bg: "blue.600" }}
              _disabled={{ bg: "gray.400", cursor: "not-allowed" }}
            >
              Analyze Purchase
            </Button>
          </VStack>
        </VStack>

        {/* Right Column */}
        <VStack gap={6} flex={1} alignItems="stretch">
          {/* Score Box */}
          <Box
            border="2px solid"
            borderColor="gray.300"
            p={8}
            textAlign="center"
            borderRadius="md"
            minH="200px"
            display="flex"
            alignItems="center"
            justifyContent="center"
          >
            {score !== null ? (
              <Text fontSize="9xl" fontWeight="bold" color={score >= 70 ? "green.500" : score >= 40 ? "yellow.500" : "red.500"}>
                {score}
              </Text>
            ) : (
              <Text fontSize="xl" color="gray.400">
                Score will appear here
              </Text>
            )}
          </Box>

          {/* Good/Bad Box */}
          <Box
            bg="gray.200"
            p={12}
            textAlign="center"
            borderRadius="md"
            minH="200px"
            display="flex"
            alignItems="center"
            justifyContent="center"
          >
            {recommendation ? (
              <Text fontSize="7xl" fontWeight="bold" color="green.500">
                {recommendation}
              </Text>
            ) : (
              <Text fontSize="xl" color="gray.400">
                Reasoning will appear here.
              </Text>
            )}
          </Box>
        </VStack>
      </HStack >
    </Box >
  )
}

export default PurchaseAnalyzer