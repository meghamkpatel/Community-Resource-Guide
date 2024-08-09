import React, { useState } from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import Login from './Login';
import reportWebVitals from './reportWebVitals';
import { GoogleOAuthProvider, googleLogout } from "@react-oauth/google";

// Extracted client ID from the JSON file
const clientId = '267588794958-ue8mn1p7gj03gga0srp2t50ak5eou93l.apps.googleusercontent.com';

const Root = () => {
  const [profile, setProfile] = useState(null);

  const handleLoginSuccess = (profileData) => {
    setProfile(profileData);
  };

  const handleLogout = () => {
    googleLogout();
    setProfile(null);
  };

  return (
    <GoogleOAuthProvider clientId={clientId}>
      <React.StrictMode>
        {profile ? (
          <App profile={profile} onLogout={handleLogout} />
        ) : (
          <Login onLoginSuccess={handleLoginSuccess} />
        )}
      </React.StrictMode>
    </GoogleOAuthProvider>
  );
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<Root />);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals.console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();

