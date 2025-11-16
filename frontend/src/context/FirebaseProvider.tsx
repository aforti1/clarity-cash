import React, { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { getAuth, onAuthStateChanged } from "firebase/auth";

type AuthContextType = {
    uid: string | null;
};

const AuthContext = createContext<AuthContextType>({ uid: null });

export const FirebaseProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [uid, setUid] = useState<string | null>(null);

    useEffect(() => {
        const auth = getAuth();
        const unsubscribe = onAuthStateChanged(auth, (user) => {
            setUid(user?.uid ?? null);
        });
        return () => unsubscribe();
    }, []);

    return <AuthContext.Provider value={{ uid }}>{children}</AuthContext.Provider>;
};

export const useFirebaseAuth = () => useContext(AuthContext);