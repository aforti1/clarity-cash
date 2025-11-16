import { Box, Button, Heading, Input, VStack, HStack, Text } from '@chakra-ui/react'
import { useState } from 'react'
import PillNav from './components/PillNav'
import ClarityCashy from './assets/Clarity-Cashy.png'

function PurchaseAnalyzer() {
  const [cost, setCost] = useState('')
  const [currency, setCurrency] = useState('$')
  const [context, setContext] = useState('')
  const [score, setScore] = useState<number | null>(null)
  const [recommendation, setRecommendation] = useState<string>('')

  return (
    <Box minH="100vh" w="100vw" bg="gray.950">
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
          activeHref='/analyze'
          className='custom-nav'
          baseColor='#111827'
          pillColor='#2563eb'
          hoveredPillTextColor='#f3f4f6'
          pillTextColor='#ffffff'
        />
      </Box>

      {/* Main Content */}
      <HStack gap={8} alignItems="flex-start" w="full" p={8}>
        {/* Left Column */}
        <VStack gap={6} flex={1} alignItems="stretch">
          {/* Cost Input with Currency */}
          <HStack>
            <Text fontSize="3xl" fontWeight="bold" color="gray.100">Cost:</Text>
            <select
              value={currency}
              onChange={(e) => setCurrency(e.target.value)}
              style={{
                fontSize: '24px',
                padding: '8px 12px',
                backgroundColor: '#1f2937',
                color: '#f3f4f6',
                border: '1px solid #374151',
                borderRadius: '4px'
              }}>
              <option>$</option>
              <option>€</option>
              <option>£</option>
              <option>¥</option>
            </select>
            <Input
              size="lg"
              bg="gray.900"
              borderColor="gray.800"
              borderWidth="1px"
              color="gray.100"
              _focus={{ borderColor: "blue.500", boxShadow: "0 0 0 1px var(--chakra-colors-blue-500)" }}
              _hover={{ borderColor: "gray.700" }}
              w="200px"
              type="text"
              placeholder="0.00"
              _placeholder={{ color: "gray.500" }}
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
            <Heading size="md" color="gray.100">Context of Purchase</Heading>
            <textarea
              placeholder="Enter context about your purchase..."
              value={context}
              onChange={(e) => setContext(e.target.value)}
              style={{
                width: '100%',
                minHeight: '250px',
                backgroundColor: '#1f2937',
                padding: '24px',
                borderRadius: '6px',
                border: '1px solid #374151',
                fontSize: '16px',
                fontFamily: 'inherit',
                resize: 'vertical',
                color: '#f3f4f6'
              }}
            />
            <Button
              bg="blue.600"
              color="white"
              size="lg"
              w="full"
              disabled={!cost || !context}
              _hover={{ bg: "blue.700" }}
              _active={{ bg: "blue.800" }}
              _disabled={{ bg: "gray.700", cursor: "not-allowed" }}
            >
              Analyze Purchase
            </Button>
          </VStack>
        </VStack>

        {/* Right Column */}
        <VStack gap={6} flex={1} alignItems="stretch">
          {/* Score Box */}
          <Box
            border="1px solid"
            borderColor="gray.800"
            bg="gray.900"
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
              <Text fontSize="xl" color="gray.500">
                Score will appear here
              </Text>
            )}
          </Box>

          {/* Good/Bad Box */}
          <Box
            bg="gray.900"
            border="1px solid"
            borderColor="gray.800"
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
              <Text fontSize="xl" color="gray.500">
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