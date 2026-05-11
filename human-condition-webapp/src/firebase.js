import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";

// Import the functions you need from the SDKs you need
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyBdjxKbRu9-2Sd2oz0O8-TuE17idk2jE7Q",
  authDomain: "anonymous-brainwriting-hci.firebaseapp.com",
  projectId: "anonymous-brainwriting-hci",
  storageBucket: "anonymous-brainwriting-hci.firebasestorage.app",
  messagingSenderId: "779644274332",
  appId: "1:779644274332:web:357ebc5315142ac0da4f59",
  measurementId: "G-EJXHJ7XXZ4"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

export const db = getFirestore(app);