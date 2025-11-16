/* Auto-launches the Plaid Link flow when rendered */

import { useEffect } from "react";
import { usePlaidLink } from "react-plaid-link";

export function PlaidAutoLauncher({ uid, linkToken }: { uid: string, linkToken: string }) {
  const { open, ready } = usePlaidLink({
    token: linkToken,
    onSuccess: async (public_token, _metadata) => {
      // Send the public_token to the backend to save the access token in Firestore
      const res = await fetch("/api/plaid/sandbox-exchange-token", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ uid, public_token }),
      });

      if (!res.ok) {
        alert("Failed to link bank account");
        return;
      }
      alert("Bank account linked successfully!");
    },
  });

  useEffect(() => {
    if (ready) open(); // auto-open the plaid widget
  }, [ready, open]);

  return null;  // Doesn't render anything, just shows the Plaid Link UI
}
