import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import {
  onAuthStateChanged,
  signInWithPopup,
  GoogleAuthProvider,
  GithubAuthProvider,
  OAuthProvider,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut as firebaseSignOut
} from "firebase/auth";
import type { User } from 'firebase/auth';
import { auth } from "../lib/firebase";
import { localDevelopmentBypass } from '../lib/access';

interface AuthContextType {
  user: User | null;
  localBypass: boolean;
  configurationError: string | null;
  loading: boolean;
  signInWithGoogle: () => Promise<void>;
  signInWithProvider: (name: 'Google' | 'GitHub' | 'Apple' | 'Microsoft') => Promise<void>;
  signInWithEmail: (email: string, password?: string) => Promise<void>;
  signUpWithEmail: (email: string, password?: string) => Promise<void>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!auth) {
      setUser(null);
      setLoading(false);
      return () => {};
    }

    // Listen for auth changes
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      if (currentUser) {
        // Retain the actual Firebase User, including its profile and token methods.
        setUser(currentUser);
      } else {
        setUser(null);
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const signInWithGoogle = async () => {
    try {
      if (!auth) throw new Error('Firebase sign-in is not configured for this deployment.');
      const provider = new GoogleAuthProvider();
      const credential=await signInWithPopup(auth, provider);
      setUser(credential.user);
    } catch (error) {
      console.error("Error signing in with Google", error);
      throw error;
    }
  };

  const signInWithProvider = async (name: 'Google' | 'GitHub' | 'Apple' | 'Microsoft') => {
    if (!auth) throw new Error('Firebase sign-in is not configured.');
    const provider = name === 'Google' ? new GoogleAuthProvider() : name === 'GitHub' ? new GithubAuthProvider() : new OAuthProvider(name === 'Apple' ? 'apple.com' : 'microsoft.com');
    if (name === 'Apple') { provider.addScope('email'); provider.addScope('name'); }
    const credential = await signInWithPopup(auth, provider);
    setUser(credential.user);
  };

  const signInWithEmail = async (email: string, password?: string) => {
    try {
      if (!auth) throw new Error('Firebase sign-in is not configured for this deployment.');
      if (!password) throw new Error("Password is required for email login");
      const credential=await signInWithEmailAndPassword(auth, email, password);
      setUser(credential.user);
    } catch (error) {
      console.error("Error signing in with email", error);
      throw error;
    }
  };

  const signUpWithEmail = async (email: string, password?: string) => {
    try {
      if (!auth) throw new Error('Firebase sign-in is not configured for this deployment.');
      if (!password) throw new Error("Password is required for email signup");
      const credential=await createUserWithEmailAndPassword(auth, email, password);
      setUser(credential.user);
    } catch (error) {
      console.error("Error signing up with email", error);
      throw error;
    }
  };

  const signOut = async () => {
    try {
      if (!auth) return;
      await firebaseSignOut(auth);
      setUser(null);
    } catch (error) {
      console.error("Error signing out", error);
      throw error;
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, localBypass:localDevelopmentBypass,
      configurationError: !auth && !localDevelopmentBypass ? 'Firebase authentication is not configured for this deployment.' : null,
      signInWithGoogle, signInWithProvider, signInWithEmail, signUpWithEmail, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

