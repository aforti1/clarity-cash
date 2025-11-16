/* Auto-launches the Plaid Link flow when rendered */

import { useEffect } from "react";
import { usePlaidLink } from "react-plaid-link";

export function PlaidAutoLauncher({ linkToken }: { linkToken: string }) {
  const { open, ready } = usePlaidLink({
    token: linkToken,
    onSuccess: async (public_token, _metadata) => {
      // send to backend
      await fetch("/plaid/sandbox-exchange-token", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ public_token }),
      });

      alert("Bank linked!");
    },
  });

  useEffect(() => {
    if (ready) open(); // auto-open the plaid widget
  }, [ready, open]);

  return null; // doesn't render ANYTHING
}
