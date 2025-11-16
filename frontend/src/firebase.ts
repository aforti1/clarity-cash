/* Initialize the Firebase instance */
import { initializeApp, getApps, getApp } from "firebase/app";
import { getAuth } from "firebase/auth";

// Safe client config (public)
const firebaseConfig = {
  apiKey: "AIzaSyBI_GOh1r_NMjZS36VBH1ZJ_lDLwD8oNVY",
  authDomain: "claritycashaf.firebaseapp.com",
  projectId: "claritycashaf",
  storageBucket: "claritycashaf.firebasestorage.app",
  messagingSenderId: "1035015535362",
  appId: "1:1035015535362:web:9ab598b6be2fd19ba6601b",
  measurementId: "G-SVJMXW01DF",
};

// Ensure we only initialize once (hot reload safe)
const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();

// Export a shared Auth instance
export const auth = getAuth(app);