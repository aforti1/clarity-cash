// src/Dashboard.tsx
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
  const [linkToken, setLinkToken] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch Plaid link token from backend
    const fetchLinkToken = async () => {
      try {
        const response = await fetch('/api/plaid/link-token/your-user-id', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('firebase_id_token')}`,
          },
        });
        const data = await response.json();
        setLinkToken(data.link_token);
      } catch (error) {
        console.error('Error fetching link token:', error);
      }
    };
    fetchLinkToken();
  }, []);

  const handlePlaidLink = () => {
    if (linkToken) {
      const handler = window.Plaid.create({
        token: linkToken,
        onSuccess: function(public_token, _metadata) {
          // Handle successful link and exchange public token with backend
          console.log('Public token:', public_token);
        },
        onExit: function(err, _metadata) {
          if (err) {
            console.error('Plaid link exited with error:', err);
          }
        },
      });
      handler.open();
    }
  };

  return (
    <div>
      <h1>Dashboard</h1>
      <button onClick={handlePlaidLink}>Link Bank Account</button>
    </div>
  );
};

export default Dashboard;
