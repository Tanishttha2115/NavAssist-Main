import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyC1aROlKaBhzeWh64RW_3MeMnbmklV0gs8",
  authDomain: "automatic-a6f5b.firebaseapp.com",
  projectId: "automatic-a6f5b",
  storageBucket: "automatic-a6f5b.firebasestorage.app",
  messagingSenderId: "804139461601",
  appId: "1:804139461601:web:62970f992874271cf080a0",
  measurementId: "G-EWH14CL265",
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export default app;
