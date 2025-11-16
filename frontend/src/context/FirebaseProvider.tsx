/* src/context/FirebaseProvider.tsx - Provides Firebase Auth context to the app */
import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { onAuthStateChanged } from "firebase/auth";
import { auth } from "../firebase";

type AuthContextType = {
  uid: string | null;
};

const AuthContext = createContext<AuthContextType>({ uid: null });

export const FirebaseProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [uid, setUid] = useState<string | null>(null);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUid(user?.uid ?? null);
    });
    return () => unsubscribe();
  }, []);

  return (
    <AuthContext.Provider value={{ uid }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useFirebaseAuth = () => useContext(AuthContext);
