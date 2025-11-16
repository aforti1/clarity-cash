/* Login/Plaid Connection Page */

import { Box, Button, Heading, Input, VStack, Text } from '@chakra-ui/react'
import { initializeApp } from 'firebase/app'
import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword } from 'firebase/auth'
import { useFirebaseAuth } from './context/FirebaseProvider'
import { useNavigate } from 'react-router-dom'
import { PlaidAutoLauncher } from './components/PlaidAutoLauncher'
import { useState } from 'react'
import LiquidEther from './components/LiquidEther'
import TextType from './components/TextType'
import { Subtitle } from './components/Subtitle'
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

  // State to hold Plaid link token for registration
  const [linkToken, setLinkToken] = useState<string | null>(null);
  var user = auth.currentUser?.uid ?? '';

  const onLogin = async () => {
    const emailInput = document.querySelector('input[placeholder="Email:"]') as HTMLInputElement | null;
    const passwordInput = document.querySelector('input[type="password"]') as HTMLInputElement | null;
    const email = emailInput?.value ?? '';
    const password = passwordInput?.value ?? '';

    try {
      await signInWithEmailAndPassword(auth, email, password);
      // On success, redirect to dashboard
      navigate('/dashboard');
      
    } catch (error) {
      // Login failed - display model asking to redirect to registration page
      console.error(error);
      const goToRegister = window.confirm('Incorrect Email or password. Would you like to register?');
      if (goToRegister) {
        // Request a link token from the backend
        try {
          const resp = await fetch('/api/plaid/link-token', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
          });

          if (!resp.ok) throw new Error(`Link token request failed: ${resp.status}`);

          // Get the link token from the response
          const data = await resp.json();
          const linkToken = data.link_token ?? data.linkToken;

          if (!linkToken) throw new Error('No link token returned from server');

          // Attempt to add as a new firebase user
          try{
            const userCredential = await createUserWithEmailAndPassword(auth, email, password);
            user = userCredential.user?.uid ?? '';
            console.log('Firebase user registered with UID:', user);
          } catch (regError) {
            console.error('Firebase registration failed:', regError);
          }

          // Display the plaid login button on a modal
          setLinkToken(linkToken);

        } catch (err) {
          console.error('Failed to fetch link token', err);
          alert('Unable to start registration. Please try again later.');
        }
      }
    }
  }

  return (
    <Box position="relative" minH="100vh" w="100vw" bg="gray.950" display="flex" alignItems="center" justifyContent="center">
      {/* Background */}
      <Box position="absolute" inset="0" zIndex={0}>
        <LiquidEther
          colors={['#5227FF', '#FF9FFC', '#B19EEF']}
          mouseForce={20}
          cursorSize={100}
          isViscous={false}
          viscous={30}
          iterationsViscous={32}
          iterationsPoisson={32}
          resolution={0.5}
          isBounce={false}
          autoDemo={true}
          autoSpeed={0.5}
          autoIntensity={2.2}
          takeoverDuration={0.1}
          autoResumeDelay={3000}
          autoRampDuration={0.4}
        />
      </Box>

      {/* Content */}
      <VStack gap={12} w="full" maxW="1200px" p={8} position="relative" zIndex={1} alignItems="center">
        <Box textAlign="center">
          <TextType text={["Welcome to ClarityCash!"]} typingSpeed={50} pauseDuration={10000} showCursor={true} cursorCharacter="|" className="text-8xl mb-8" />
        </Box>

        <Subtitle />

        <VStack gap={6} w="full" maxW="850px" mt={8} alignItems="stretch">
          <Input
            placeholder="Email:"  // Large area for expansion - include different kinds of login methods
            size="lg"
            h="64px"
            fontSize="xl"
            px={6}
            bg="gray.900"
            borderColor="gray.800"
            borderWidth="1px"
            color="gray.100"
            _placeholder={{ color: "gray.500", fontSize: "xl" }}
            _hover={{ borderColor: "gray.700" }}
            _focus={{ borderColor: "blue.500", boxShadow: "0 0 0 2px var(--chakra-colors-blue-500)" }}
          />

          <Input
            type="password"
            placeholder="Password:"
            size="lg"
            h="64px"
            fontSize="xl"
            px={6}
            bg="gray.900"
            borderColor="gray.800"
            borderWidth="1px"
            color="gray.100"
            _placeholder={{ color: "gray.500", fontSize: "xl" }}
            _hover={{ borderColor: "gray.700" }}
            _focus={{ borderColor: "blue.500", boxShadow: "0 0 0 2px var(--chakra-colors-blue-500)" }}
          />

          <Button
            bg="blue.600"
            color="white"
            size="lg"
            w="auto"
            px={20}
            py={6}
            mt={4}
            fontSize="2xl"
            borderRadius="md"
            _hover={{ bg: "blue.700" }}
            _active={{ bg: "blue.800" }}
            onClick={onLogin}
          >
            Login
          </Button>

          {linkToken && <PlaidAutoLauncher uid={user} linkToken={linkToken} />}
        </VStack>
      </VStack>
    </Box>
  )
}

export default App