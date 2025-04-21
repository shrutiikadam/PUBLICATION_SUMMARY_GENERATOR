// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyDfnKgKseLomnmxqINmxkjET1CKexLd-EY",
  authDomain: "publication-summary-136b8.firebaseapp.com",
  projectId: "publication-summary-136b8",
  storageBucket: "publication-summary-136b8.firebasestorage.app",
  messagingSenderId: "1084087577958",
  appId: "1:1084087577958:web:e00a69cf3a455c9c982ca7",
  measurementId: "G-FJGJ3ZPPNR"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);