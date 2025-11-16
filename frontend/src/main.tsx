import { StrictMode } from 'react'
import { Provider } from './components/ui/provider'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import Dashboard from './dashboard.tsx'
import PurchaseAnalyzer from './PurchaseAnalyzer.tsx'
import './index.css'
import { FirebaseProvider } from './context/FirebaseProvider.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <FirebaseProvider>
        <Provider>
          <Routes>
            <Route path="/" element={<App />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/analyze" element={<PurchaseAnalyzer />} />
          </Routes>
          <App />
        </Provider>
      </FirebaseProvider>
    </BrowserRouter>
  </StrictMode>
)