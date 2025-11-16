import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

type PlaidTokenContextValue = {
    linkToken: string | null;
    setToken: (token: string | null) => void;
    clearToken: () => void;
    isLoaded: boolean;
};

const STORAGE_KEY = "plaid_token";

const PlaidTokenContext = createContext<PlaidTokenContextValue | undefined>(undefined);

type Props = {
    children: React.ReactNode;
};

export function PlaidTokenProvider({ children }: Props) {
    const [linkToken, setTokenState] = useState<string | null>(null);
    const [isLoaded, setIsLoaded] = useState(false);

    // initialize from localStorage
    useEffect(() => {
        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            setTokenState(raw ?? null);
        } catch {
            setTokenState(null);
        } finally {
            setIsLoaded(true);
        }
    }, []);

    const setToken = useCallback((next: string | null) => {
        try {
            if (next === null) {
                localStorage.removeItem(STORAGE_KEY);
            } else {
                localStorage.setItem(STORAGE_KEY, next);
            }
        } catch {
            // ignore storage errors
        }
        setTokenState(next);
    }, []);

    const clearToken = useCallback(() => setToken(null), [setToken]);

    const value = useMemo(
        () => ({ linkToken, setToken, clearToken, isLoaded }),
        [linkToken, setToken, clearToken, isLoaded]
    );

    return <PlaidTokenContext.Provider value={value}>{children}</PlaidTokenContext.Provider>;
}

export function usePlaidToken() {
    const ctx = useContext(PlaidTokenContext);
    if (!ctx) {
        throw new Error("usePlaidToken must be used within a PlaidTokenProvider");
    }
    return ctx;
}