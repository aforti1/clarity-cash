// src/LoginPage.tsx
import React, { useState } from 'react';
import { auth } from './firebaseConfig';
import { signInWithEmailAndPassword } from 'firebase/auth';
import { useNavigate } from 'react-router-dom';

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [error, setError] = useState<string>('');
  const navigate = useNavigate(); // To redirect after login

  // Handle email/password login
  const handleLoginWithEmail = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // Sign in with Firebase
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;

      if (user) {
        // Get the Firebase ID token
        const idToken = await user.getIdToken();
        console.log("Firebase ID Token:", idToken);

        // Now send this ID token to your backend to authenticate the user
        await loginWithBackend(idToken);

        // Redirect to dashboard after successful login
        navigate('/dashboard');
      }
    } catch (err: any) {
      setError(err.message);
    }
  };

  // Send ID token to backend for verification
  const loginWithBackend = async (idToken: string) => {
    try {
      const response = await fetch('http://your-backend-api/plaid/link-token', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${idToken}`,  // Include Firebase ID token here
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('Link Token Response:', data);
        // Handle Plaid Link token in frontend
      } else {
        throw new Error('Failed to authenticate with backend');
      }
    } catch (error) {
      console.error('Error sending ID token to backend:', error);
    }
  };

  return (
    <div className="login-page">
      <h2>Login Page</h2>
      
      <form onSubmit={handleLoginWithEmail}>
        <div>
          <label htmlFor="email">Email:</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        
        <div>
          <label htmlFor="password">Password:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        
        <button type="submit">Login</button>
      </form>

      {error && <div className="error-message">{error}</div>}
    </div>
  );
};

export default LoginPage;
