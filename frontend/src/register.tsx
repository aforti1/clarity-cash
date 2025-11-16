import { Box, Button, Heading, Input, VStack, Text } from '@chakra-ui/react'
import { initializeApp } from 'firebase/app'
import { getAuth, signInWithEmailAndPassword } from 'firebase/auth'
import { useFirebaseAuth } from './context/FirebaseProvider'
import { useNavigate } from 'react-router-dom'
import './App.css'

function App() {

  // Instantiate Firebase Auth (safe public keys)
  const firebaseConfig = {
  apiKey: "AIzaSyBI_GOh1r_NMjZS36VBH1ZJ_lDLwD8oNVY",
  authDomain: "claritycashaf.firebaseapp.com",
  projectId: "claritycashaf",
  storageBucket: "claritycashaf.firebasestorage.app",
  messagingSenderId: "1035015535362",
  appId: "1:1035015535362:web:9ab598b6be2fd19ba6601b",
  measurementId: "G-SVJMXW01DF"
  };

  // Initialize Firebase
  const app = initializeApp(firebaseConfig);

  // Initialize Firebase Auth
  const auth = getAuth(app);

  const navigate = useNavigate();

  const onLogin = async () => {
    const emailInput = document.querySelector('input[placeholder="Username:"]') as HTMLInputElement | null;
    const passwordInput = document.querySelector('input[type="password"]') as HTMLInputElement | null;
    const email = emailInput?.value ?? '';
    const password = passwordInput?.value ?? '';

    try {
      await signInWithEmailAndPassword(auth, email, password);
      // On success, save the uid to context and redirect to dashboard
      useFirebaseAuth().uid = auth.currentUser?.uid ?? null;
      
      navigate('/dashboard');
      
    } catch (error) {
      // Login failed - display model asking to redirect to registration page
      console.error(error);
      const goToRegister = window.confirm('Incorrect username or password. Would you like to register?');
      if (goToRegister) {
        navigate('/register');
      }
    }
  }

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
            _placeholder={{ color: "gray.700" }}
          />
          
          <Input
            type="password"
            placeholder="Password:"
            size="lg"
            bg="gray.200"
            border="none"
            _placeholder={{ color: "gray.700" }}
          />
          
          <Button
            bg="gray.300"
            size="lg"
            w="auto"
            px={12}
            mt={2}
            _hover={{ bg: "gray.400" }}
            onClick={onLogin}
          >
            Login
          </Button>
        </VStack>
      </VStack>
    </Box>
  )
}

export default App