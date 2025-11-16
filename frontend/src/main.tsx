import { StrictMode } from 'react'
import { Provider } from './components/ui/provider'
import { BrowserRouter } from 'react-router-dom'
import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import { FirebaseProvider } from './context/FirebaseProvider.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <FirebaseProvider>
        <Provider>
          <App />
        </Provider>
      </FirebaseProvider>
    </BrowserRouter>
  </StrictMode>
)