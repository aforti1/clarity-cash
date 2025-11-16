import React from "react";
import { PlaidLink, usePlaidLink } from "react-plaid-link";
import { usePlaidToken } from "../context/PlaidTokenProvider";

export const PlaidButton: React.FC = () => {
  const linkToken = usePlaidToken();

  // normalize the context value to a string token (handles cases where the context returns an object)
  const tokenString =
    typeof linkToken === "string"
      ? linkToken
      : linkToken && typeof linkToken === "object" && "token" in linkToken
      ? (linkToken as any).token
      : "";

  const onSuccess = async (public_token: string, _metadata: any) => {
    // send public_token to your backend
    const res = await fetch("http://localhost:8000/plaid/sandbox-exchange-token/" + public_token);
    const data = await res.json();

    // data.access_token is what your backend gets from Plaid
    // store it in Firestore under this user’s UID, etc.
    console.log("Access token response", data);
  };

  if (!tokenString) return <button disabled>Loading Plaid...</button>;

  return (
    <PlaidLink
      token={tokenString}
      onSuccess={onSuccess}
      onExit={(err, metadata) => {
        console.log("Link exit", err, metadata);
      }}
    >
      Connect your bank
    </PlaidLink>
  );
};
