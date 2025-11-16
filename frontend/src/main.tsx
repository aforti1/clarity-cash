import { StrictMode } from 'react'
import { Provider } from './components/ui/provider'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import Dashboard from './dashboard.tsx'
import PurchaseAnalyzer from './PurchaseAnalyzer.tsx'
import './index.css'
import { FirebaseProvider } from './context/FirebaseProvider.tsx'
import { createSystem, defaultConfig } from '@chakra-ui/react'

// Configure Chakra UI v3 system with uniform dark mode colors
const system = createSystem(defaultConfig, {
  theme: {
    tokens: {
      colors: {
        bg: {
          canvas: { value: '{colors.gray.950}' },  // Deepest gray
          subtle: { value: '{colors.gray.900}' },  // Cards and surfaces
          muted: { value: '{colors.gray.800}' },  // Hover states
        },
        border: {
          DEFAULT: { value: '{colors.gray.800}' },
        },
      },
    },
  },
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <FirebaseProvider>
        <Provider value={system} defaultTheme="dark" forcedTheme="dark">
          <Routes>
            <Route path="/" element={<App />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/analyze" element={<PurchaseAnalyzer />} />
          </Routes>
        </Provider>
      </FirebaseProvider>
    </BrowserRouter>
  </StrictMode>
)