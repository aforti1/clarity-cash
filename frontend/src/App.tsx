import { Box, Button, Heading, Input, VStack, Text } from '@chakra-ui/react'
import './App.css'

function App() {
  return (
    <Box minH="100vh" w="100vw"bg="white" display="flex" alignItems="center" justifyContent="center">
      <VStack gap={8} w="full" maxW="400px" p={4}>
        <Heading size="2xl" color="gray.700" textAlign="center">
          ClarityCash
        </Heading>
        
        <Text color="gray.600" textAlign="center" fontSize="md">
          Smarter spending decisions powered by real-time purchase analysis.
        </Text>
        
        <VStack gap={4} w="full" maxW="350px" mt={6} alignItems="stretch">
          <Input
            placeholder="Username:"
            size="lg"
            bg="gray.200"
            border="none"
            color="black"
            _placeholder={{ color: "gray.700" }}
          />
          
          <Input
            type="password"
            placeholder="Password:"
            size="lg"
            bg="gray.200"
            border="none"
            color ="black"
            _placeholder={{ color: "gray.700" }}
          />
          
          <Button
            bg="gray.300"
            size="lg"
            w="auto"
            px={12}
            mt={2}
            _hover={{ bg: "gray.400" }}
          >
            Login
          </Button>
        </VStack>
      </VStack>
    </Box>
  )
}

export default App